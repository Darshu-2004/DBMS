import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
import folium
import numpy as np
import pickle
import os
from datetime import datetime
from typing import List, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')


class TrafficDataSimulator:
    """Simulates dynamic traffic data f(position, time)"""
    
    def __init__(self):
        # Simulate different traffic patterns by hour
        self.hourly_congestion_factors = {
            # Rush hours
            7: 1.8, 8: 2.0, 9: 1.7,  # Morning
            17: 1.9, 18: 2.1, 19: 1.8,  # Evening
            # Normal hours
            10: 1.2, 11: 1.2, 12: 1.3, 13: 1.3, 14: 1.2, 15: 1.3, 16: 1.4,
            # Off-peak
            0: 0.8, 1: 0.7, 2: 0.7, 3: 0.7, 4: 0.7, 5: 0.9, 6: 1.0,
            20: 1.4, 21: 1.2, 22: 1.0, 23: 0.9
        }
        
        # Road type congestion sensitivity
        self.road_type_sensitivity = {
            'primary': 1.5,
            'secondary': 1.3,
            'tertiary': 1.2,
            'residential': 1.0,
            'trunk': 1.4,
            'motorway': 1.1,
            'motorway_link': 1.2,
            'trunk_link': 1.3,
            'primary_link': 1.4,
            'secondary_link': 1.3
        }
    
    def get_traffic_factor(self, edge_data: dict, current_time: datetime) -> float:
        """
        Returns traffic congestion factor for an edge at given time
        f(position, time) -> congestion_factor
        """
        hour = current_time.hour
        base_factor = self.hourly_congestion_factors.get(hour, 1.0)
        
        # Get road type
        road_type = edge_data.get('highway', 'residential')
        if isinstance(road_type, list):
            road_type = road_type[0]
        
        # Apply road-specific sensitivity
        sensitivity = self.road_type_sensitivity.get(road_type, 1.0)
        
        # Add some randomness to simulate real-world variability
        np.random.seed(hash((hour, str(edge_data.get('osmid', 0)))) % (2**32))
        random_factor = np.random.uniform(0.95, 1.05)
        
        traffic_factor = base_factor * sensitivity * random_factor
        
        return max(traffic_factor, 0.5)  # Minimum factor of 0.5


class EdgeWeightLearner:
    """Learns optimal edge weights from experience"""
    
    def __init__(self):
        # Learnable parameters for different scenarios
        self.theta = {
            'aggregator': np.array([0.2, 0.5, 0.1, 0.2]),  # [distance, time, cost, fuel]
            'logistics': np.array([0.2, 0.3, 0.3, 0.2]),
            'personal': np.array([0.3, 0.5, 0.1, 0.1])
        }
        
        # Store prediction errors for learning
        self.prediction_errors = []
        self.learning_rate = 0.01
    
    def compute_edge_weight(self, edge_data: dict, traffic_factor: float, 
                          scenario: str = 'personal') -> dict:
        """
        Compute multi-objective edge weight
        Returns dict with all components
        """
        length_km = edge_data.get('length', 0) / 1000
        
        # Get base speed
        base_speed = edge_data.get('maxspeed', 40)
        if isinstance(base_speed, list):
            base_speed = base_speed[0]
        try:
            base_speed = float(base_speed)
        except (ValueError, TypeError):
            base_speed = 40
        
        # Adjust speed for traffic
        adjusted_speed = base_speed / traffic_factor
        adjusted_speed = max(adjusted_speed, 5)  # Minimum 5 km/h
        
        # Time component
        travel_time = (length_km / adjusted_speed) * 3600  # seconds
        
        # Cost component (tolls, wear-and-tear)
        base_cost_per_km = 2.0  # ₹2 per km baseline
        cost = length_km * base_cost_per_km
        
        # Fuel component (varies by road type and speed)
        road_type = edge_data.get('highway', 'residential')
        if isinstance(road_type, list):
            road_type = road_type[0]
        
        fuel_efficiency = {
            'motorway': 15,  # km per liter
            'trunk': 14,
            'primary': 12,
            'secondary': 11,
            'tertiary': 10,
            'residential': 9,
            'motorway_link': 13,
            'trunk_link': 12,
            'primary_link': 11
        }.get(road_type, 10)
        
        fuel_cost_per_liter = 100  # ₹100 per liter
        fuel = (length_km / fuel_efficiency) * fuel_cost_per_liter
        
        # Weighted combination using learned theta
        theta = self.theta.get(scenario, self.theta['personal'])
        
        # Normalize components to similar scales
        normalized = np.array([
            length_km / 10,  # normalize distance
            travel_time / 600,  # normalize time
            cost / 20,  # normalize cost
            fuel / 50  # normalize fuel
        ])
        
        combined_weight = np.dot(theta, normalized)
        
        return {
            'distance': length_km,
            'travel_time': travel_time,
            'cost': cost,
            'fuel': fuel,
            'combined_weight': max(combined_weight, 0.01)  # Prevent zero weights
        }
    
    def update_from_feedback(self, route_data: dict, actual_performance: dict, 
                            scenario: str):
        """
        ADAPTIVE LEARNING: Update theta based on actual performance
        """
        predicted_time = route_data['predicted_time']
        actual_time = actual_performance['actual_time']
        
        # Calculate error
        error = actual_time - predicted_time
        self.prediction_errors.append(error)
        
        # Gradient-based update (simplified)
        if abs(error) > 60:  # More than 1 minute error
            # Adjust time weight
            if error > 0:  # Under-predicted (too optimistic)
                self.theta[scenario][1] *= (1 + self.learning_rate)
            else:  # Over-predicted (too pessimistic)
                self.theta[scenario][1] *= (1 - self.learning_rate)
            
            # Normalize to keep sum consistent
            theta_sum = np.sum(self.theta[scenario])
            if theta_sum > 0:
                self.theta[scenario] = self.theta[scenario] / theta_sum
        
        print(f"📊 Learning Update: Error={error/60:.1f}min, "
              f"New theta[{scenario}]={self.theta[scenario]}")
    
    def save_model(self, filepath: str):
        """Save learned parameters"""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self.theta, f)
            print(f"✓ Model saved to {filepath}")
        except Exception as e:
            print(f"⚠ Error saving model: {e}")
    
    def load_model(self, filepath: str):
        """Load learned parameters"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    self.theta = pickle.load(f)
                print(f"✓ Loaded learned model from {filepath}")
            else:
                print("⚠ No saved model found, using defaults")
        except Exception as e:
            print(f"⚠ Error loading model: {e}, using defaults")
    
    def get_learning_stats(self) -> dict:
        """Get statistics about learning progress"""
        if not self.prediction_errors:
            return {'status': 'No learning data yet'}
        
        errors = np.array(self.prediction_errors)
        return {
            'num_trips': len(errors),
            'mean_error_seconds': np.mean(errors),
            'std_error_seconds': np.std(errors),
            'mae_minutes': np.mean(np.abs(errors)) / 60,
            'recent_5_mae_minutes': np.mean(np.abs(errors[-5:])) / 60 if len(errors) >= 5 else None
        }


class AdaptiveRouteOptimizer:
    """Main adaptive route optimization system"""
    
    def __init__(self, G: nx.DiGraph):
        self.G = G
        self.traffic_sim = TrafficDataSimulator()
        self.edge_learner = EdgeWeightLearner()
        self.trip_history = []
        
    def update_graph_weights(self, scenario: str = 'personal', 
                           current_time: datetime = None):
        """
        ADAPTIVE LEARNING POINT 1: Update all edge weights with learned parameters
        """
        if current_time is None:
            current_time = datetime.now()
        
        print(f"⚡ Updating edge weights for scenario: {scenario} at {current_time.hour}:00")
        
        for u, v, data in self.G.edges(data=True):
            # Get traffic factor f(position, time)
            traffic_factor = self.traffic_sim.get_traffic_factor(data, current_time)
            
            # Compute multi-objective weight using learned parameters
            weights = self.edge_learner.compute_edge_weight(data, traffic_factor, scenario)
            
            # Update edge data
            data['travel_time'] = weights['travel_time']
            data['cost'] = weights['cost']
            data['fuel'] = weights['fuel']
            data['combined_weight'] = weights['combined_weight']
            data['traffic_factor'] = traffic_factor
    
    def find_k_diverse_paths(self, source: int, target: int, K: int = 4, 
                           weight: str = 'combined_weight', 
                           diversity_factor: float = 0.3) -> List[List[int]]:
        """
        Find K diverse paths using penalty method
        This is your search space exploration
        """
        paths = []
        edge_counts = {}
        
        try:
            # First path using A*
            first_path = nx.astar_path(self.G, source, target, weight=weight)
            paths.append(first_path)
            
            # Update edge counts
            for u, v in zip(first_path[:-1], first_path[1:]):
                edge_counts[(u, v)] = 1
            
            attempts = 0
            max_attempts = K * 3
            
            while len(paths) < K and attempts < max_attempts:
                attempts += 1
                
                # Create temporary graph with penalties
                H = self.G.copy()
                
                for (u, v), count in edge_counts.items():
                    if H.has_edge(u, v):
                        penalty = 1 + (count * diversity_factor)
                        original_weight = self.G[u][v].get(weight, 1.0)
                        H[u][v][weight] = original_weight * penalty
                
                try:
                    alt_path = nx.astar_path(H, source, target, weight=weight)
                    
                    # Check diversity
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
            print("⚠ No path found between source and target")
            return []
        except Exception as e:
            print(f"⚠ Error finding paths: {e}")
            return []
        
        return paths
    
    def compute_route_metrics(self, route: List[int]) -> dict:
        """Compute all metrics for a route"""
        total_distance = 0
        total_time = 0
        total_cost = 0
        total_fuel = 0
        
        for u, v in zip(route[:-1], route[1:]):
            if self.G.has_edge(u, v):
                edge = self.G[u][v]
                total_distance += edge.get('length', 0) / 1000
                total_time += edge.get('travel_time', 0)
                total_cost += edge.get('cost', 0)
                total_fuel += edge.get('fuel', 0)
        
        return {
            'distance_km': total_distance,
            'time_minutes': total_time / 60,
            'cost_rupees': total_cost,
            'fuel_rupees': total_fuel,
            'num_nodes': len(route)
        }
    
    def optimize_route(self, src_lat: float, src_lon: float, 
                      dst_lat: float, dst_lon: float,
                      scenario: str = 'personal',
                      current_time: datetime = None,
                      K: int = 4) -> Tuple[List[List[int]], List[dict]]:
        """
        Main optimization function with adaptive learning
        """
        if current_time is None:
            current_time = datetime.now()
        
        # LEARNING POINT 1: Update graph with learned weights
        self.update_graph_weights(scenario, current_time)
        
        # Find nearest nodes
        source = ox.distance.nearest_nodes(self.G, src_lon, src_lat)
        target = ox.distance.nearest_nodes(self.G, dst_lon, dst_lat)
        
        print(f"📍 Source node: {source}, Target node: {target}")
        
        # SEARCH SPACE: Full graph with k diverse alternatives
        print(f"🚗 Computing {K} alternative routes...")
        routes = self.find_k_diverse_paths(source, target, K=K)
        
        if not routes:
            print("⚠ No routes found!")
            return [], []
        
        # Compute metrics for all routes
        route_metrics = [self.compute_route_metrics(r) for r in routes]
        
        # Store for potential feedback learning
        self.current_trip = {
            'routes': routes,
            'metrics': route_metrics,
            'scenario': scenario,
            'time': current_time
        }
        
        return routes, route_metrics
    
    def process_trip_feedback(self, selected_route_idx: int, 
                             actual_time_minutes: float):
        """
        ADAPTIVE LEARNING POINT 2: Learn from actual performance
        """
        if not hasattr(self, 'current_trip'):
            print("⚠ No current trip to update")
            return
        
        trip = self.current_trip
        
        if selected_route_idx >= len(trip['metrics']):
            print(f"⚠ Invalid route index: {selected_route_idx}")
            return
        
        predicted_time = trip['metrics'][selected_route_idx]['time_minutes']
        
        # Update learner
        self.edge_learner.update_from_feedback(
            route_data={'predicted_time': predicted_time * 60},  # convert to seconds
            actual_performance={'actual_time': actual_time_minutes * 60},
            scenario=trip['scenario']
        )
        
        # Store in history
        self.trip_history.append({
            'predicted': predicted_time,
            'actual': actual_time_minutes,
            'error': actual_time_minutes - predicted_time,
            'scenario': trip['scenario'],
            'timestamp': trip['time']
        })
        
        print(f"✓ Feedback processed. Total trips logged: {len(self.trip_history)}")


def visualize_routes(G, routes, route_metrics, src_lat, src_lon, dst_lat, dst_lon, 
                    output_file: str = "route_map.html"):
    """Visualize routes with detailed metrics using Folium"""
    
    try:
        # Extract node coordinates directly from the graph
        center_lat = (src_lat + dst_lat) / 2
        center_lon = (src_lon + dst_lon) / 2
        
        colors = ["red", "blue", "green", "orange", "purple"]
        
        # Create base map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=13, 
                      tiles='OpenStreetMap')
        
        # Add routes
        for idx, (route, metrics) in enumerate(zip(routes, route_metrics)):
            # Extract coordinates directly from graph nodes
            route_coords = []
            for node in route:
                if node in G.nodes:
                    node_data = G.nodes[node]
                    lat = node_data.get('y', None)
                    lon = node_data.get('x', None)
                    if lat is not None and lon is not None:
                        route_coords.append([lat, lon])
            
            if len(route_coords) < 2:
                print(f"⚠ Route {idx+1} has insufficient coordinates, skipping...")
                continue
            
            # Create detailed tooltip
            tooltip = f"""
            <div style="font-family: Arial; font-size: 12px;">
                <b style="color: {colors[idx % len(colors)]};">Route {idx+1}</b><br>
                <hr style="margin: 5px 0;">
                📏 Distance: <b>{metrics['distance_km']:.2f} km</b><br>
                ⏱ Time: <b>{metrics['time_minutes']:.1f} min</b><br>
                💰 Cost: <b>₹{metrics['cost_rupees']:.2f}</b><br>
                ⛽ Fuel: <b>₹{metrics['fuel_rupees']:.2f}</b><br>
                📍 Nodes: <b>{metrics['num_nodes']}</b>
            </div>
            """
            
            popup_text = f"""
            <div style="font-family: Arial;">
                <h4 style="color: {colors[idx % len(colors)]};">Route {idx+1}</h4>
                <p><b>Time:</b> {metrics['time_minutes']:.1f} minutes</p>
                <p><b>Distance:</b> {metrics['distance_km']:.2f} km</p>
                <p><b>Total Cost:</b> ₹{metrics['cost_rupees']:.2f}</p>
            </div>
            """
            
            # Add polyline
            folium.PolyLine(
                locations=route_coords,
                color=colors[idx % len(colors)],
                weight=6,
                opacity=0.7,
                tooltip=tooltip,
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(m)
            
            print(f"✓ Added Route {idx+1} with {len(route_coords)} points")
        
        # Add start marker
        folium.Marker(
            [src_lat, src_lon], 
            tooltip="<b>Start Point</b>", 
            popup="<div style='font-family: Arial;'><h4>🚗 Start</h4><p>Begin your journey here</p></div>",
            icon=folium.Icon(color="green", icon="play", prefix='fa')
        ).add_to(m)
        
        # Add destination marker
        folium.Marker(
            [dst_lat, dst_lon], 
            tooltip="<b>Destination</b>", 
            popup="<div style='font-family: Arial;'><h4>🏁 Destination</h4><p>Your final destination</p></div>",
            icon=folium.Icon(color="red", icon="stop", prefix='fa')
        ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 200px; height: auto; 
                    background-color: white; z-index:9999; font-size:14px;
                    border:2px solid grey; border-radius: 5px; padding: 10px">
            <p style="margin: 0; font-weight: bold;">Route Legend</p>
            <hr style="margin: 5px 0;">
        '''
        
        for idx, (route, metrics) in enumerate(zip(routes, route_metrics)):
            legend_html += f'''
            <p style="margin: 5px 0;">
                <span style="background-color: {colors[idx % len(colors)]}; 
                             width: 20px; height: 3px; display: inline-block;"></span>
                Route {idx+1}: {metrics['time_minutes']:.1f}min
            </p>
            '''
        
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map
        m.save(output_file)
        print(f"💾 Map saved to: {output_file}")
        print(f"🗺  Open '{output_file}' in your browser to view the interactive map")
        
        return m
    
    except Exception as e:
        print(f"⚠ Error creating map: {e}")
        import traceback
        print("Full error traceback:")
        traceback.print_exc()
        return None


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Step 1: Define coordinates
    src_lat, src_lon = 12.934879, 77.537081
    dst_lat, dst_lon = 12.9779079, 77.5723936
    
    # Step 2: Get OSM data
    print("📡 Fetching OSM data...")
    center_lat = (src_lat + dst_lat) / 2
    center_lon = (src_lon + dst_lon) / 2
    bbox = ox.utils_geo.bbox_from_point((center_lat, center_lon), dist=3000)
    
    try:
        G_multi = ox.graph_from_bbox(bbox=bbox, network_type="drive", simplify=True)
        print(f"✓ Network: {len(G_multi.nodes)} nodes, {len(G_multi.edges)} edges")
    except Exception as e:
        print(f"❌ Error fetching OSM data: {e}")
        exit(1)
    
    # Step 3: Convert to DiGraph
    print("🔄 Converting to DiGraph...")
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
    
    print(f"✓ Converted to DiGraph: {len(G.nodes)} nodes, {len(G.edges)} edges")
    
    # Step 4: Initialize adaptive optimizer
    print("🤖 Initializing adaptive optimizer...")
    optimizer = AdaptiveRouteOptimizer(G)
    
    # Try to load previously learned model
    optimizer.edge_learner.load_model('learned_weights.pkl')
    
    # Step 5: Optimize routes for different scenarios
    scenarios = ['personal', 'aggregator', 'logistics']
    
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"🎯 Optimizing for scenario: {scenario.upper()}")
        print(f"{'='*60}")
        
        # Simulate different times of day
        test_time = datetime.now().replace(hour=18, minute=0)  # Rush hour
        
        routes, metrics = optimizer.optimize_route(
            src_lat, src_lon, dst_lat, dst_lon,
            scenario=scenario,
            current_time=test_time,
            K=4
        )
        
        if not routes:
            print(f"⚠ No routes found for scenario: {scenario}")
            continue
        
        # Print results
        print(f"\n📊 Found {len(routes)} alternative routes:")
        for i, m in enumerate(metrics, 1):
            print(f"\n🛣  Route {i}:")
            print(f"   📏 Distance: {m['distance_km']:.2f} km")
            print(f"   ⏱  Time: {m['time_minutes']:.1f} min")
            print(f"   💰 Cost: ₹{m['cost_rupees']:.2f}")
            print(f"   ⛽ Fuel: ₹{m['fuel_rupees']:.2f}")
        
        # Visualize
        map_file = f"route_map_{scenario}.html"
        visualize_routes(G, routes, metrics, src_lat, src_lon, dst_lat, dst_lon, 
                        map_file)
        
        # Simulate feedback (in real system, this comes from actual trip)
        print(f"\n🔄 Simulating feedback for learning...")
        selected_route = 0  # User selected first route
        actual_time = metrics[selected_route]['time_minutes'] * 1.15  # 15% slower than predicted
        
        print(f"   🎯 Selected: Route {selected_route + 1}")
        print(f"   ⏱  Predicted: {metrics[selected_route]['time_minutes']:.1f} min")
        print(f"   ⏱  Actual: {actual_time:.1f} min")
        print(f"   📉 Error: {(actual_time - metrics[selected_route]['time_minutes']):.1f} min")
        
        optimizer.process_trip_feedback(selected_route, actual_time)
    
    # Save learned model
    optimizer.edge_learner.save_model('learned_weights.pkl')
    
    print(f"\n{'='*60}")
    print("✅ Optimization complete!")
    print(f"📚 Total trips in history: {len(optimizer.trip_history)}")
    print("💾 Learned weights saved for future use")
    
    # Print learning statistics
    print(f"\n{'='*60}")
    print("📈 LEARNING STATISTICS")
    print(f"{'='*60}")
    stats = optimizer.edge_learner.get_learning_stats()
    if 'status' not in stats:
        print(f"Total trips learned from: {stats['num_trips']}")
        print(f"Mean Absolute Error: {stats['mae_minutes']:.2f} minutes")
        if stats['recent_5_mae_minutes']:
            print(f"Recent 5 trips MAE: {stats['recent_5_mae_minutes']:.2f} minutes")
    
    # Print learned weights for each scenario
    print(f"\n{'='*60}")
    print("🧠 LEARNED WEIGHT PARAMETERS")
    print(f"{'='*60}")
    print("Format: [Distance, Time, Cost, Fuel]\n")
    for scenario, theta in optimizer.edge_learner.theta.items():
        print(f"{scenario.capitalize():12} : {theta}")