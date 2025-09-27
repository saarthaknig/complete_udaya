# app.py - Simple Flask Application for Python 3.13
from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import json
import os
import math
import random
from datetime import datetime, timedelta
import sqlite3

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Simple database file
DB_FILE = 'agrismart.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            state TEXT NOT NULL,
            city TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create price_predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            crop_name TEXT NOT NULL,
            harvest_date DATE NOT NULL,
            state TEXT NOT NULL,
            city TEXT NOT NULL,
            predicted_price REAL NOT NULL,
            best_sell_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create crop_recommendations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crop_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            harvest_date DATE NOT NULL,
            state TEXT NOT NULL,
            city TEXT NOT NULL,
            recommended_crops TEXT NOT NULL,
            expected_profit REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Simple token generation (for demo purposes)
def create_token(user_id):
    """Create a simple token"""
    import time
    token_data = f"{user_id}:{int(time.time())}"
    return hashlib.md5(token_data.encode()).hexdigest()

def verify_token(token):
    """Verify token (simplified)"""
    # In production, use proper JWT verification
    return 1  # Return user_id for demo

STATES_CITIES = {
    'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Rajahmundry', 'Kadapa', 'Tirupati'],
    'Arunachal Pradesh': ['Itanagar', 'Naharlagun', 'Pasighat', 'Tezpur', 'Bomdila', 'Ziro'],
    'Assam': ['Guwahati', 'Silchar', 'Dibrugarh', 'Jorhat', 'Nagaon', 'Tinsukia', 'Tezpur', 'Bongaigaon'],
    'Bihar': ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Purnia', 'Darbhanga', 'Bihar Sharif', 'Arrah'],
    'Chhattisgarh': ['Raipur', 'Bhilai', 'Bilaspur', 'Korba', 'Durg', 'Rajnandgaon', 'Jagdalpur', 'Raigarh'],
    'Goa': ['Panaji', 'Margao', 'Vasco da Gama', 'Mapusa', 'Ponda', 'Bicholim'],
    'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar', 'Junagadh', 'Gandhinagar'],
    'Haryana': ['Gurugram', 'Faridabad', 'Panipat', 'Ambala', 'Karnal', 'Sonipat', 'Yamunanagar', 'Rohtak'],
    'Himachal Pradesh': ['Shimla', 'Dharamshala', 'Solan', 'Mandi', 'Kullu', 'Hamirpur', 'Una', 'Bilaspur'],
    'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Phusro', 'Hazaribagh', 'Giridih'],
    'Karnataka': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Gulbarga', 'Davanagere', 'Bellary'],
    'Kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Kollam', 'Thrissur', 'Alappuzha', 'Palakkad', 'Kannur'],
    'Madhya Pradesh': ['Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Ujjain', 'Sagar', 'Dewas', 'Satna'],
    'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad', 'Solapur', 'Amravati', 'Kolhapur'],
    'Manipur': ['Imphal', 'Bishnupur', 'Thoubal', 'Churachandpur', 'Kakching', 'Ukhrul'],
    'Meghalaya': ['Shillong', 'Tura', 'Jowai', 'Nongpoh', 'Baghmara', 'Williamnagar'],
    'Mizoram': ['Aizawl', 'Lunglei', 'Saiha', 'Champhai', 'Kolasib', 'Serchhip'],
    'Nagaland': ['Kohima', 'Dimapur', 'Mokokchung', 'Tuensang', 'Wokha', 'Mon'],
    'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Berhampur', 'Sambalpur', 'Puri', 'Balasore', 'Bhadrak'],
    'Punjab': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali', 'Pathankot', 'Hoshiarpur'],
    'Rajasthan': ['Jaipur', 'Jodhpur', 'Udaipur', 'Kota', 'Ajmer', 'Bikaner', 'Alwar', 'Bharatpur'],
    'Sikkim': ['Gangtok', 'Namchi', 'Gyalshing', 'Mangan', 'Rangpo', 'Jorethang'],
    'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Tiruchirappalli', 'Tirunelveli', 'Erode', 'Vellore'],
    'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar', 'Ramagundam', 'Khammam', 'Mahbubnagar', 'Nalgonda'],
    'Tripura': ['Agartala', 'Dharmanagar', 'Udaipur', 'Kailashahar', 'Belonia', 'Ambassa'],
    'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Varanasi', 'Meerut', 'Allahabad', 'Bareilly', 'Ghaziabad'],
    'Uttarakhand': ['Dehradun', 'Haridwar', 'Roorkee', 'Haldwani', 'Rudrapur', 'Kashipur', 'Rishikesh', 'Pithoragarh'],
    'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri', 'Bardhaman', 'Malda', 'Kharagpur'],
    'Andaman and Nicobar Islands': ['Port Blair', 'Bamboo Flat', 'Garacharma', 'Diglipur'],
    'Chandigarh': ['Chandigarh', 'Mani Majra', 'Dhanas', 'Maloya'],
    'Dadra and Nagar Haveli and Daman and Diu': ['Daman', 'Diu', 'Silvassa', 'Dadra'],
    'Delhi': ['New Delhi', 'Dwarka', 'Rohini', 'Janakpuri', 'Laxmi Nagar', 'Karol Bagh'],
    'Jammu and Kashmir': ['Srinagar', 'Jammu', 'Anantnag', 'Baramulla', 'Udhampur', 'Kathua'],
    'Ladakh': ['Leh', 'Kargil', 'Nubra', 'Zanskar'],
    'Lakshadweep': ['Kavaratti', 'Agatti', 'Minicoy', 'Amini'],
    'Puducherry': ['Puducherry', 'Karaikal', 'Mahe', 'Yanam']
}

# Price prediction logic
def predict_crop_price(crop_name, target_date, state=None):
    """Simple price prediction"""
    base_prices = {
        'Wheat': 2100, 'Rice': 2300, 'Maize': 1800, 
        'Cotton': 5500, 'Sugarcane': 2800, 'Soybean': 2400,
        'Mustard': 2200, 'Gram': 2000
    }
    
    base_price = base_prices.get(crop_name, 2000)
    
    # Add seasonal variation
    day_of_year = target_date.timetuple().tm_yday
    seasonal_factor = 1 + 0.1 * math.sin(2 * math.pi * day_of_year / 365.25)
    
    # Add market volatility
    market_factor = random.uniform(0.85, 1.15)
    
    # State-based variation
    state_multipliers = {
        'Punjab': 1.1, 'Haryana': 1.05, 'Uttar Pradesh': 1.0,
        'Madhya Pradesh': 0.95, 'Maharashtra': 1.08, 'Karnataka': 0.98
    }
    state_factor = state_multipliers.get(state, 1.0)
    
    final_price = base_price * seasonal_factor * market_factor * state_factor
    return max(final_price, 500)

def find_best_sell_date(crop_name, harvest_date, days_ahead=90):
    """Find optimal selling date"""
    best_price = predict_crop_price(crop_name, harvest_date)
    best_date = harvest_date
    
    for days in range(1, days_ahead + 1):
        check_date = harvest_date + timedelta(days=days)
        predicted_price = predict_crop_price(crop_name, check_date)
        
        if predicted_price > best_price:
            best_price = predicted_price
            best_date = check_date
    
    return best_date, best_price

# Crop recommendation logic
def get_crop_recommendations(harvest_date, state, city=None):
    """Get crop recommendations"""
    crop_data = {
        'Wheat': {
            'growing_months': [11, 12, 1, 2, 3, 4],
            'profit_per_acre': 25000,
            'growing_duration': 120,
            'suitable_states': ['Punjab', 'Haryana', 'Uttar Pradesh', 'Madhya Pradesh']
        },
        'Rice': {
            'growing_months': [6, 7, 8, 9, 10],
            'profit_per_acre': 30000,
            'growing_duration': 120,
            'suitable_states': ['Punjab', 'Haryana', 'Uttar Pradesh', 'West Bengal']
        },
        'Cotton': {
            'growing_months': [5, 6, 7, 8, 9, 10],
            'profit_per_acre': 45000,
            'growing_duration': 180,
            'suitable_states': ['Maharashtra', 'Gujarat', 'Karnataka']
        },
        'Sugarcane': {
            'growing_months': [1, 2, 3, 4, 10, 11, 12],
            'profit_per_acre': 55000,
            'growing_duration': 365,
            'suitable_states': ['Uttar Pradesh', 'Maharashtra', 'Karnataka']
        }
    }
    
    recommendations = []
    harvest_month = harvest_date.month
    
    for crop, data in crop_data.items():
        if state not in data['suitable_states']:
            continue
            
        planting_date = harvest_date - timedelta(days=data['growing_duration'])
        planting_month = planting_date.month
        
        if planting_month in data['growing_months']:
            market_factor = random.uniform(0.8, 1.2)
            expected_profit = data['profit_per_acre'] * market_factor
            
            recommendations.append({
                'crop': crop,
                'expected_profit': round(expected_profit, 2),
                'planting_date': planting_date.strftime('%Y-%m-%d'),
                'growing_duration': data['growing_duration'],
                'confidence': round(random.uniform(0.75, 0.95), 2)
            })
    
    recommendations.sort(key=lambda x: x['expected_profit'], reverse=True)
    return recommendations[:3]

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'AgriSmart API is running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/states', methods=['GET'])
def get_states():
    """Get list of all states"""
    return jsonify({
        'success': True,
        'data': list(STATES_CITIES.keys())
    })

@app.route('/api/cities/<state>', methods=['GET'])
def get_cities(state):
    """Get cities for a specific state"""
    cities = STATES_CITIES.get(state, [])
    return jsonify({
        'success': True,
        'data': cities
    })

@app.route('/api/signup', methods=['POST'])
def signup():
    """User registration"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'state', 'city']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        # Validate state and city
        if data['state'] not in STATES_CITIES:
            return jsonify({'success': False, 'message': 'Invalid state'}), 400
        
        if data['city'] not in STATES_CITIES[data['state']]:
            return jsonify({'success': False, 'message': 'Invalid city for selected state'}), 400
        
        # Check if user exists
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Create user
        password_hash = hash_password(data['password'])
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, state, city)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['name'], data['email'], password_hash, data['state'], data['city']))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create token
        access_token = create_token(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'access_token': access_token,
            'user': {
                'id': user_id,
                'name': data['name'],
                'email': data['email'],
                'state': data['state'],
                'city': data['city']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        # Find user
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, password_hash, state, city FROM users WHERE email = ?', (data['email'],))
        user = cursor.fetchone()
        conn.close()
        
        if not user or user[2] != hash_password(data['password']):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Create token
        access_token = create_token(user[0])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user[0],
                'name': user[1],
                'email': data['email'],
                'state': user[3],
                'city': user[4]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'}), 500

@app.route('/api/price-prediction', methods=['POST'])
def predict_price():
    """Get price prediction"""
    try:
        # Simple auth check
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': 'Authorization token required'}), 401
        
        user_id = verify_token(token)
        data = request.get_json()
        
        # Validate input
        required_fields = ['crop_name', 'harvest_date', 'state', 'city']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Parse date
        try:
            harvest_date = datetime.strptime(data['harvest_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get predictions
        crop_name = data['crop_name'].title()
        current_price = predict_crop_price(crop_name, harvest_date, data['state'])
        best_sell_date, best_price = find_best_sell_date(crop_name, harvest_date)
        
        # Calculate profit increase
        profit_increase = ((best_price - current_price) / current_price) * 100
        
        # Save to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO price_predictions 
            (user_id, crop_name, harvest_date, state, city, predicted_price, best_sell_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, crop_name, harvest_date, data['state'], data['city'], current_price, best_sell_date))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'crop_name': crop_name,
                'harvest_date': harvest_date.strftime('%Y-%m-%d'),
                'current_predicted_price': round(current_price, 2),
                'best_sell_date': best_sell_date.strftime('%Y-%m-%d'),
                'best_sell_price': round(best_price, 2),
                'potential_profit_increase': round(profit_increase, 1),
                'days_to_wait': (best_sell_date - harvest_date).days,
                'recommendation': f"Wait {(best_sell_date - harvest_date).days} days for {profit_increase:.1f}% better price" if profit_increase > 5 else "Sell now - prices may not improve significantly",
                'location': f"{data['city']}, {data['state']}"
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Price prediction failed: {str(e)}'}), 500

@app.route('/api/crop-recommendation', methods=['POST'])
def recommend_crops():
    """Get crop recommendations"""
    try:
        # Simple auth check
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': 'Authorization token required'}), 401
        
        user_id = verify_token(token)
        data = request.get_json()
        
        # Validate input
        required_fields = ['harvest_date', 'state', 'city']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Parse date
        try:
            harvest_date = datetime.strptime(data['harvest_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get recommendations
        recommendations = get_crop_recommendations(harvest_date, data['state'], data['city'])
        
        if not recommendations:
            return jsonify({
                'success': True,
                'data': {
                    'recommendations': [],
                    'message': 'No suitable crops found for the selected harvest date and location.'
                }
            })
        
        total_expected_profit = sum(rec['expected_profit'] for rec in recommendations)
        
        # Save to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO crop_recommendations 
            (user_id, harvest_date, state, city, recommended_crops, expected_profit)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, harvest_date, data['state'], data['city'], json.dumps(recommendations), total_expected_profit))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'harvest_date': harvest_date.strftime('%Y-%m-%d'),
                'location': f"{data['city']}, {data['state']}",
                'recommendations': recommendations,
                'total_expected_profit': round(total_expected_profit, 2),
                'summary': f"Top recommendation: {recommendations[0]['crop']} with expected profit of ₹{recommendations[0]['expected_profit']:,.2f} per acre",
                'planting_advice': f"Start planting by {recommendations[0]['planting_date']} for optimal harvest timing"
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Crop recommendation failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    print("Starting AgriSmart API server...")
    app.run(debug=True, host='0.0.0.0', port=5001)
    
