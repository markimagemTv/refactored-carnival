from typing import Dict, List, Optional, Any
import uuid

# In-memory database for simplicity
users = {}
carts = {}
orders = {}

class User:
    def __init__(self, id, nome, telefone):
        self.id = id
        self.nome = nome
        self.telefone = telefone
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone
        }

class CartItem:
    def __init__(self, name, price, details=None):
        self.name = name
        self.price = price
        self.details = details or {}
    
    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "details": self.details
        }

class Order:
    def __init__(self, id, user_id, items, status="pendente", payment_id=None):
        self.id = id
        self.user_id = user_id
        self.items = items
        self.status = status
        self.payment_id = payment_id
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "payment_id": self.payment_id,
            "items": [item.to_dict() for item in self.items]
        }

class DataStore:
    """Handle in-memory data persistence for users, carts, and orders"""
    
    def __init__(self):
        self.users = users
        self.carts = carts
        self.orders = orders
    
    # User methods
    def save_user(self, user_id, name, phone):
        """Save user information"""
        users[str(user_id)] = {"nome": name, "telefone": phone}
    
    def get_user(self, user_id):
        """Get user by ID"""
        user_data = users.get(str(user_id))
        if user_data:
            return User(
                id=int(user_id),
                nome=user_data["nome"],
                telefone=user_data["telefone"]
            )
        return None
    
    # Cart methods
    def add_to_cart(self, user_id, item):
        """Add item to user's cart"""
        if str(user_id) not in carts:
            carts[str(user_id)] = []
        
        if isinstance(item, dict):
            # Convert dict to CartItem if necessary
            cart_item = CartItem(
                name=item.get("name", ""),
                price=item.get("price", 0),
                details=item.get("details", {})
            )
            carts[str(user_id)].append(cart_item)
        else:
            carts[str(user_id)].append(item)
    
    def get_cart(self, user_id):
        """Get user's cart"""
        return carts.get(str(user_id), [])
    
    def clear_cart(self, user_id):
        """Clear user's cart"""
        carts[str(user_id)] = []
    
    # Order methods
    def create_order(self, user_id, cart_items, payment_id=None):
        """Create a new order"""
        order_id = str(uuid.uuid4())[:8]
        
        order = Order(
            id=order_id,
            user_id=user_id,
            items=cart_items,
            payment_id=payment_id
        )
        
        orders[order_id] = order
        return order
    
    def get_order(self, order_id):
        """Get order by ID"""
        return orders.get(order_id)
    
    def update_order_status(self, order_id, status, payment_id=None):
        """Update order status and optionally payment_id"""
        if order_id in orders:
            orders[order_id].status = status
            if payment_id:
                orders[order_id].payment_id = payment_id
            return True
        return False
    
    def get_user_orders(self, user_id):
        """Get all orders for a user"""
        user_orders = []
        for order_id, order in orders.items():
            if str(order.user_id) == str(user_id):
                user_orders.append(order)
        return user_orders

# Create global data store instance
db = DataStore()