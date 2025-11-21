"""Test admin revenue API endpoints"""
import requests
from datetime import datetime

API_URL = 'http://localhost:5000'

# You'll need to login first to get a token
# Replace with your admin credentials
LOGIN_DATA = {
    'username': 'admin',
    'password': 'Admin@123'
}

print("🔐 Logging in as admin...")
response = requests.post(f'{API_URL}/api/auth/signin', json=LOGIN_DATA)
result = response.json()

if result.get('success'):
    token = result['token']
    print(f"✅ Login successful! Token: {token[:20]}...")
    
    # Test daily revenue endpoint
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n📊 Testing daily revenue API for {today}...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_URL}/api/admin/revenue/daily?date={today}', headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ API Response:")
        print(f"   Success: {data.get('success')}")
        print(f"   Date: {data.get('date')}")
        print(f"   Total Revenue: ₹{data.get('total_revenue', 0)}")
        print(f"   Total Bookings: {data.get('total_bookings', 0)}")
        print(f"\n   KSRTC:")
        print(f"      Revenue: ₹{data.get('ksrtc', {}).get('total_revenue', 0)}")
        print(f"      Bookings: {data.get('ksrtc', {}).get('confirmed_bookings', 0)}")
        print(f"\n   Train:")
        print(f"      Revenue: ₹{data.get('train', {}).get('total_revenue', 0)}")
        print(f"      Bookings: {data.get('train', {}).get('confirmed_bookings', 0)}")
        print(f"\n   Flight:")
        print(f"      Revenue: ₹{data.get('flight', {}).get('total_revenue', 0)}")
        print(f"      Bookings: {data.get('flight', {}).get('confirmed_bookings', 0)}")
        print(f"\n   Top Users: {len(data.get('top_users', []))} users")
    else:
        print(f"❌ Error: {response.text}")
else:
    print(f"❌ Login failed: {result.get('message')}")
