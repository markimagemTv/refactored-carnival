import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config import ADMIN_ID
from models import User, Order
from utils import format_order_details

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def notify_admin_new_order(context: CallbackContext, order, user):
    """Notify admin about new order"""
    try:
        # Format order details
        order_details = format_order_details(order, include_items=True)
        
        # Create message with user details
        admin_message = (
            f"🔔 *NOVA VENDA CONFIRMADA!* 🔔\n\n"
            f"👤 *Cliente:* {user.nome}\n"
            f"📱 *Telefone:* {user.telefone}\n\n"
            f"{order_details}\n\n"
            f"✅ Pagamento confirmado e processado"
        )
        
        # Add buttons for order management
        keyboard = [
            [InlineKeyboardButton("✅ Marcar como Entregue", callback_data=f"mark_delivered_{order.id}")],
            [InlineKeyboardButton("❌ Cancelar Pedido", callback_data=f"cancel_order_{order.id}")]
        ]
        
        # Send message to admin
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        logger.info(f"Admin notified about new order {order.id}")
        
    except Exception as e:
        logger.error(f"Error notifying admin about order {order.id}: {e}")

def mark_as_delivered(update: Update, context: CallbackContext):
    """Mark order as delivered (admin only)"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Verify admin
    if str(user_id) != ADMIN_ID:
        query.answer("Você não tem permissão para esta ação", show_alert=True)
        return
    
    # Extract order ID from callback data
    order_id = query.data.split('_')[2]
    
    # Update order status
    from models import db
    success = db.update_order_status(order_id, "entregue")
    
    if success:
        # Get updated order
        order = db.get_order(order_id)
        if not order:
            query.answer("Pedido não encontrado", show_alert=True)
            return
            
        # Get user info
        user = db.get_user(order.user_id)
        if not user:
            query.answer("Usuário não encontrado", show_alert=True)
            return
            
        # Notify admin
        query.answer("Pedido marcado como entregue!", show_alert=True)
        
        # Update admin message
        order_details = format_order_details(order, include_items=True)
        admin_message = (
            f"📦 *PEDIDO ENTREGUE* 📦\n\n"
            f"👤 *Cliente:* {user.nome}\n"
            f"📱 *Telefone:* {user.telefone}\n\n"
            f"{order_details}"
        )
        
        query.edit_message_text(
            text=admin_message,
            parse_mode="Markdown"
        )
        
        # Notify customer
        try:
            customer_message = (
                f"🎉 *Seu pedido foi entregue!* 🎉\n\n"
                f"Seu pedido #{order.id} foi marcado como entregue.\n"
                f"Obrigado por comprar conosco!"
            )
            
            context.bot.send_message(
                chat_id=order.user_id,
                text=customer_message,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error notifying customer about delivery: {e}")
    else:
        query.answer("Não foi possível atualizar o status do pedido", show_alert=True)

def cancel_order(update: Update, context: CallbackContext):
    """Cancel order (admin only)"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Verify admin
    if str(user_id) != ADMIN_ID:
        query.answer("Você não tem permissão para esta ação", show_alert=True)
        return
    
    # Extract order ID from callback data
    order_id = query.data.split('_')[2]
    
    # Update order status
    from models import db
    success = db.update_order_status(order_id, "cancelado")
    
    if success:
        # Get updated order
        order = db.get_order(order_id)
        if not order:
            query.answer("Pedido não encontrado", show_alert=True)
            return
            
        # Get user info
        user = db.get_user(order.user_id)
        if not user:
            query.answer("Usuário não encontrado", show_alert=True)
            return
            
        # Notify admin
        query.answer("Pedido cancelado!", show_alert=True)
        
        # Update admin message
        order_details = format_order_details(order, include_items=True)
        admin_message = (
            f"❌ *PEDIDO CANCELADO* ❌\n\n"
            f"👤 *Cliente:* {user.nome}\n"
            f"📱 *Telefone:* {user.telefone}\n\n"
            f"{order_details}"
        )
        
        query.edit_message_text(
            text=admin_message,
            parse_mode="Markdown"
        )
        
        # Notify customer
        try:
            customer_message = (
                f"❌ *Seu pedido foi cancelado* ❌\n\n"
                f"Seu pedido #{order.id} foi cancelado.\n"
                f"Entre em contato com o suporte para mais informações."
            )
            
            context.bot.send_message(
                chat_id=order.user_id,
                text=customer_message,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error notifying customer about cancellation: {e}")
    else:
        query.answer("Não foi possível cancelar o pedido", show_alert=True)

def list_pending_orders(update: Update, context: CallbackContext):
    """List all pending orders (admin only)"""
    user_id = update.effective_user.id
    
    # Verify admin
    if str(user_id) != ADMIN_ID:
        update.message.reply_text("Você não tem permissão para esta ação")
        return
    
    # Get all orders
    from models import db, orders
    pending_orders = []
    
    for order_id, order in orders.items():
        if order.status == "pendente" or order.status == "pago":
            pending_orders.append(order)
    
    if not pending_orders:
        update.message.reply_text("Não há pedidos pendentes no momento.")
        return
    
    # Format and send each pending order
    for order in pending_orders:
        user = db.get_user(order.user_id)
        if not user:
            continue
            
        order_details = format_order_details(order, include_items=True)
        
        admin_message = (
            f"📋 *PEDIDO PENDENTE* 📋\n\n"
            f"👤 *Cliente:* {user.nome}\n"
            f"📱 *Telefone:* {user.telefone}\n\n"
            f"{order_details}"
        )
        
        # Add buttons for order management
        keyboard = [
            [InlineKeyboardButton("✅ Marcar como Entregue", callback_data=f"mark_delivered_{order.id}")],
            [InlineKeyboardButton("❌ Cancelar Pedido", callback_data=f"cancel_order_{order.id}")]
        ]
        
        update.message.reply_text(
            text=admin_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )