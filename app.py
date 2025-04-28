from flask import Flask, render_template, jsonify
import os
from models import DataStore
from config import ADMIN_ID

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "secret-key")

# Get data store
data_store = DataStore()

@app.route('/')
def index():
    """Admin dashboard homepage"""
    return render_template('index.html')

@app.route('/api/orders')
def get_orders():
    """Get all orders as JSON"""
    orders = []
    for order_id in data_store.orders:
        order = data_store.orders[order_id]
        user_id = order.user_id
        user = data_store.get_user(user_id)
        
        order_data = order.to_dict()
        if user:
            order_data["user"] = user.to_dict()
        
        orders.append(order_data)
    
    return jsonify({"orders": orders})

@app.route('/api/users')
def get_users():
    """Get all users as JSON"""
    users = []
    for user_id in data_store.users:
        user = data_store.users[user_id]
        users.append(user.to_dict())
    
    return jsonify({"users": users})

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)