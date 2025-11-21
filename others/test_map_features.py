"""
Test script for map and navigation features
"""
import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_route_search_with_coordinates():
    """Test route search returns coordinates for map visualization"""
    print("\n=== Testing Route Search with Coordinates ===")
    
    # First, try to sign up
    signup_data = {
        'username': 'testuser',
        'password': 'Test@123',
        'email': 'test@example.com',
        'full_name': 'Test User'
    }
    
    # Try signup (may fail if user exists, that's OK)
    response = requests.post(f'{BASE_URL}/api/auth/signup', json=signup_data)
    if response.status_code == 201:
        print("✅ New user created")
    
    # Now sign in
    signin_data = {
        'username': 'testuser',
        'password': 'Test@123'
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/signin', json=signin_data)
    print(f"Signin Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Failed to sign in: {response.text}")
        return None, None
    
    token = response.json().get('token')
    print("✅ Signed in successfully")
    
    # Search for routes
    search_data = {
        'source': 'Koramangala',
        'destination': 'MG Road',
        'transport_mode': 'private',
        'private_mode': 'bike'
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(f'{BASE_URL}/api/routes/search', json=search_data, headers=headers)
    print(f"\nRoute Search Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('routes'):
            route = data['routes'][0]
            print(f"✅ Route found: {route.get('mode', 'N/A')}")
            print(f"   Route: {route.get('route_name', route.get('source', 'N/A'))} to {route.get('destination', 'N/A')}")
            print(f"   Distance: {route.get('distance_km', route.get('distance', 'N/A'))}")
            print(f"   Duration: {route.get('duration_mins', route.get('duration', 'N/A'))}")
            print(f"   Speed: {route.get('speed_kmh', 'N/A')} km/h")
            print(f"   Source Coords: {route.get('source_coords', 'N/A')}")
            print(f"   Dest Coords: {route.get('dest_coords', 'N/A')}")
            
            if route.get('source_coords') and route.get('dest_coords'):
                print("✅ Coordinates available for map visualization")
                return token, route
            else:
                print("❌ Coordinates missing")
                print(f"   Full route data: {json.dumps(route, indent=2)}")
        else:
            print("❌ No routes returned")
    else:
        print(f"❌ Route search failed: {response.text}")
    
    return None, None

def test_navigation_tracking(token, route):
    """Test navigation start, update, and stop"""
    if not token or not route:
        print("\n⚠️  Skipping navigation test - no token or route")
        return
    
    print("\n=== Testing Navigation Tracking ===")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Start navigation
    start_data = {
        'booking_id': 0,
        'vehicle_number': route.get('mode', 'BIKE').upper(),
        'source': 'Koramangala',
        'source_lat': route['source_coords']['lat'],
        'source_lng': route['source_coords']['lng'],
        'total_distance': route.get('distance_km', route.get('distance', 5))
    }
    
    response = requests.post(f'{BASE_URL}/api/navigation/start', json=start_data, headers=headers)
    print(f"Start Navigation Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        tracking_id = data.get('tracking_id')
        print(f"✅ Navigation started - Tracking ID: {tracking_id}")
        
        # Simulate position updates
        print("\n📍 Simulating position updates...")
        for i in range(3):
            update_data = {
                'tracking_id': tracking_id,
                'lat': route['source_coords']['lat'] + (i * 0.001),
                'lng': route['source_coords']['lng'] + (i * 0.001),
                'distance_remaining': (route.get('distance_km', route.get('distance', 5)) if isinstance(route.get('distance_km', route.get('distance', 5)), (int, float)) else 5) - (i * 0.5),
                'location': f"Position {i+1}"
            }
            
            response = requests.post(f'{BASE_URL}/api/navigation/update', json=update_data, headers=headers)
            if response.status_code == 200:
                print(f"   ✅ Update {i+1}: Position updated successfully")
            else:
                print(f"   ❌ Update {i+1} failed")
            
            time.sleep(0.5)
        
        # Stop navigation
        stop_data = {'tracking_id': tracking_id}
        response = requests.post(f'{BASE_URL}/api/navigation/stop', json=stop_data, headers=headers)
        
        if response.status_code == 200:
            print("✅ Navigation stopped successfully")
        else:
            print(f"❌ Failed to stop navigation: {response.text}")
    else:
        print(f"❌ Failed to start navigation: {response.text}")

def main():
    print("=" * 60)
    print("TESTING MAP AND NAVIGATION FEATURES")
    print("=" * 60)
    
    # Test route search with coordinates
    token, route = test_route_search_with_coordinates()
    
    # Test navigation tracking
    if token and route:
        test_navigation_tracking(token, route)
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)
    print("\n✅ Ready to test in browser!")
    print("1. Open http://localhost:5000/index.html")
    print("2. Sign in with username: darshith, password: Darshu@2004")
    print("3. Search for a route (e.g., Koramangala to MG Road)")
    print("4. Click '📍 View on Map' button")
    print("5. Click 'Start Navigation' to see emoji movement")
    print("6. Watch the emoji move along the route with live tracking!")

if __name__ == '__main__':
    main()
