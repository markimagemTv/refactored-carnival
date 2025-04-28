import logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from config import PRODUCT_CATALOG, DISCOUNT_THRESHOLD, DISCOUNT_PERCENTAGE

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Main keyboard for regular operations
MAIN_KEYBOARD = ReplyKeyboardMarkup([
    ["🛒 Ver Carrinho", "🛍️ Produtos"],
    ["📋 Meus Pedidos", "❓ Ajuda"]
], resize_keyboard=True)

# Admin keyboard with additional options
ADMIN_KEYBOARD = ReplyKeyboardMarkup([
    ["🛒 Ver Carrinho", "🛍️ Produtos"],
    ["📋 Meus Pedidos", "🛠️ Admin"],
    ["❓ Ajuda"]
], resize_keyboard=True)

def get_cart_total(cart_items):
    """Calculate total price of items in cart"""
    total = 0
    for item in cart_items:
        total += item.price
    return total

def apply_discount(product_price, quantity, has_discount=False):
    """Apply discount for credit purchases if applicable"""
    total = product_price * quantity
    # Aplicar desconto de 5% apenas para compras de 11+ créditos
    # e apenas para produtos que não sejam 'UPPER PLAY' (indicado pelo has_discount)
    if has_discount and quantity >= DISCOUNT_THRESHOLD:
        return total * DISCOUNT_PERCENTAGE
    return total

def format_cart_message(cart_items):
    """Format cart items for display"""
    if not cart_items:
        return "Seu carrinho está vazio."
    
    total = get_cart_total(cart_items)
    
    message = "🛒 *Seu Carrinho:*\n\n"
    
    for i, item in enumerate(cart_items, 1):
        item_details = ""
        if hasattr(item, 'details') and item.details:
            item_details = "\n".join([f"  • {k}: {v}" for k, v in item.details.items()])
            item_details = f"\n{item_details}"
        
        message += f"{i}. {item.name} - R${item.price:.2f}{item_details}\n\n"
    
    message += f"\n💰 *Total:* R${total:.2f}"
    return message

def create_categories_keyboard():
    """Create inline keyboard for product categories"""
    keyboard = []
    
    for category in PRODUCT_CATALOG.keys():
        keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])
    
    return InlineKeyboardMarkup(keyboard)

def create_products_keyboard(products):
    """Create inline keyboard for products"""
    keyboard = []
    
    for i, product in enumerate(products):
        price = f"R${product['price']:.2f}"
        keyboard.append([
            InlineKeyboardButton(f"{product['name']} - {price}", callback_data=f"product_{i}")
        ])
    
    # Add back button
    keyboard.append([InlineKeyboardButton("◀️ Voltar", callback_data="back_to_categories")])
    
    return InlineKeyboardMarkup(keyboard)

def create_credits_keyboard():
    """Create keyboard for credit quantities"""
    keyboard = []
    
    quantities = [10, 20, 50, 100]
    row = []
    
    for i, qty in enumerate(quantities):
        row.append(InlineKeyboardButton(str(qty), callback_data=f"qty_{qty}"))
        
        # 2 buttons per row
        if (i + 1) % 2 == 0 or i == len(quantities) - 1:
            keyboard.append(row)
            row = []
    
    # Add back button
    keyboard.append([InlineKeyboardButton("◀️ Voltar", callback_data="back_to_products")])
    
    return InlineKeyboardMarkup(keyboard)

def format_order_details(order, include_items=True):
    """Format order details for display"""
    status_emoji = {
        "pendente": "⏳",
        "pago": "💰",
        "entregue": "✅",
        "cancelado": "❌"
    }
    
    status_display = f"{status_emoji.get(order.status, '❓')} {order.status.upper()}"
    
    message = (
        f"🧾 *Pedido #{order.id}*\n"
        f"📊 *Status:* {status_display}\n"
    )
    
    if order.payment_id:
        message += f"💳 *Pagamento ID:* {order.payment_id}\n"
    
    if include_items and order.items:
        message += "\n📦 *Itens:*\n"
        
        total = 0
        for i, item in enumerate(order.items, 1):
            total += item.price
            
            item_details = ""
            if hasattr(item, 'details') and item.details:
                item_details = "\n".join([f"  • {k}: {v}" for k, v in item.details.items()])
                item_details = f"\n{item_details}"
            
            message += f"{i}. {item.name} - R${item.price:.2f}{item_details}\n"
        
        message += f"\n💰 *Total:* R${total:.2f}"
    
    return message

def log_error(error, context=None):
    """Log errors with context"""
    context_text = f" - {context}" if context else ""
    logger.error(f"ERROR{context_text}: {error}")