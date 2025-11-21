from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import osmnx as ox
import networkx as nx
import folium
from datetime import datetime
from typing import List, Dict, Optional
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import math
import requests
import numpy as np
import pickle

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'aggregators',
    'user': 'postgres',
    'password': 'Darshu@2004',
    'port': 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Realistic Bangalore city speeds (based on actual traffic conditions)
INCIDENT_TYPE_MAPPING = {
    1: {'color': 'O', 'speed': 18, 'delay_factor': 1.3, 'name': 'Slow Traffic', 'icon': '⚠️'},
    3: {'color': 'DR', 'speed': 8, 'delay_factor': 2.5, 'name': 'Stationary Traffic', 'icon': '🚫'},
    4: {'color': 'RC', 'speed': 2, 'delay_factor': 10.0, 'name': 'Road Closed', 'icon': '❌'},
    6: {'color': 'R', 'speed': 12, 'delay_factor': 1.8, 'name': 'Heavy Traffic', 'icon': '🚗'},
    9: {'color': 'RC', 'speed': 5, 'delay_factor': 2.0, 'name': 'Accident', 'icon': '🚧'}
}

SPEED_RANGES = {
    'B': {'avg': 25, 'color': '#0066ff', 'name': 'Normal'},      # Normal city traffic
    'O': {'avg': 18, 'color': '#ff9900', 'name': 'Moderate'},   # Moderate congestion
    'R': {'avg': 12, 'color': '#ff0000', 'name': 'Heavy'},      # Heavy traffic
    'DR': {'avg': 8, 'color': '#8b0000', 'name': 'Severe'},     # Severe congestion
    'RC': {'avg': 2, 'color': '#660000', 'name': 'Road Closed'} # Nearly blocked
}

optimizer_cache = {}
active_sessions = {}

class RouteRequest(BaseModel):
    src_lat: float
    src_lon: float
    dst_lat: float
    dst_lon: float
    scenario: str = "personal"

class NavigationSession(BaseModel):
    user_id: Optional[str] = "guest"
    route_id: int
    selected_route: List[int]
    src_lat: float
    src_lon: float
    dst_lat: float
    dst_lon: float

# ============================================================================
# ADAPTIVE OPTIMIZER CLASSES (Embedded)
# ============================================================================

class IncidentDataFetcher:
    """Fetches real-time incident data from PostgreSQL"""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.incident_severity = INCIDENT_TYPE_MAPPING
    
    def fetch_incidents(self, bbox: tuple = None) -> List[dict]:
        """Fetch incidents with optional bounding box filter"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            if bbox:
                min_lat, min_lon, max_lat, max_lon = bbox
                query = """
                    SELECT 
                        id, ty, latitude, longitude, cs, d, sd, f, t, l
                    FROM incidents
                    WHERE latitude IS NOT NULL 
                    AND longitude IS NOT NULL
                    AND latitude BETWEEN %s AND %s
                    AND longitude BETWEEN %s AND %s
                    AND sd > NOW() - INTERVAL '24 hours'
                    ORDER BY sd DESC
                """
                cursor.execute(query, (min_lat, max_lat, min_lon, max_lon))
            else:
                query = """
                    SELECT 
                        id, ty, latitude, longitude, cs, d, sd, f, t, l
                    FROM incidents
                    WHERE latitude IS NOT NULL 
                    AND longitude IS NOT NULL
                    AND sd > NOW() - INTERVAL '24 hours'
                    ORDER BY sd DESC
                """
                cursor.execute(query)
            
            incidents = cursor.fetchall()
            cursor.close()
            conn.close()
            
            incident_list = []
            for inc in incidents:
                inc_dict = dict(inc)
                ty = int(inc_dict.get('ty', 1))
                severity = self.incident_severity.get(ty, self.incident_severity[1])
                inc_dict.update({
                    'severity': severity,
                    'lat': float(inc_dict['latitude']),
                    'lon': float(inc_dict['longitude'])
                })
                incident_list.append(inc_dict)
            
            print(f"✓ Fetched {len(incident_list)} incidents")
            return incident_list
            
        except Exception as e:
            print(f"⚠ Error fetching incidents: {e}")
            return []


class TrafficDataSimulator:
    """Integrates real incidents with time-based patterns"""
    
    def __init__(self, incident_fetcher: IncidentDataFetcher):
        self.incident_fetcher = incident_fetcher
        self.incidents = []
        self.incident_grid = {}
        
        self.hourly_congestion_factors = {
            7: 1.8, 8: 2.0, 9: 1.7,
            17: 1.9, 18: 2.1, 19: 1.8,
            10: 1.2, 11: 1.2, 12: 1.3, 13: 1.3, 14: 1.2, 15: 1.3, 16: 1.4,
            0: 0.8, 1: 0.7, 2: 0.7, 3: 0.7, 4: 0.7, 5: 0.9, 6: 1.0,
            20: 1.4, 21: 1.2, 22: 1.0, 23: 0.9
        }
        
        self.road_type_sensitivity = {
            'primary': 1.5, 'secondary': 1.3, 'tertiary': 1.2,
            'residential': 1.0, 'trunk': 1.4, 'motorway': 1.1,
            'motorway_link': 1.2, 'trunk_link': 1.3,
            'primary_link': 1.4, 'secondary_link': 1.3
        }
    
    def load_incidents(self, bbox: tuple):
        self.incidents = self.incident_fetcher.fetch_incidents(bbox)
        self._build_incident_grid()
    
    def _build_incident_grid(self):
        GRID_RES = 2000
        self.incident_grid = {}
        
        for incident in self.incidents:
            lat, lon = incident['lat'], incident['lon']
            grid_x = int(lon * GRID_RES)
            grid_y = int(lat * GRID_RES)
            key = f"{grid_x},{grid_y}"
            
            if key not in self.incident_grid:
                self.incident_grid[key] = []
            self.incident_grid[key].append(incident)
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371000
        φ1, φ2 = math.radians(lat1), math.radians(lat2)
        Δφ = math.radians(lat2 - lat1)
        Δλ = math.radians(lon2 - lon1)
        
        a = math.sin(Δφ/2)**2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    def find_nearby_incidents(self, lat: float, lon: float, radius: float = 200) -> List[dict]:
        GRID_RES = 2000
        nearby = []
        
        grid_x = int(lon * GRID_RES)
        grid_y = int(lat * GRID_RES)
        
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                key = f"{grid_x + dx},{grid_y + dy}"
                if key in self.incident_grid:
                    for incident in self.incident_grid[key]:
                        dist = self.haversine_distance(lat, lon, incident['lat'], incident['lon'])
                        if dist <= radius:
                            nearby.append({**incident, 'distance': dist})
        
        return sorted(nearby, key=lambda x: x['distance'])
    
    def get_traffic_factor(self, edge_data: dict, edge_lat: float, edge_lon: float, 
                          current_time: datetime) -> tuple:
        hour = current_time.hour
        base_factor = self.hourly_congestion_factors.get(hour, 1.0)
        
        road_type = edge_data.get('highway', 'residential')
        if isinstance(road_type, list):
            road_type = road_type[0]
        sensitivity = self.road_type_sensitivity.get(road_type, 1.0)
        
        nearby_incidents = self.find_nearby_incidents(edge_lat, edge_lon, radius=200)
        
        incident_factor = 1.0
        affecting_incidents = []
        
        if nearby_incidents:
            for incident in nearby_incidents[:3]:
                severity = incident['severity']['delay_factor']
                distance_weight = 1.0 - (incident['distance'] / 200)
                incident_factor = max(incident_factor, severity * distance_weight)
                affecting_incidents.append(incident)
        
        total_factor = base_factor * sensitivity * incident_factor
        
        return max(total_factor, 0.5), affecting_incidents


class EdgeWeightLearner:
    """Learns optimal edge weights with realistic Bangalore traffic modeling"""
    
    def __init__(self):
        self.theta = {
            'aggregator': np.array([0.2, 0.5, 0.1, 0.2]),
            'logistics': np.array([0.2, 0.3, 0.3, 0.2]),
            'personal': np.array([0.3, 0.5, 0.1, 0.1])
        }
        self.prediction_errors = []
        self.learning_rate = 0.01
        
        # Realistic Bangalore speeds by road type (km/h)
        self.base_speeds = {
            'motorway': 60,      # Expressways (rare in Bangalore)
            'trunk': 45,         # Major arterial roads (ORR, Bellary Road)
            'primary': 35,       # Main city roads (MG Road, Hosur Road)
            'secondary': 28,     # Secondary roads
            'tertiary': 22,      # Smaller roads
            'residential': 18,   # Residential areas
            'motorway_link': 40,
            'trunk_link': 35,
            'primary_link': 30,
            'secondary_link': 25,
            'unclassified': 20,
            'service': 15
        }
    
    def compute_edge_weight(self, edge_data: dict, traffic_factor: float, 
                          scenario: str = 'personal') -> dict:
        length_km = edge_data.get('length', 0) / 1000
        
        # Get road type specific speed
        road_type = edge_data.get('highway', 'residential')
        if isinstance(road_type, list):
            road_type = road_type[0]
        
        # Use realistic base speed for road type
        base_speed = self.base_speeds.get(road_type, 25)
        
        # OSM maxspeed override (if available and reasonable)
        osm_maxspeed = edge_data.get('maxspeed')
        if osm_maxspeed:
            if isinstance(osm_maxspeed, list):
                osm_maxspeed = osm_maxspeed[0]
            try:
                speed_value = float(osm_maxspeed)
                # Only use if reasonable for Indian city (5-80 km/h)
                if 5 <= speed_value <= 80:
                    base_speed = speed_value * 0.7  # Actual achievable is ~70% of limit
            except (ValueError, TypeError):
                pass
        
        # Apply traffic factor (from incidents + time of day)
        adjusted_speed = base_speed / traffic_factor
        adjusted_speed = max(adjusted_speed, 2)  # Minimum 2 km/h (severe jam)
        adjusted_speed = min(adjusted_speed, base_speed)  # Can't exceed base
        
        # Calculate travel time in seconds
        travel_time = (length_km / adjusted_speed) * 3600 if adjusted_speed > 0 else length_km * 3600
        
        base_cost_per_km = 2.0
        cost = length_km * base_cost_per_km
        
        fuel_efficiency = {
            'motorway': 15, 'trunk': 14, 'primary': 12,
            'secondary': 11, 'tertiary': 10, 'residential': 9,
            'motorway_link': 13, 'trunk_link': 12
        }.get(road_type, 10)
        
        fuel_cost_per_liter = 100
        fuel = (length_km / fuel_efficiency) * fuel_cost_per_liter
        
        theta = self.theta.get(scenario, self.theta['personal'])
        normalized = np.array([
            length_km / 10,
            travel_time / 600,
            cost / 20,
            fuel / 50
        ])
        
        combined_weight = np.dot(theta, normalized)
        
        return {
            'distance': length_km,
            'travel_time': travel_time,
            'cost': cost,
            'fuel': fuel,
            'combined_weight': max(combined_weight, 0.01),
            'adjusted_speed': adjusted_speed,
            'base_speed': base_speed,
            'road_type': road_type
        }
    
    def load_model(self, filepath: str):
        try:
            import os
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    self.theta = pickle.load(f)
                print(f"✓ Loaded model from {filepath}")
        except Exception as e:
            print(f"⚠ Using default weights: {e}")


class AdaptiveRouteOptimizer:
    """Main optimizer with incident integration"""
    
    def __init__(self, G: nx.DiGraph, db_config: dict = None):
        self.G = G
        if db_config:
            self.incident_fetcher = IncidentDataFetcher(db_config)
            self.traffic_sim = TrafficDataSimulator(self.incident_fetcher)
        else:
            self.incident_fetcher = None
            self.traffic_sim = None
        self.edge_learner = EdgeWeightLearner()
        self.trip_history = []
        self.edge_incidents = {}
    
    def update_graph_weights(self, scenario: str = 'personal', 
                           current_time: datetime = None, bbox: tuple = None):
        if current_time is None:
            current_time = datetime.now()
        
        if self.traffic_sim and bbox:
            self.traffic_sim.load_incidents(bbox)
        
        self.edge_incidents = {}
        
        for u, v, data in self.G.edges(data=True):
            u_data = self.G.nodes[u]
            v_data = self.G.nodes[v]
            mid_lat = (u_data['y'] + v_data['y']) / 2
            mid_lon = (u_data['x'] + v_data['x']) / 2
            
            if self.traffic_sim:
                traffic_factor, affecting_incidents = self.traffic_sim.get_traffic_factor(
                    data, mid_lat, mid_lon, current_time
                )
                if affecting_incidents:
                    self.edge_incidents[(u, v)] = affecting_incidents
            else:
                traffic_factor = 1.0
            
            weights = self.edge_learner.compute_edge_weight(data, traffic_factor, scenario)
            
            data['travel_time'] = weights['travel_time']
            data['cost'] = weights['cost']
            data['fuel'] = weights['fuel']
            data['combined_weight'] = weights['combined_weight']
            data['traffic_factor'] = traffic_factor
            data['adjusted_speed'] = weights['adjusted_speed']
    
    def find_k_diverse_paths(self, source: int, target: int, K: int = 4, 
                           weight: str = 'combined_weight') -> List[List[int]]:
        paths = []
        edge_counts = {}
        
        try:
            first_path = nx.astar_path(self.G, source, target, weight=weight)
            paths.append(first_path)
            
            for u, v in zip(first_path[:-1], first_path[1:]):
                edge_counts[(u, v)] = 1
            
            attempts = 0
            max_attempts = K * 3
            
            while len(paths) < K and attempts < max_attempts:
                attempts += 1
                H = self.G.copy()
                
                for (u, v), count in edge_counts.items():
                    if H.has_edge(u, v):
                        penalty = 1 + (count * 0.3)
                        original_weight = self.G[u][v].get(weight, 1.0)
                        H[u][v][weight] = original_weight * penalty
                
                try:
                    alt_path = nx.astar_path(H, source, target, weight=weight)
                    path_edges = set(zip(alt_path[:-1], alt_path[1:]))
                    existing_paths_edges = [set(zip(p[:-1], p[1:])) for p in paths]
                    
                    if existing_paths_edges:
                        max_overlap = max((len(path_edges & existing) / len(path_edges) 
                                         for existing in existing_paths_edges), default=0)
                    else:
                        max_overlap = 0
                    
                    if max_overlap < 0.7:
                        paths.append(alt_path)
                        for u, v in zip(alt_path[:-1], alt_path[1:]):
                            edge_counts[(u, v)] = edge_counts.get((u, v), 0) + 1
                        
                except nx.NetworkXNoPath:
                    continue
                    
        except nx.NetworkXNoPath:
            return []
        
        return paths
    
    def compute_route_metrics(self, route: List[int]) -> dict:
        """Compute detailed metrics with actual road-based calculations"""
        total_distance = 0
        total_time = 0
        total_cost = 0
        total_fuel = 0
        route_incidents = []
        segment_details = []
        
        for u, v in zip(route[:-1], route[1:]):
            if self.G.has_edge(u, v):
                edge = self.G[u][v]
                segment_distance = edge.get('length', 0) / 1000
                segment_time = edge.get('travel_time', 0)
                segment_speed = edge.get('adjusted_speed', 25)
                road_type = edge.get('highway', 'residential')
                if isinstance(road_type, list):
                    road_type = road_type[0]
                
                total_distance += segment_distance
                total_time += segment_time
                total_cost += edge.get('cost', 0)
                total_fuel += edge.get('fuel', 0)
                
                segment_details.append({
                    'distance_km': segment_distance,
                    'time_seconds': segment_time,
                    'speed_kmh': segment_speed,
                    'road_type': road_type
                })
                
                if (u, v) in self.edge_incidents:
                    for inc in self.edge_incidents[(u, v)]:
                        if inc not in route_incidents:
                            route_incidents.append(inc)
        
        avg_speed = (total_distance / (total_time / 3600)) if total_time > 0 else 0
        
        return {
            'distance_km': total_distance,
            'time_minutes': total_time / 60,
            'time_seconds': total_time,
            'cost_rupees': total_cost,
            'fuel_rupees': total_fuel,
            'num_nodes': len(route),
            'incidents': route_incidents,
            'incident_count': len(route_incidents),
            'average_speed': avg_speed,
            'segment_details': segment_details
        }
    
    def optimize_route(self, src_lat: float, src_lon: float, 
                      dst_lat: float, dst_lon: float,
                      scenario: str = 'personal',
                      current_time: datetime = None,
                      K: int = 4) -> tuple:
        if current_time is None:
            current_time = datetime.now()
        
        bbox = (
            min(src_lat, dst_lat) - 0.05,
            min(src_lon, dst_lon) - 0.05,
            max(src_lat, dst_lat) + 0.05,
            max(src_lon, dst_lon) + 0.05
        )
        
        self.update_graph_weights(scenario, current_time, bbox)
        
        source = ox.distance.nearest_nodes(self.G, src_lon, src_lat)
        target = ox.distance.nearest_nodes(self.G, dst_lon, dst_lat)
        
        routes = self.find_k_diverse_paths(source, target, K=K)
        
        if not routes:
            return [], []
        
        route_metrics = [self.compute_route_metrics(r) for r in routes]
        
        return routes, route_metrics


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371000
    φ1 = lat1 * 0.017453292519943295
    φ2 = lat2 * 0.017453292519943295
    Δφ = (lat2 - lat1) * 0.017453292519943295
    Δλ = (lng2 - lng1) * 0.017453292519943295
    a = math.sin(Δφ * 0.5) * math.sin(Δφ * 0.5) + \
        math.cos(φ1) * math.cos(φ2) * \
        math.sin(Δλ * 0.5) * math.sin(Δλ * 0.5)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_incidents_using_postgis(route_coords):
    """Get incidents within 200m and snap to route line"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        coords_wkt = ', '.join([f"{lng} {lat}" for lat, lng in route_coords])
        route_linestring = f"LINESTRING({coords_wkt})"
        
        query = """
            WITH route_line AS (
                SELECT ST_SetSRID(ST_GeomFromText(%s), 4326) AS geom
            ),
            nearby_incidents AS (
                SELECT 
                    i.id, i.ty, i.latitude, i.longitude,
                    i.d as description, i.f as location_from, i.t as location_to,
                    COALESCE(CAST(i.l AS INTEGER), 300) as length,
                    ST_Distance(i.geom_indexed::geography, (SELECT geom::geography FROM route_line)) as distance_m,
                    ST_ClosestPoint((SELECT geom FROM route_line), ST_SetSRID(ST_MakePoint(i.longitude, i.latitude), 4326)) as snapped_point
                FROM incidents i, route_line
                WHERE i.latitude IS NOT NULL AND i.longitude IS NOT NULL
                AND ST_DWithin(i.geom_indexed::geography, (SELECT geom::geography FROM route_line), 200)
            )
            SELECT 
                id, ty, latitude, longitude, description, location_from, location_to, length, distance_m,
                ST_X(snapped_point) as snapped_lng,
                ST_Y(snapped_point) as snapped_lat
            FROM nearby_incidents
            ORDER BY distance_m ASC
        """
        
        cursor.execute(query, (route_linestring,))
        incidents = cursor.fetchall()
        cursor.close()
        conn.close()
        
        route_incidents = []
        for inc in incidents:
            ty = int(inc.get('ty', 1))
            config = INCIDENT_TYPE_MAPPING.get(ty, INCIDENT_TYPE_MAPPING[1])
            
            snapped_lat = float(inc['snapped_lat'])
            snapped_lng = float(inc['snapped_lng'])
            
            route_incidents.append({
                'id': inc['id'],
                'lat': snapped_lat,
                'lng': snapped_lng,
                'original_lat': float(inc['latitude']),
                'original_lng': float(inc['longitude']),
                'ty': ty,
                'severity': config['color'],
                'type': config['name'],
                'icon': config['icon'],
                'description': inc.get('description', ''),
                'location': f"{inc.get('location_from', '')} - {inc.get('location_to', '')}",
                'affected_distance': int(inc['length']),
                'speed': config['speed'],
                'distance_to_route': float(inc['distance_m'])
            })
        
        print(f"✅ Found {len(route_incidents)} incidents (snapped to route)")
        return route_incidents
        
    except Exception as e:
        print(f"❌ PostGIS error: {e}")
        return []


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/search-location")
async def search_location(query: str):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': query, 'format': 'json', 'limit': 5, 'addressdetails': 1}
        headers = {'User-Agent': 'RouteOptimizerApp/1.0'}
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        results = response.json()
        
        formatted_results = [{
            'display_name': r.get('display_name', ''),
            'lat': float(r.get('lat', 0)),
            'lon': float(r.get('lon', 0)),
            'type': r.get('type', ''),
            'address': r.get('address', {})
        } for r in results]
        
        return {'results': formatted_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize-route")
async def optimize_route(request: RouteRequest):
    try:
        print(f"📍 Optimizing route from ({request.src_lat}, {request.src_lon}) to ({request.dst_lat}, {request.dst_lon})")
        
        center_lat = (request.src_lat + request.dst_lat) / 2
        center_lon = (request.src_lon + request.dst_lon) / 2
        bbox = ox.utils_geo.bbox_from_point((center_lat, center_lon), dist=3000)
        cache_key = f"{bbox}_{request.scenario}"
        
        if cache_key not in optimizer_cache:
            print("🔄 Loading network data...")
            G_multi = ox.graph_from_bbox(bbox=bbox, network_type="drive", simplify=True)
            G = nx.DiGraph()
            G.graph.update(G_multi.graph)
            for n, d in G_multi.nodes(data=True):
                G.add_node(n, **d)
            for u, v, data in G_multi.edges(data=True):
                if G.has_edge(u, v):
                    if data.get('length', float('inf')) < G[u][v].get('length', float('inf')):
                        G[u][v].update(data)
                else:
                    G.add_edge(u, v, **data)
            
            optimizer = AdaptiveRouteOptimizer(G, DB_CONFIG)
            optimizer.edge_learner.load_model('learned_weights.pkl')
            optimizer_cache[cache_key] = optimizer
            print(f"✅ Network cached: {len(G.nodes)} nodes, {len(G.edges)} edges")
        else:
            optimizer = optimizer_cache[cache_key]
            print("✅ Using cached network")
        
        routes, metrics = optimizer.optimize_route(
            request.src_lat, request.src_lon,
            request.dst_lat, request.dst_lon,
            scenario=request.scenario, K=3
        )
        
        if not routes:
            raise HTTPException(status_code=404, detail="No routes found")
        
        # Get incidents for each route using PostGIS
        all_routes_incidents = []
        for route in routes:
            route_coords = [(optimizer.G.nodes[n]['y'], optimizer.G.nodes[n]['x']) 
                          for n in route if n in optimizer.G.nodes]
            incidents = get_incidents_using_postgis(route_coords)
            all_routes_incidents.append(incidents)
        
        map_html = generate_multi_route_map(
            optimizer.G, routes, metrics, all_routes_incidents,
            request.src_lat, request.src_lon,
            request.dst_lat, request.dst_lon
        )
        
        routes_serializable = [[int(node) for node in route] for route in routes]
        
        return {
            'routes': routes_serializable,
            'metrics': metrics,
            'incidents': all_routes_incidents,
            'map_html': map_html,
            'status': 'success'
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def generate_multi_route_map(G, routes, route_metrics, all_incidents, src_lat, src_lon, dst_lat, dst_lon):
    """Generate map with routes and incidents"""
    center_lat = (src_lat + dst_lat) / 2
    center_lon = (src_lon + dst_lon) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    
    colors = ['#0066ff', '#00cc66', '#cc6600']
    
    for idx, (route, metrics) in enumerate(zip(routes, route_metrics)):
        route_coords = []
        for node in route:
            if node in G.nodes:
                node_data = G.nodes[node]
                route_coords.append([node_data['y'], node_data['x']])
        
        if route_coords:
            tooltip = f"""
            <b>Route {idx+1}</b><br>
            Time: {metrics['time_minutes']:.1f} min<br>
            Distance: {metrics['distance_km']:.2f} km<br>
            Incidents: {metrics['incident_count']}
            """
            
            folium.PolyLine(
                locations=route_coords,
                color=colors[idx % len(colors)],
                weight=6,
                opacity=0.7,
                tooltip=tooltip
            ).add_to(m)
    
    # Add incidents (deduplicated)
    all_incidents_set = {}
    for incidents in all_incidents:
        for inc in incidents:
            if inc['id'] not in all_incidents_set:
                all_incidents_set[inc['id']] = inc
    
    for inc in all_incidents_set.values():
        color = SPEED_RANGES[inc['severity']]['color']
        folium.CircleMarker(
            location=[inc['lat'], inc['lng']],
            radius=10,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.9,
            popup=f"<b>{inc['icon']} {inc['type']}</b><br>{inc['description']}<br>Speed: {inc['speed']} km/h",
            tooltip=f"{inc['icon']} {inc['type']}"
        ).add_to(m)
    
    folium.Marker([src_lat, src_lon], tooltip="Start", icon=folium.Icon(color="green", icon="play", prefix='fa')).add_to(m)
    folium.Marker([dst_lat, dst_lon], tooltip="Destination", icon=folium.Icon(color="red", icon="stop", prefix='fa')).add_to(m)
    
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; width: 220px; background: white; z-index:9999; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        <p style="margin: 0 0 12px 0; font-weight: bold; font-size: 14px;">🚦 Traffic Incidents</p>
        <div style="margin: 8px 0; font-size: 12px;">
            <div style="width: 20px; height: 20px; background: #ff9900; border-radius: 50%; display: inline-block; margin-right: 8px;"></div>
            Moderate (18 km/h)
        </div>
        <div style="margin: 8px 0; font-size: 12px;">
            <div style="width: 20px; height: 20px; background: #ff0000; border-radius: 50%; display: inline-block; margin-right: 8px;"></div>
            Heavy (12 km/h)
        </div>
        <div style="margin: 8px 0; font-size: 12px;">
            <div style="width: 20px; height: 20px; background: #8b0000; border-radius: 50%; display: inline-block; margin-right: 8px;"></div>
            Severe (8 km/h)
        </div>
        <div style="margin: 8px 0; font-size: 12px;">
            <div style="width: 20px; height: 20px; background: #660000; border-radius: 50%; display: inline-block; margin-right: 8px;"></div>
            Blocked (2 km/h)
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m._parent.render()


@app.post("/api/start-navigation")
async def start_navigation(session: NavigationSession):
    try:
        session_id = f"nav_{datetime.now().strftime('%Y%m%d%H%M%S')}_{session.user_id}"
        
        center_lat = (session.src_lat + session.dst_lat) / 2
        center_lon = (session.src_lon + session.dst_lon) / 2
        bbox = ox.utils_geo.bbox_from_point((center_lat, center_lon), dist=3000)
        cache_key = f"{bbox}_personal"
        
        if cache_key not in optimizer_cache:
            raise HTTPException(status_code=404, detail="Network data not found. Please optimize route first.")
        
        optimizer = optimizer_cache[cache_key]
        G = optimizer.G
        
        # Build route with actual edge data
        route_segments = []
        total_distance = 0
        
        for i in range(len(session.selected_route) - 1):
            u = session.selected_route[i]
            v = session.selected_route[i + 1]
            
            if u in G.nodes and v in G.nodes:
                u_data = G.nodes[u]
                v_data = G.nodes[v]
                
                # Get edge data
                edge_data = G[u][v] if G.has_edge(u, v) else {}
                
                segment_distance = edge_data.get('length', 0) / 1000  # km
                adjusted_speed = edge_data.get('adjusted_speed', 25)  # km/h
                road_type = edge_data.get('highway', 'residential')
                if isinstance(road_type, list):
                    road_type = road_type[0]
                
                segment_time_hours = segment_distance / adjusted_speed if adjusted_speed > 0 else segment_distance / 25
                
                route_segments.append({
                    'start': [u_data['y'], u_data['x']],
                    'end': [v_data['y'], v_data['x']],
                    'distance_km': segment_distance,
                    'speed_kmh': adjusted_speed,
                    'time_seconds': segment_time_hours * 3600,
                    'road_type': road_type
                })
                
                total_distance += segment_distance
        
        route_coords = [seg['start'] for seg in route_segments]
        if route_segments:
            route_coords.append(route_segments[-1]['end'])
        
        # Get incidents using PostGIS
        route_coords_tuple = [(c[0], c[1]) for c in route_coords]
        incidents = get_incidents_using_postgis(route_coords_tuple)
        
        # Apply incident impacts to segments
        segment_speeds = []
        segment_distances = []
        
        for seg in route_segments:
            base_speed = seg['speed_kmh']
            segment_distance = seg['distance_km'] * 1000  # meters
            
            # Check incidents affecting this segment
            min_speed = base_speed
            for inc in incidents:
                # Check if incident is near this segment
                seg_mid_lat = (seg['start'][0] + seg['end'][0]) / 2
                seg_mid_lng = (seg['start'][1] + seg['end'][1]) / 2
                
                dist_to_inc = haversine_distance(
                    seg_mid_lat, seg_mid_lng,
                    inc['lat'], inc['lng']
                )
                
                # If incident is within affected distance
                if dist_to_inc < inc['affected_distance']:
                    min_speed = min(min_speed, inc['speed'])
            
            segment_speeds.append(min_speed)
            segment_distances.append(segment_distance)
        
        # Calculate total realistic time
        total_time_seconds = 0
        for dist_m, speed_kmh in zip(segment_distances, segment_speeds):
            if speed_kmh > 0:
                total_time_seconds += (dist_m / 1000 / speed_kmh) * 3600
            else:
                total_time_seconds += (dist_m / 1000 / 25) * 3600
        
        total_time_minutes = int(total_time_seconds / 60)
        avg_speed = (total_distance / (total_time_seconds / 3600)) if total_time_seconds > 0 else 25
        
        print(f"⏱️  Navigation Details:")
        print(f"   Distance: {total_distance:.2f} km")
        print(f"   Time: {total_time_minutes} min ({total_time_seconds:.0f} sec)")
        print(f"   Avg Speed: {avg_speed:.1f} km/h")
        print(f"   Segments: {len(route_segments)}")
        print(f"   Incidents: {len(incidents)}")
        
        nav_map_html = generate_navigation_map(
            route_coords, incidents, segment_speeds, total_time_seconds,
            session.src_lat, session.src_lon,
            session.dst_lat, session.dst_lon
        )
        
        active_sessions[session_id] = {
            'route': session.selected_route,
            'last_update': datetime.now(),
            'eta_minutes': total_time_minutes,
            'distance_km': total_distance,
            'average_speed': avg_speed
        }
        
        # Store in database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS navigation_history (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) UNIQUE,
                    user_id VARCHAR(255),
                    route_id INTEGER,
                    src_lat DOUBLE PRECISION,
                    src_lon DOUBLE PRECISION,
                    dst_lat DOUBLE PRECISION,
                    dst_lon DOUBLE PRECISION,
                    distance_km DOUBLE PRECISION,
                    estimated_time INTEGER,
                    average_speed DOUBLE PRECISION,
                    start_time TIMESTAMP DEFAULT NOW(),
                    status VARCHAR(50) DEFAULT 'active'
                )
            """)
            cursor.execute("""
                INSERT INTO navigation_history (session_id, user_id, route_id, src_lat, src_lon, dst_lat, dst_lon, distance_km, estimated_time, average_speed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (session_id, session.user_id, session.route_id, session.src_lat, session.src_lon, 
                  session.dst_lat, session.dst_lon, total_distance, total_time_minutes, avg_speed))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as db_error:
            print(f"⚠️ Database logging error: {db_error}")
        
        return {
            'session_id': session_id,
            'status': 'started',
            'map_html': nav_map_html,
            'distance_km': round(total_distance, 2),
            'eta_minutes': total_time_minutes,
            'average_speed': round(avg_speed, 1),
            'num_segments': len(route_segments),
            'num_incidents': len(incidents),
            'message': f'Navigation started: {total_distance:.1f} km in ~{total_time_minutes} min'
        }
        
    except Exception as e:
        print(f"❌ Navigation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def generate_navigation_map(route_coords, incidents, segment_speeds, total_time_seconds, 
                           src_lat, src_lon, dst_lat, dst_lon):
    """Generate navigation map with moving car simulation"""
    center_lat = (src_lat + dst_lat) / 2
    center_lon = (src_lon + dst_lon) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)
    
    # Draw route in blue
    folium.PolyLine(
        locations=route_coords,
        color='#0066ff',
        weight=10,
        opacity=0.9,
        tooltip="Your Route"
    ).add_to(m)
    
    # Add incidents as colored markers ON the route
    for inc in incidents:
        color = SPEED_RANGES[inc['severity']]['color']
        folium.CircleMarker(
            location=[inc['lat'], inc['lng']],
            radius=12,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.9,
            popup=f"<b>{inc['icon']} {inc['type']}</b><br>{inc['description']}<br>Speed: {inc['speed']} km/h<br>Affected: {inc['affected_distance']}m",
            tooltip=f"{inc['icon']} {inc['type']}"
        ).add_to(m)
    
    folium.Marker([src_lat, src_lon], tooltip="Start", icon=folium.Icon(color="green", icon="play", prefix='fa')).add_to(m)
    folium.Marker([dst_lat, dst_lon], tooltip="Destination", icon=folium.Icon(color="red", icon="flag-checkered", prefix='fa')).add_to(m)
    
    # Calculate durations for each segment
    map_name = m.get_name()
    total_time_minutes = int(total_time_seconds / 60)
    
    moving_car_js = f"""
    <script>
    (function() {{
        var routeCoords = {json.dumps(route_coords)};
        var segmentSpeeds = {json.dumps(segment_speeds)};
        var totalTime = {total_time_seconds};
        
        // Wait for Leaflet to be fully loaded
        function waitForLeaflet() {{
            if (typeof L === 'undefined' || !window.{map_name}) {{
                setTimeout(waitForLeaflet, 100);
                return;
            }}
            startCustomAnimation();
        }}
        
        // Calculate realistic segment durations
        var durations = [];
        for (let i = 0; i < routeCoords.length - 1; i++) {{
            let lat1 = routeCoords[i][0] * Math.PI / 180;
            let lat2 = routeCoords[i+1][0] * Math.PI / 180;
            let dLat = (routeCoords[i+1][0] - routeCoords[i][0]) * Math.PI / 180;
            let dLon = (routeCoords[i+1][1] - routeCoords[i][1]) * Math.PI / 180;
            let a = Math.sin(dLat/2) * Math.sin(dLat/2) + 
                    Math.cos(lat1) * Math.cos(lat2) * 
                    Math.sin(dLon/2) * Math.sin(dLon/2);
            let distance = 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            durations.push((distance / segmentSpeeds[i]) * 3600 * 1000);
        }}
        
        function startCustomAnimation() {{
            var map = window.{map_name};
            if (!map) {{
                console.error('❌ Map object not found');
                return;
            }}
            
            console.log('🚗 Starting custom car animation...');
            
            // Create car icon
            var carIcon = L.divIcon({{
                html: '<div style="font-size: 32px; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3)); transition: transform 0.3s;">🚗</div>',
                iconSize: [40, 40],
                iconAnchor: [20, 20],
                className: ''
            }});
            
            var carMarker = L.marker(routeCoords[0], {{icon: carIcon}}).addTo(map);
            
            // Create info display
            var display = L.control({{position: 'topright'}});
            display.onAdd = function() {{
                var div = L.DomUtil.create('div');
                div.innerHTML = '<div style="background:white;padding:20px;border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,0.3);font-family:Arial">' +
                    '<div style="display:flex;align-items:center;margin-bottom:15px">' +
                    '<div style="font-size:40px;margin-right:15px">🚗</div>' +
                    '<div><div style="color:#666;font-size:12px;text-transform:uppercase">Current Speed</div>' +
                    '<div id="spd" style="font-size:36px;font-weight:bold;color:#0066ff">' + segmentSpeeds[0] + ' <span style="font-size:20px">km/h</span></div></div>' +
                    '</div>' +
                    '<div style="border-top:2px solid #eee;padding-top:15px">' +
                    '<div style="color:#666;font-size:12px;text-transform:uppercase">Time Remaining</div>' +
                    '<div id="eta" style="font-size:24px;font-weight:600;color:#333">' + {total_time_minutes} + ' min</div>' +
                    '</div>' +
                    '<div style="margin-top:10px;"><button id="pauseBtn" style="background:#0066ff;color:white;border:none;padding:8px 16px;border-radius:5px;cursor:pointer;font-size:12px;">⏸️ Pause</button></div>' +
                    '</div>';
                return div;
            }};
            display.addTo(map);
            
            // Animation variables
            var currentSegment = 0;
            var segmentProgress = 0;
            var startTime = Date.now();
            var isPaused = false;
            var animationFrame;
            
            // Pause/Resume functionality
            setTimeout(function() {{
                var pauseBtn = document.getElementById('pauseBtn');
                if (pauseBtn) {{
                    pauseBtn.addEventListener('click', function() {{
                        isPaused = !isPaused;
                        this.innerHTML = isPaused ? '▶️ Resume' : '⏸️ Pause';
                        if (!isPaused) {{
                            startTime = Date.now() - (segmentProgress * durations[currentSegment]);
                            animate();
                        }}
                    }});
                }}
            }}, 500);
            
            function lerp(start, end, t) {{
                return start + (end - start) * t;
            }}
            
            function animate() {{
                if (isPaused) return;
                
                var now = Date.now();
                var elapsed = now - startTime;
                
                // Calculate total elapsed time across all segments
                var totalElapsed = 0;
                var currentSeg = 0;
                
                for (var i = 0; i < durations.length; i++) {{
                    if (totalElapsed + durations[i] > elapsed) {{
                        currentSeg = i;
                        break;
                    }}
                    totalElapsed += durations[i];
                }}
                
                if (currentSeg >= durations.length) {{
                    // Animation complete
                    carMarker.setLatLng(routeCoords[routeCoords.length - 1]);
                    var etaElem = document.getElementById('eta');
                    var spdElem = document.getElementById('spd');
                    if (etaElem) etaElem.innerHTML = '🎉 Arrived!';
                    if (spdElem) spdElem.innerHTML = '0 <span style="font-size:20px">km/h</span>';
                    var pauseBtn = document.getElementById('pauseBtn');
                    if (pauseBtn) pauseBtn.style.display = 'none';
                    console.log('✅ Navigation completed!');
                    return;
                }}
                
                // Calculate progress within current segment
                var segmentElapsed = elapsed - totalElapsed;
                var progress = Math.min(segmentElapsed / durations[currentSeg], 1);
                
                // Interpolate position
                var startCoord = routeCoords[currentSeg];
                var endCoord = routeCoords[currentSeg + 1];
                var newLat = lerp(startCoord[0], endCoord[0], progress);
                var newLng = lerp(startCoord[1], endCoord[1], progress);
                
                carMarker.setLatLng([newLat, newLng]);
                
                // Update UI
                var spdElem = document.getElementById('spd');
                var etaElem = document.getElementById('eta');
                
                if (spdElem && currentSeg < segmentSpeeds.length) {{
                    spdElem.innerHTML = segmentSpeeds[currentSeg] + ' <span style="font-size:20px">km/h</span>';
                }}
                
                if (etaElem) {{
                    var remainingTime = totalTime - (elapsed / 1000);
                    var mins = Math.max(0, Math.floor(remainingTime / 60));
                    var secs = Math.max(0, Math.floor(remainingTime % 60));
                    etaElem.innerHTML = mins + ':' + (secs < 10 ? '0' : '') + secs;
                }}
                
                // Continue animation
                animationFrame = requestAnimationFrame(animate);
            }}
            
            // Start animation
            animate();
            
            console.log('✅ Custom animation started! Duration: ' + (totalTime/60).toFixed(1) + ' min');
        }}
        
        // Start when ready
        waitForLeaflet();
    }})();
    </script>
    """
    
    m.get_root().html.add_child(folium.Element(moving_car_js))
    
    # Traffic legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 220px; background: white; z-index:9999; padding: 15px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <p style="margin: 0 0 12px 0; font-weight: bold; font-size: 14px;">🚦 Traffic Conditions</p>
        <div style="margin: 10px 0; font-size: 12px;">
            <div style="width: 20px; height: 20px; background: #0066ff; border-radius: 50%; display: inline-block; margin-right: 8px;"></div>
            Normal (25 km/h)
        </div>
        <div style="margin: 10px 0; font-size: 12px;">
            <div style="width: 20px; height: 20px; background: #ff9900; border-radius: 50%; display: inline-block; margin-right: 8px;"></div>
            Moderate (18 km/h)
        </div>
        <div style="margin: 10px 0; font-size: 12px;">
            <div style="width: 20px; height: 20px; background: #ff0000; border-radius: 50%; display: inline-block; margin-right: 8px;"></div>
            Heavy (12 km/h)
        </div>
        <div style="margin: 10px 0; font-size: 12px;">
            <div style="width: 20px; height: 20px; background: #8b0000; border-radius: 50%; display: inline-block; margin-right: 8px;"></div>
            Severe (8 km/h)
        </div>
        <div style="margin: 10px 0; font-size: 12px;">
            <div style="width: 20px; height: 20px; background: #660000; border-radius: 50%; display: inline-block; margin-right: 8px;"></div>
            Blocked (2 km/h)
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m._parent.render()


@app.get("/api/navigation-status/{session_id}")
async def get_navigation_status(session_id: str):
    """Get current navigation session status"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        
        return {
            'session_id': session_id,
            'status': 'active',
            'last_update': session['last_update'].isoformat(),
            'eta_minutes': session.get('eta_minutes', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/navigation-feedback")
async def submit_navigation_feedback(session_id: str, actual_time_minutes: float):
    """Submit feedback for adaptive learning"""
    try:
        # This would update the learning model
        print(f"📊 Feedback received for session {session_id}: {actual_time_minutes} minutes")
        
        # Update database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE navigation_history
            SET actual_time = %s, status = 'completed', end_time = NOW()
            WHERE session_id = %s
        """, (actual_time_minutes, session_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'status': 'success', 'message': 'Feedback recorded'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cached_networks": len(optimizer_cache),
        "active_sessions": len(active_sessions)
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Adaptive Route Optimizer API",
        "version": "2.0",
        "endpoints": {
            "search": "/api/search-location?query=<location>",
            "optimize": "/api/optimize-route (POST)",
            "navigate": "/api/start-navigation (POST)",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Adaptive Route Optimizer API...")
    print("📍 Server: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)