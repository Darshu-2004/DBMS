"""
Test the backend API endpoints
Run this to verify all endpoints are working
"""

import requests
import json
from datetime import date

BASE_URL = 'http://localhost:5000/api'

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_health():
    print_header("Testing Health Check")
    response = requests.get('http://localhost:5000/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_signup():
    print_header("Testing User Signup")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test@123",
        "full_name": "Test User",
        "phone_number": "9876543210"
    }
    response = requests.post(f'{BASE_URL}/auth/signup', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [201, 409]  # 409 if user already exists

def test_signin():
    print_header("Testing User Signin")
    data = {
        "username": "testuser",
        "password": "Test@123"
    }
    response = requests.post(f'{BASE_URL}/auth/signin', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()['token']
    return None

def test_admin_signin():
    print_header("Testing Admin Signin")
    data = {
        "username": "admin",
        "password": "Admin@123"
    }
    response = requests.post(f'{BASE_URL}/auth/signin', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()['token']
    return None

def test_route_search(token):
    print_header("Testing Route Search")
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        "source": "Koramangala",
        "destination": "MG Road",
        "transport_mode": "public",
        "public_mode": "metro",
        "preference_type": "time"
    }
    response = requests.post(f'{BASE_URL}/routes/search', json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_create_booking(token):
    print_header("Testing Booking Creation")
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        "booking_type": "metro",
        "source": "Koramangala",
        "destination": "MG Road",
        "journey_date": str(date.today()),
        "journey_time": "10:00:00",
        "passenger_count": 1,
        "fare_amount": 40.00
    }
    response = requests.post(f'{BASE_URL}/bookings/create', json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201

def test_admin_dashboard(admin_token):
    print_header("Testing Admin Dashboard")
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = requests.get(f'{BASE_URL}/admin/dashboard', headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Dashboard loaded successfully!")
        print(f"  - Transport Modes: {len(data['dashboard']['transport_modes'])} entries")
        print(f"  - Popular Routes: {len(data['dashboard']['popular_routes'])} entries")
        print(f"  - User Activity: {len(data['dashboard']['user_activity'])} users")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def run_all_tests():
    print("\n" + "🚀"*30)
    print("  MULTI-MODAL TRANSPORT SYSTEM - API TESTS")
    print("🚀"*30)
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health()))
    
    # Test 2: User Signup
    results.append(("User Signup", test_signup()))
    
    # Test 3: User Signin
    user_token = test_signin()
    results.append(("User Signin", user_token is not None))
    
    if user_token:
        # Test 4: Route Search
        results.append(("Route Search", test_route_search(user_token)))
        
        # Test 5: Create Booking
        results.append(("Create Booking", test_create_booking(user_token)))
    
    # Test 6: Admin Signin
    admin_token = test_admin_signin()
    results.append(("Admin Signin", admin_token is not None))
    
    if admin_token:
        # Test 7: Admin Dashboard
        results.append(("Admin Dashboard", test_admin_dashboard(admin_token)))
    
    # Print Results
    print_header("TEST RESULTS SUMMARY")
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("="*60 + "\n")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Your application is working perfectly!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server!")
        print("Make sure the backend is running on http://localhost:5000")
        print("\nTo start the backend:")
        print("  cd backend")
        print("  python app.py")
