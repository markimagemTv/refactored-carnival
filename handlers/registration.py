from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from models import db
from utils import MAIN_KEYBOARD, log_error

# States
NAME = 1
PHONE = 2

def start(update: Update, context: CallbackContext):
    """Start command handler - entry point for new users"""
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Check if user is already registered
        existing_user = db.get_user(chat_id)
        if existing_user:
            update.message.reply_text(
                f"Bem-vindo de volta, {existing_user.nome}! 👋",
                reply_markup=MAIN_KEYBOARD
            )
            return ConversationHandler.END
            
        # New user - start registration
        update.message.reply_text(
            "Olá! Bem-vindo à nossa loja digital! 🎉\n\n"
            "Para começar, preciso que me informe seu nome completo:"
        )
        return NAME
    except Exception as e:
        log_error(e, f"Error in start handler for user {update.effective_user.id}")
        update.message.reply_text(
            "Desculpe, ocorreu um erro ao iniciar o bot. Por favor, tente novamente."
        )
        return ConversationHandler.END

def handle_name(update: Update, context: CallbackContext):
    """Handle user name input"""
    try:
        context.user_data['nome'] = update.message.text
        update.message.reply_text(
            "Obrigado! Agora, envie seu telefone com DDD (ex: 11999999999):"
        )
        return PHONE
    except Exception as e:
        log_error(e, f"Error in handle_name for user {update.effective_user.id}")
        update.message.reply_text(
            "Desculpe, ocorreu um erro. Por favor, tente novamente com /start."
        )
        return ConversationHandler.END

def handle_phone(update: Update, context: CallbackContext):
    """Handle user phone input and complete registration"""
    try:
        nome = context.user_data.get("nome")
        telefone = update.message.text
        
        # Basic validation
        if not telefone.isdigit() or len(telefone) < 10 or len(telefone) > 11:
            update.message.reply_text(
                "Formato de telefone inválido. Por favor, envie apenas números com DDD (ex: 11999999999):"
            )
            return PHONE
            
        # Save user information
        user_id = update.effective_chat.id
        db.save_user(user_id, nome, telefone)
        
        update.message.reply_text(
            f"✅ Cadastro concluído com sucesso!\n\n"
            f"Nome: {nome}\n"
            f"Telefone: {telefone}\n\n"
            f"Use os botões abaixo para navegar pela loja:",
            reply_markup=MAIN_KEYBOARD
        )
        return ConversationHandler.END
    except Exception as e:
        log_error(e, f"Error in handle_phone for user {update.effective_user.id}")
        update.message.reply_text(
            "Desculpe, ocorreu um erro ao salvar seus dados. Por favor, tente novamente com /start."
        )
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    """Cancel conversation handler"""
    update.message.reply_text(
        "Operação cancelada. Use /start para começar novamente."
    )
    return ConversationHandler.END