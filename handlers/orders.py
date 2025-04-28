import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from models import db
from utils import format_order_details, log_error, MAIN_KEYBOARD

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def list_orders(update: Update, context: CallbackContext):
    """List all user orders"""
    try:
        user_id = update.effective_user.id
        
        # Get user orders
        orders = db.get_user_orders(user_id)
        
        if not orders:
            update.message.reply_text(
                "📋 Você ainda não realizou nenhum pedido.",
                reply_markup=MAIN_KEYBOARD
            )
            return
        
        # Create message and keyboard
        message = "📋 *Seus Pedidos:*\n\n"
        keyboard = []
        
        for order in orders:
            status_emoji = {
                "pendente": "⏳",
                "pago": "💰",
                "entregue": "✅",
                "cancelado": "❌"
            }.get(order.status, "❓")
            
            message += f"{status_emoji} Pedido #{order.id} - Status: {order.status.upper()}\n"
            keyboard.append([InlineKeyboardButton(f"Ver Pedido #{order.id}", callback_data=f"order_details_{order.id}")])
        
        update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        log_error(e, f"Error listing orders for user {update.effective_user.id}")
        update.message.reply_text(
            "❌ Ocorreu um erro ao listar seus pedidos. Por favor, tente novamente.",
            reply_markup=MAIN_KEYBOARD
        )

def order_details(update: Update, context: CallbackContext):
    """Show details for a specific order"""
    try:
        query = update.callback_query
        query.answer()
        
        # Extract order ID from callback data
        order_id = query.data.split("_")[2]
        
        # Get order
        order = db.get_order(order_id)
        if not order:
            query.edit_message_text(
                "❌ Pedido não encontrado. Por favor, tente novamente."
            )
            return
        
        # Verify this is the user's order
        if order.user_id != query.from_user.id:
            query.edit_message_text(
                "❌ Você não tem permissão para ver este pedido."
            )
            return
        
        # Format order details
        order_details_text = format_order_details(order, include_items=True)
        
        # Create keyboard based on order status
        keyboard = []
        
        if order.status == "pendente":
            keyboard.append([InlineKeyboardButton("🔍 Verificar Pagamento", callback_data=f"check_payment_{order.id}")])
        
        keyboard.append([InlineKeyboardButton("◀️ Voltar aos Pedidos", callback_data="back_to_orders")])
        
        query.edit_message_text(
            order_details_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        log_error(e, f"Error showing order details for user {update.callback_query.from_user.id}")
        update.callback_query.edit_message_text(
            "❌ Ocorreu um erro ao exibir os detalhes do pedido. Por favor, tente novamente."
        )

def check_payment_callback(update: Update, context: CallbackContext):
    """Handle check payment callback"""
    try:
        query = update.callback_query
        query.answer()
        
        if query.data == "back_to_orders":
            # Show user's orders again
            user_id = query.from_user.id
            orders = db.get_user_orders(user_id)
            
            if not orders:
                query.edit_message_text(
                    "📋 Você ainda não realizou nenhum pedido."
                )
                return
            
            # Create message and keyboard
            message = "📋 *Seus Pedidos:*\n\n"
            keyboard = []
            
            for order in orders:
                status_emoji = {
                    "pendente": "⏳",
                    "pago": "💰",
                    "entregue": "✅",
                    "cancelado": "❌"
                }.get(order.status, "❓")
                
                message += f"{status_emoji} Pedido #{order.id} - Status: {order.status.upper()}\n"
                keyboard.append([InlineKeyboardButton(f"Ver Pedido #{order.id}", callback_data=f"order_details_{order.id}")])
            
            query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
    except Exception as e:
        log_error(e, f"Error in check_payment_callback for user {update.callback_query.from_user.id}")
        update.callback_query.edit_message_text(
            "❌ Ocorreu um erro. Por favor, tente novamente."
        )