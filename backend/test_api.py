# test_api.py - API Testing Script
import requests
import json
from datetime import datetime, timedelta

# Base URL for your API
BASE_URL = "http://localhost:5000/api"

def test_api():
    """Test all API endpoints"""
    print("🧪 Testing AgriSmart API...")
    
    # Test health check
    print("\n1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test states endpoint
    print("\n2. Testing States Endpoint...")
    response = requests.get(f"{BASE_URL}/states")
    print(f"Status: {response.status_code}")
    states_data = response.json()
    print(f"States available: {len(states_data['data'])}")
    
    # Test cities endpoint
    print("\n3. Testing Cities Endpoint...")
    response = requests.get(f"{BASE_URL}/cities/Punjab")
    print(f"Status: {response.status_code}")
    cities_data = response.json()
    print(f"Cities in Punjab: {cities_data['data']}")
    
    # Test user registration
    print("\n4. Testing User Registration...")
    signup_data = {
        "name": "Test Farmer",
        "email": "testfarmer@example.com",
        "password": "testpass123",
        "state": "Punjab",
        "city": "Ludhiana"
    }
    response = requests.post(f"{BASE_URL}/signup", json=signup_data)
    print(f"Status: {response.status_code}")
    signup_result = response.json()
    print(f"Registration: {signup_result['success']}")
    
    # Store token for authenticated requests
    token = None
    if signup_result['success']:
        token = signup_result['access_token']
        print(f"Token received: {token[:20]}...")
    
    # Test login (in case user already exists)
    if not token:
        print("\n5. Testing User Login...")
        login_data = {
            "email": "testfarmer@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Status: {response.status_code}")
        login_result = response.json()
        if login_result['success']:
            token = login_result['access_token']
            print(f"Login successful, token: {token[:20]}...")
    
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Headers for authenticated requests
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test price prediction
    print("\n6. Testing Price Prediction...")
    harvest_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    price_data = {
        "crop_name": "Wheat",
        "harvest_date": harvest_date,
        "state": "Punjab",
        "city": "Ludhiana"
    }
    response = requests.post(f"{BASE_URL}/price-prediction", json=price_data, headers=headers)
    print(f"Status: {response.status_code}")
    price_result = response.json()
    if price_result['success']:
        data = price_result['data']
        print(f"Crop: {data['crop_name']}")
        print(f"Current Price: ₹{data['current_predicted_price']}")
        print(f"Best Sell Price: ₹{data['best_sell_price']}")
        print(f"Best Sell Date: {data['best_sell_date']}")
        print(f"Profit Increase: {data['potential_profit_increase']}%")
    
    # Test crop recommendation
    print("\n7. Testing Crop Recommendation...")
    harvest_date = (datetime.now() + timedelta(days=120)).strftime('%Y-%m-%d')
    crop_rec_data = {
        "harvest_date": harvest_date,
        "state": "Punjab",
        "city": "Ludhiana"
    }
    response = requests.post(f"{BASE_URL}/crop-recommendation", json=crop_rec_data, headers=headers)
    print(f"Status: {response.status_code}")
    crop_result = response.json()
    if crop_result['success']:
        data = crop_result['data']
        print(f"Harvest Date: {data['harvest_date']}")
        print(f"Location: {data['location']}")
        print(f"Recommendations: {len(data['recommendations'])}")
        for i, rec in enumerate(data['recommendations'], 1):
            print(f"  {i}. {rec['crop']} - Expected Profit: ₹{rec['expected_profit']:,.2f}")
    
    # Test user profile
    print("\n8. Testing User Profile...")
    response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
    print(f"Status: {response.status_code}")
    profile_result = response.json()
    if profile_result['success']:
        user_data = profile_result['data']['user']
        stats = profile_result['data']['statistics']
        print(f"User: {user_data['name']} ({user_data['email']})")
        print(f"Location: {user_data['city']}, {user_data['state']}")
        print(f"Total Queries: {stats['total_queries']}")
    
    print("\n✅ API Testing Complete!")

if __name__ == "__main__":
    test_api()