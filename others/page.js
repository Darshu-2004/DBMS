'use client';

import { useState, useEffect } from 'react';
import { MapPin, Navigation, Clock, DollarSign, Fuel, AlertCircle, Search, Play, Square } from 'lucide-react';

export default function RouteOptimizer() {
  const [source, setSource] = useState({ lat: '', lon: '', name: '' });
  const [destination, setDestination] = useState({ lat: '', lon: '', name: '' });
  const [sourceQuery, setSourceQuery] = useState('');
  const [destQuery, setDestQuery] = useState('');
  const [sourceResults, setSourceResults] = useState([]);
  const [destResults, setDestResults] = useState([]);
  const [showSourceDropdown, setShowSourceDropdown] = useState(false);
  const [showDestDropdown, setShowDestDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [routeData, setRouteData] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [navigating, setNavigating] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [navigationMapHtml, setNavigationMapHtml] = useState(null);

  // Search location
  const searchLocation = async (query, isSource) => {
    if (query.length < 3) {
      if (isSource) setSourceResults([]);
      else setDestResults([]);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/search-location?query=${encodeURIComponent(query)}`);
      const data = await response.json();
      
      if (isSource) {
        setSourceResults(data.results || []);
        setShowSourceDropdown(true);
      } else {
        setDestResults(data.results || []);
        setShowDestDropdown(true);
      }
    } catch (err) {
      console.error('Location search error:', err);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      if (sourceQuery) searchLocation(sourceQuery, true);
    }, 300);
    return () => clearTimeout(timer);
  }, [sourceQuery]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (destQuery) searchLocation(destQuery, false);
    }, 300);
    return () => clearTimeout(timer);
  }, [destQuery]);

  const selectLocation = (result, isSource) => {
    if (isSource) {
      setSource({ lat: result.lat.toString(), lon: result.lon.toString(), name: result.display_name });
      setSourceQuery(result.display_name);
      setShowSourceDropdown(false);
    } else {
      setDestination({ lat: result.lat.toString(), lon: result.lon.toString(), name: result.display_name });
      setDestQuery(result.display_name);
      setShowDestDropdown(false);
    }
  };

  const handleOptimize = async () => {
    if (!source.lat || !source.lon || !destination.lat || !destination.lon) {
      setError('Please select valid locations for both source and destination');
      return;
    }

    setLoading(true);
    setError('');
    setRouteData(null);

    try {
      const response = await fetch('http://localhost:8000/api/optimize-route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          src_lat: parseFloat(source.lat),
          src_lon: parseFloat(source.lon),
          dst_lat: parseFloat(destination.lat),
          dst_lon: parseFloat(destination.lon),
          scenario: 'personal'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to optimize route');
      }

      const data = await response.json();
      setRouteData(data);
    } catch (err) {
      setError(err.message || 'Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  };

  const useCurrentLocation = (isSource) => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude.toString();
        const lon = position.coords.longitude.toString();
        
        if (isSource) {
          setSource({ lat, lon, name: `Current Location` });
          setSourceQuery(`Current Location (${lat.substring(0, 8)}, ${lon.substring(0, 8)})`);
        } else {
          setDestination({ lat, lon, name: `Current Location` });
          setDestQuery(`Current Location (${lat.substring(0, 8)}, ${lon.substring(0, 8)})`);
        }
      },
      (error) => {
        let errorMessage = 'Unable to get location: ';
        switch(error.code) {
          case error.PERMISSION_DENIED:
            errorMessage += 'Permission denied';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage += 'Location unavailable';
            break;
          case error.TIMEOUT:
            errorMessage += 'Request timeout';
            break;
          default:
            errorMessage += 'Unknown error';
        }
        setError(errorMessage);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  const startNavigation = async (routeIdx) => {
    try {
      setLoading(true);
      setSelectedRoute(routeIdx);
      
      const selectedRouteNodes = routeData.routes[routeIdx];
      
      const response = await fetch('http://localhost:8000/api/start-navigation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'user_' + Date.now(),
          route_id: routeIdx,
          selected_route: selectedRouteNodes,
          src_lat: parseFloat(source.lat),
          src_lon: parseFloat(source.lon),
          dst_lat: parseFloat(destination.lat),
          dst_lon: parseFloat(destination.lon)
        })
      });

      const data = await response.json();
      setSessionId(data.session_id);
      setNavigationMapHtml(data.map_html);
      setNavigating(true);
      setLoading(false);
      
    } catch (err) {
      console.error('Start navigation error:', err);
      setError('Failed to start navigation: ' + err.message);
      setLoading(false);
    }
  };

  const endNavigation = () => {
    setNavigating(false);
    setSessionId(null);
    setSelectedRoute(null);
    setNavigationMapHtml(null);
  };

  // Navigation View
  if (navigating && navigationMapHtml) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-gradient-to-r from-green-600 to-blue-600 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white flex items-center">
                  <Navigation className="w-6 h-6 mr-2" />
                  Navigating Route {selectedRoute + 1}
                </h1>
                <p className="text-green-100 text-sm mt-1">🚗 Live navigation with real-time traffic</p>
              </div>
              <button
                onClick={endNavigation}
                className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center font-semibold shadow-lg"
              >
                <Square className="w-4 h-4 mr-2" />
                End Navigation
              </button>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 py-6">
          {/* Route Info Card */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Clock className="w-6 h-6 mx-auto mb-2 text-blue-600" />
                <p className="text-sm text-gray-600">Time</p>
                <p className="text-xl font-bold text-gray-900">
                  {routeData.metrics[selectedRoute].time_minutes.toFixed(0)} min
                </p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Navigation className="w-6 h-6 mx-auto mb-2 text-green-600" />
                <p className="text-sm text-gray-600">Distance</p>
                <p className="text-xl font-bold text-gray-900">
                  {routeData.metrics[selectedRoute].distance_km.toFixed(1)} km
                </p>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <DollarSign className="w-6 h-6 mx-auto mb-2 text-yellow-600" />
                <p className="text-sm text-gray-600">Cost</p>
                <p className="text-xl font-bold text-gray-900">
                  ₹{routeData.metrics[selectedRoute].cost_rupees.toFixed(0)}
                </p>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <AlertCircle className="w-6 h-6 mx-auto mb-2 text-red-600" />
                <p className="text-sm text-gray-600">Incidents</p>
                <p className="text-xl font-bold text-gray-900">
                  {routeData.incidents[selectedRoute].length}
                </p>
              </div>
            </div>
          </div>

          {/* Map */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4">
              <h2 className="text-xl font-semibold text-white flex items-center">
                🗺️ Live Navigation Map
                <span className="ml-auto text-sm bg-green-500 px-3 py-1 rounded-full">Active</span>
              </h2>
            </div>
            <div className="w-full h-[650px]">
              <iframe
                srcDoc={navigationMapHtml}
                className="w-full h-full"
                title="Navigation Map"
              />
            </div>
          </div>

          {/* Instructions */}
          <div className="mt-6 bg-blue-50 border-l-4 border-blue-600 rounded-lg p-4">
            <p className="text-sm text-gray-700">
              <strong>🚗 Navigation Active:</strong> Watch the car emoji move along your route at realistic speeds. 
              Colors indicate traffic conditions. The car will reach your destination in the predicted time shown above.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Results Page
  if (routeData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">
                🛣️ Route Options
              </h1>
              <button
                onClick={() => {
                  setRouteData(null);
                  setSelectedRoute(null);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                New Search
              </button>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {routeData.metrics && routeData.metrics.map((metric, idx) => (
              <div 
                key={idx} 
                className="bg-white rounded-lg shadow-md p-4 border-l-4 border-blue-500 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-lg text-gray-800">Route {idx + 1}</h3>
                  <button
                    onClick={() => startNavigation(idx)}
                    disabled={loading}
                    className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 flex items-center disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                  >
                    <Play className="w-4 h-4 mr-1" />
                    Start
                  </button>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center text-sm">
                    <Navigation className="w-4 h-4 mr-2 text-gray-600" />
                    <span className="text-gray-600">Distance:</span>
                    <span className="ml-auto font-semibold">{metric.distance_km.toFixed(2)} km</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <Clock className="w-4 h-4 mr-2 text-gray-600" />
                    <span className="text-gray-600">Time:</span>
                    <span className="ml-auto font-semibold">{metric.time_minutes.toFixed(1)} min</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <DollarSign className="w-4 h-4 mr-2 text-gray-600" />
                    <span className="text-gray-600">Cost:</span>
                    <span className="ml-auto font-semibold">₹{metric.cost_rupees.toFixed(2)}</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <Fuel className="w-4 h-4 mr-2 text-gray-600" />
                    <span className="text-gray-600">Fuel:</span>
                    <span className="ml-auto font-semibold">₹{metric.fuel_rupees.toFixed(2)}</span>
                  </div>
                </div>
                {routeData.incidents && routeData.incidents[idx] && routeData.incidents[idx].length > 0 && (
                  <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm font-semibold text-red-700 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {routeData.incidents[idx].length} Traffic Incident{routeData.incidents[idx].length > 1 ? 's' : ''}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              🗺️ All Routes Preview
            </h2>
            <div className="w-full h-[600px] border rounded-lg overflow-hidden">
              <iframe
                srcDoc={routeData.map_html}
                className="w-full h-full"
                title="Route Map"
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Input Page
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              🚗 Smart Route Navigator
            </h1>
            <p className="text-gray-600">
              Real-time traffic-aware routing with live navigation
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8">
            {error && (
              <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                  <p className="text-red-700">{error}</p>
                </div>
              </div>
            )}

            <div className="mb-6 relative">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <MapPin className="w-4 h-4 mr-2 text-green-600" />
                Source Location
              </label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search for a location..."
                  value={sourceQuery}
                  onChange={(e) => setSourceQuery(e.target.value)}
                  onFocus={() => sourceResults.length > 0 && setShowSourceDropdown(true)}
                  className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                />
                <Search className="absolute right-3 top-3.5 w-5 h-5 text-gray-400" />
              </div>
              
              {showSourceDropdown && sourceResults.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {sourceResults.map((result, idx) => (
                    <div
                      key={idx}
                      onClick={() => selectLocation(result, true)}
                      className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b last:border-b-0"
                    >
                      <div className="flex items-start">
                        <MapPin className="w-4 h-4 mr-2 text-blue-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">{result.display_name}</p>
                          <p className="text-xs text-gray-500">{result.type}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <button
                onClick={() => useCurrentLocation(true)}
                className="mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                📍 Use Current Location
              </button>
            </div>

            <div className="mb-6 relative">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <MapPin className="w-4 h-4 mr-2 text-red-600" />
                Destination Location
              </label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search for a location..."
                  value={destQuery}
                  onChange={(e) => setDestQuery(e.target.value)}
                  onFocus={() => destResults.length > 0 && setShowDestDropdown(true)}
                  className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                />
                <Search className="absolute right-3 top-3.5 w-5 h-5 text-gray-400" />
              </div>
              
              {showDestDropdown && destResults.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {destResults.map((result, idx) => (
                    <div
                      key={idx}
                      onClick={() => selectLocation(result, false)}
                      className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b last:border-b-0"
                    >
                      <div className="flex items-start">
                        <MapPin className="w-4 h-4 mr-2 text-red-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">{result.display_name}</p>
                          <p className="text-xs text-gray-500">{result.type}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <button
                onClick={() => useCurrentLocation(false)}
                className="mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                📍 Use Current Location
              </button>
            </div>

            <button
              onClick={handleOptimize}
              disabled={loading}
              className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Finding Best Routes...
                </span>
              ) : (
                '🚀 Find Traffic-Aware Routes'
              )}
            </button>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-700">
                <strong>💡 Features:</strong> Select a route to see ONLY that route with a moving car emoji. 
                Traffic colors stretch along the road based on incident length. Car moves at realistic speeds matching traffic conditions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}