import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, Filters

from config import TOKEN, ADMIN_ID
from handlers.admin import notify_admin_new_order, mark_as_delivered, cancel_order, list_pending_orders
from handlers.cart import view_cart, view_cart_callback, clear_cart, checkout
from handlers.orders import list_orders, order_details, check_payment_callback
from handlers.payment import check_payment_status
from handlers.products import (
    menu_inicial,
    show_category,
    select_product,
    handle_quantity,
    collect_product_fields,
    continue_shopping
)
from handlers.products_admin import (
    admin_products,
    admin_select_category,
    admin_select_product,
    admin_edit_product_field,
    admin_edit_discount,
    admin_handle_edit_value,
    admin_confirm_delete_product,
    admin_add_product_name,
    admin_add_product_price,
    admin_add_product_type,
    admin_add_product_fields,
    admin_cancel,
    admin_cancel_callback
)
from handlers.registration import start, handle_name, handle_phone, cancel
from models import db
from utils import MAIN_KEYBOARD, ADMIN_KEYBOARD

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# States for registration
NAME, PHONE = range(1, 3)

# States for admin product management
CATEGORY_SELECTION = 1
PRODUCT_ACTION = 2
ADD_PRODUCT_NAME = 3
ADD_PRODUCT_PRICE = 4
ADD_PRODUCT_FIELDS = 5
CONFIRM_DELETE = 6
EDIT_PRODUCT_FIELD = 7
EDIT_PRODUCT_VALUE = 8

class TelegramBot:
    """Main Telegram bot class"""

    def __init__(self, token):
        """Initialize bot with token"""
        self.token = token
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self._register_handlers()

    def _register_handlers(self):
        """Register all handlers"""
        # Registration conversation
        registration_conv = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                NAME: [MessageHandler(Filters.text & ~Filters.command, handle_name)],
                PHONE: [MessageHandler(Filters.text & ~Filters.command, handle_phone)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        self.dispatcher.add_handler(registration_conv)

        # Admin product management conversation
        admin_product_conv = ConversationHandler(
            entry_points=[CommandHandler('admin', admin_products)],
            states={
                CATEGORY_SELECTION: [
                    CallbackQueryHandler(admin_select_category, pattern=r'^admin_cat_|^admin_add_category')
                ],
                PRODUCT_ACTION: [
                    CallbackQueryHandler(admin_select_product, pattern=r'^admin_prod_|^admin_add_product|^admin_back_to_')
                ],
                ADD_PRODUCT_NAME: [
                    CallbackQueryHandler(admin_cancel_callback, pattern=r'^admin_cancel_add'),
                    MessageHandler(Filters.text & ~Filters.command, admin_add_product_name)
                ],
                ADD_PRODUCT_PRICE: [
                    CallbackQueryHandler(admin_cancel_callback, pattern=r'^admin_cancel_add'),
                    MessageHandler(Filters.text & ~Filters.command, admin_add_product_price)
                ],
                ADD_PRODUCT_FIELDS: [
                    CallbackQueryHandler(admin_add_product_type, pattern=r'^admin_type_'),
                    CallbackQueryHandler(admin_cancel_callback, pattern=r'^admin_cancel_add'),
                    MessageHandler(Filters.text & ~Filters.command, admin_add_product_fields)
                ],
                CONFIRM_DELETE: [
                    CallbackQueryHandler(admin_confirm_delete_product, pattern=r'^admin_confirm_delete|^admin_prod_')
                ],
                EDIT_PRODUCT_FIELD: [
                    CallbackQueryHandler(admin_edit_product_field, pattern=r'^admin_edit_|^admin_cat_|^admin_delete_')
                ],
                EDIT_PRODUCT_VALUE: [
                    CallbackQueryHandler(admin_edit_discount, pattern=r'^admin_set_discount_'),
                    MessageHandler(Filters.text & ~Filters.command, admin_handle_edit_value)
                ],
            },
            fallbacks=[CommandHandler('cancel', admin_cancel)]
        )
        self.dispatcher.add_handler(admin_product_conv)

        # Product navigation handlers
        self.dispatcher.add_handler(MessageHandler(Filters.regex(r'^🛍️ Produtos$'), menu_inicial))
        self.dispatcher.add_handler(CallbackQueryHandler(show_category, pattern=r'^category_'))
        self.dispatcher.add_handler(CallbackQueryHandler(select_product, pattern=r'^product_'))
        self.dispatcher.add_handler(CallbackQueryHandler(handle_quantity, pattern=r'^qty_'))
        self.dispatcher.add_handler(CallbackQueryHandler(
            continue_shopping, pattern=r'^back_to_categories|^back_to_products'))

        # Cart handlers
        self.dispatcher.add_handler(MessageHandler(Filters.regex(r'^🛒 Ver Carrinho$'), view_cart))
        self.dispatcher.add_handler(CallbackQueryHandler(view_cart_callback, pattern=r'^view_cart$'))
        self.dispatcher.add_handler(CallbackQueryHandler(clear_cart, pattern=r'^clear_cart$'))
        self.dispatcher.add_handler(CallbackQueryHandler(checkout, pattern=r'^checkout$'))

        # Order handlers
        self.dispatcher.add_handler(MessageHandler(Filters.regex(r'^📋 Meus Pedidos$'), list_orders))
        self.dispatcher.add_handler(CallbackQueryHandler(order_details, pattern=r'^order_details_'))
        self.dispatcher.add_handler(CallbackQueryHandler(check_payment_status, pattern=r'^check_payment_'))

        # Admin handlers
        self.dispatcher.add_handler(MessageHandler(Filters.regex(r'^🛠️ Admin$'), list_pending_orders))
        self.dispatcher.add_handler(CallbackQueryHandler(mark_as_delivered, pattern=r'^mark_delivered_'))
        self.dispatcher.add_handler(CallbackQueryHandler(cancel_order, pattern=r'^cancel_order_'))

        # Help handler
        self.dispatcher.add_handler(MessageHandler(Filters.regex(r'^❓ Ajuda$'), self._help_command))
        self.dispatcher.add_handler(CommandHandler('help', self._help_command))

        # Collect required fields for specific products
        self.dispatcher.add_handler(MessageHandler(
            Filters.text & ~Filters.command & ~Filters.regex(r'^🛒|^🛍️|^📋|^❓|^🛠️'),
            collect_product_fields
        ))

        # Error handler
        self.dispatcher.add_error_handler(self._error_handler)

    def _help_command(self, update, context):
        """Send help information"""
        user_id = update.effective_user.id
        
        help_text = (
            "🤖 *Comandos Disponíveis:*\n\n"
            "• /start - Iniciar o bot ou fazer cadastro\n"
            "• /help - Mostrar esta mensagem de ajuda\n\n"
            "*Navegação:*\n"
            "• 🛍️ Produtos - Ver categorias de produtos\n"
            "• 🛒 Ver Carrinho - Ver itens no carrinho\n"
            "• 📋 Meus Pedidos - Ver histórico de pedidos\n"
            "• ❓ Ajuda - Mostrar esta mensagem de ajuda\n\n"
            "Para comprar, navegue pelos produtos, selecione a quantidade desejada, e finalize a compra pelo carrinho."
        )
        
        # Add admin command if user is admin
        if str(user_id) == ADMIN_ID:
            help_text += (
                "\n\n*Comandos de Administrador:*\n"
                "• /admin - Gerenciar produtos\n"
                "• 🛠️ Admin - Ver pedidos pendentes\n"
            )
            
            update.message.reply_text(
                help_text,
                parse_mode="Markdown",
                reply_markup=ADMIN_KEYBOARD
            )
        else:
            update.message.reply_text(
                help_text,
                parse_mode="Markdown",
                reply_markup=MAIN_KEYBOARD
            )

    def _error_handler(self, update, context):
        """Log errors raised by handlers"""
        logger.error(f"Update {update} caused error: {context.error}")
        
        # Get user ID if available
        user_id = update.effective_user.id if update and update.effective_user else "Unknown"
        
        # Log detailed error
        logger.error(f"Error details: User {user_id}, Error: {context.error}")
        
        # Try to notify user about error
        if update and update.effective_chat:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Ocorreu um erro inesperado. Por favor, tente novamente mais tarde."
            )

    def run(self):
        """Start the bot"""
        logger.info("Starting bot polling...")
        self.updater.start_polling()
        self.updater.idle()