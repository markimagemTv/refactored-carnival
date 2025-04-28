import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from models import db
from utils import format_cart_message, log_error, MAIN_KEYBOARD
from handlers.payment import process_payment

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def view_cart(update: Update, context: CallbackContext):
    """Show user's shopping cart (triggered by message)"""
    try:
        user_id = update.effective_user.id
        
        # Get cart items
        cart_items = db.get_cart(user_id)
        
        if not cart_items:
            update.message.reply_text(
                "🛒 Seu carrinho está vazio.\n\n"
                "Use o botão '🛍️ Produtos' para navegar e adicionar produtos.",
                reply_markup=MAIN_KEYBOARD
            )
            return
            
        # Format cart message
        cart_message = format_cart_message(cart_items)
        
        # Create keyboard with checkout and clear cart buttons
        keyboard = [
            [InlineKeyboardButton("💰 Finalizar Compra", callback_data="checkout")],
            [InlineKeyboardButton("🗑️ Limpar Carrinho", callback_data="clear_cart")],
            [InlineKeyboardButton("🛍️ Continuar Comprando", callback_data="back_to_categories")]
        ]
        
        update.message.reply_text(
            cart_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        log_error(e, f"Error viewing cart for user {update.effective_user.id}")
        update.message.reply_text(
            "❌ Ocorreu um erro ao exibir seu carrinho. Por favor, tente novamente."
        )
        
def view_cart_callback(update: Update, context: CallbackContext):
    """Show user's shopping cart (triggered by callback button)"""
    try:
        query = update.callback_query
        query.answer()
        
        user_id = query.from_user.id
        
        # Get cart items
        cart_items = db.get_cart(user_id)
        
        if not cart_items:
            query.edit_message_text(
                "🛒 Seu carrinho está vazio.\n\n"
                "Use o botão '🛍️ Produtos' para navegar e adicionar produtos."
            )
            return
            
        # Format cart message
        cart_message = format_cart_message(cart_items)
        
        # Create keyboard with checkout and clear cart buttons
        keyboard = [
            [InlineKeyboardButton("💰 Finalizar Compra", callback_data="checkout")],
            [InlineKeyboardButton("🗑️ Limpar Carrinho", callback_data="clear_cart")],
            [InlineKeyboardButton("🛍️ Continuar Comprando", callback_data="back_to_categories")]
        ]
        
        query.edit_message_text(
            cart_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        log_error(e, f"Error viewing cart for user {update.effective_user.id}")
        update.message.reply_text(
            "❌ Ocorreu um erro ao exibir seu carrinho. Por favor, tente novamente."
        )

def checkout(update: Update, context: CallbackContext):
    """Process checkout and payment"""
    # Simplemente redireciona para process_payment em payment.py
    return process_payment(update, context)

def clear_cart(update: Update, context: CallbackContext):
    """Clear user's shopping cart"""
    try:
        query = update.callback_query
        if not query:
            # Caso não seja um callback, pode ser uma mensagem direta
            if update.message:
                update.message.reply_text(
                    "Por favor, use os botões fornecidos para gerenciar seu carrinho.",
                    reply_markup=MAIN_KEYBOARD
                )
            return
            
        query.answer()
        
        user_id = query.from_user.id
        
        # Clear cart
        db.clear_cart(user_id)
        
        query.edit_message_text(
            "🗑️ Seu carrinho foi esvaziado com sucesso!\n\n"
            "Use o botão '🛍️ Produtos' para navegar e adicionar produtos."
        )
        
    except Exception as e:
        user_id = "Unknown"
        if update.effective_user:
            user_id = update.effective_user.id
            
        log_error(e, f"Error clearing cart for user {user_id}")
        
        # Tratamento de erro seguro
        try:
            if update.callback_query:
                update.callback_query.edit_message_text(
                    "❌ Ocorreu um erro ao limpar seu carrinho. Por favor, tente novamente."
                )
            elif update.message:
                update.message.reply_text(
                    "❌ Ocorreu um erro ao limpar seu carrinho. Por favor, tente novamente.",
                    reply_markup=MAIN_KEYBOARD
                )
        except Exception:
            # Último recurso se nada funcionar
            pass