import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from config import PRODUCT_CATALOG, DISCOUNT_THRESHOLD
from models import db, CartItem
from utils import (
    create_categories_keyboard, 
    create_products_keyboard, 
    create_credits_keyboard,
    apply_discount,
    log_error,
    MAIN_KEYBOARD
)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
COLLECT_FIELDS = 1

def menu_inicial(update: Update, context: CallbackContext):
    """Display initial product categories menu"""
    try:
        # Verificar se há um callback ou mensagem
        if update.callback_query:
            query = update.callback_query
            query.answer()
            keyboard = create_categories_keyboard()
            
            query.edit_message_text(
                "🛍️ *Categorias de Produtos*\n\n"
                "Escolha uma categoria para ver os produtos disponíveis:",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        elif update.message:
            # Create keyboard with categories
            keyboard = create_categories_keyboard()
            
            update.message.reply_text(
                "🛍️ *Categorias de Produtos*\n\n"
                "Escolha uma categoria para ver os produtos disponíveis:",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        else:
            # Não há mensagem ou callback
            return
    except Exception as e:
        user_id = "Unknown"
        if update.effective_user:
            user_id = update.effective_user.id
            
        log_error(e, f"Error showing categories for user {user_id}")
        
        # Tratamento de erro seguro
        try:
            if update.callback_query:
                update.callback_query.edit_message_text(
                    "❌ Ocorreu um erro ao exibir as categorias. Por favor, tente novamente."
                )
            elif update.message:
                update.message.reply_text(
                    "❌ Ocorreu um erro ao exibir as categorias. Por favor, tente novamente.",
                    reply_markup=MAIN_KEYBOARD
                )
        except Exception:
            # Último recurso se nada funcionar
            pass

def show_category(update: Update, context: CallbackContext):
    """Show products in selected category"""
    try:
        query = update.callback_query
        if not query:
            # Caso não seja um callback, pode ser uma mensagem direta
            if update.message:
                update.message.reply_text(
                    "Por favor, use os botões fornecidos para navegar pelo menu.",
                    reply_markup=MAIN_KEYBOARD
                )
            return
            
        query.answer()
        
        # Extract category from callback data
        category = query.data.split("_")[1]
        
        # Store selected category in user data
        context.user_data['selected_category'] = category
        
        # Get products for this category
        products = PRODUCT_CATALOG.get(category, [])
        
        if not products:
            query.edit_message_text(
                f"😢 Não há produtos disponíveis na categoria {category} no momento."
            )
            return
        
        # Create keyboard with products
        keyboard = create_products_keyboard(products)
        
        query.edit_message_text(
            f"📦 *Produtos na categoria {category}*\n\n"
            f"Escolha um produto para ver detalhes:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        user_id = "Unknown"
        if update.effective_user:
            user_id = update.effective_user.id
            
        log_error(e, f"Error showing products for user {user_id}")
        
        # Tratamento de erro seguro
        try:
            if update.callback_query:
                update.callback_query.edit_message_text(
                    "❌ Ocorreu um erro ao exibir os produtos. Por favor, tente novamente."
                )
            elif update.message:
                update.message.reply_text(
                    "❌ Ocorreu um erro ao exibir os produtos. Por favor, tente novamente.",
                    reply_markup=MAIN_KEYBOARD
                )
        except Exception:
            # Último recurso se nada funcionar
            pass

def select_product(update: Update, context: CallbackContext):
    """Handle product selection"""
    try:
        query = update.callback_query
        if not query:
            # Caso não seja um callback, pode ser uma mensagem direta
            if update.message:
                update.message.reply_text(
                    "Por favor, use os botões fornecidos para navegar pelo menu.",
                    reply_markup=MAIN_KEYBOARD
                )
            return
            
        query.answer()
        
        # Get selected category
        category = context.user_data.get('selected_category')
        if not category:
            query.edit_message_text(
                "❌ Erro: Categoria não selecionada. Por favor, comece novamente."
            )
            return
        
        # Extract product index from callback data
        product_index = int(query.data.split("_")[1])
        
        # Get products and selected product
        products = PRODUCT_CATALOG.get(category, [])
        if product_index >= len(products):
            query.edit_message_text(
                "❌ Erro: Produto não encontrado. Por favor, tente novamente."
            )
            return
        
        product = products[product_index]
        
        # Store product in user data
        context.user_data['selected_product'] = product
        context.user_data['product_index'] = product_index
        
        # Handle different types of products
        if category == "COMPRAR CRÉDITOS":
            # For credit products, show quantity options
            keyboard = create_credits_keyboard()
            
            query.edit_message_text(
                f"🎮 *{product['name']}*\n\n"
                f"💰 Preço unitário: R${product['price']:.2f}\n\n"
                f"Selecione a quantidade de créditos:",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        else:
            # For app products, show product details and add to cart button
            # Check if product has required fields
            fields = product.get('fields', [])
            
            message = (
                f"📱 *{product['name']}*\n\n"
                f"💰 Preço: R${product['price']:.2f}\n"
            )
            
            if fields:
                context.user_data['required_fields'] = fields
                context.user_data['collected_fields'] = {}
                
                # Show first field prompt
                message += (
                    f"\nPara adicionar ao carrinho, precisamos de algumas informações:\n\n"
                    f"Por favor, informe o seu *{fields[0]}*:"
                )
                
                query.edit_message_text(
                    message,
                    parse_mode="Markdown"
                )
                
                return COLLECT_FIELDS
            else:
                # No required fields, add directly to cart
                cart_item = CartItem(
                    name=product['name'],
                    price=product['price']
                )
                
                db.add_to_cart(query.from_user.id, cart_item.to_dict())
                
                message += "\n✅ Produto adicionado ao carrinho!"
                
                keyboard = [
                    [InlineKeyboardButton("🛒 Ver Carrinho", callback_data="view_cart")],
                    [InlineKeyboardButton("🛍️ Continuar Comprando", callback_data="back_to_categories")]
                ]
                
                query.edit_message_text(
                    message,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
    except Exception as e:
        user_id = "Unknown"
        if update.effective_user:
            user_id = update.effective_user.id
            
        log_error(e, f"Error selecting product for user {user_id}")
        
        # Tratamento de erro seguro
        try:
            if update.callback_query:
                update.callback_query.edit_message_text(
                    "❌ Ocorreu um erro ao selecionar o produto. Por favor, tente novamente."
                )
            elif update.message:
                update.message.reply_text(
                    "❌ Ocorreu um erro ao selecionar o produto. Por favor, tente novamente.",
                    reply_markup=MAIN_KEYBOARD
                )
        except Exception:
            # Último recurso se nada funcionar
            pass

def handle_quantity(update: Update, context: CallbackContext):
    """Handle credit quantity selection"""
    try:
        query = update.callback_query
        if not query:
            # Caso não seja um callback, pode ser uma mensagem direta
            if update.message:
                update.message.reply_text(
                    "Por favor, use os botões fornecidos para navegar pelo menu.",
                    reply_markup=MAIN_KEYBOARD
                )
            return
            
        query.answer()
        
        # Extract quantity from callback data
        quantity = int(query.data.split("_")[1])
        
        # Get selected product
        product = context.user_data.get('selected_product')
        if not product:
            query.edit_message_text(
                "❌ Erro: Produto não selecionado. Por favor, comece novamente."
            )
            return
        
        # Calculate price with possible discount
        has_discount = product.get('discount', False)
        total_price = apply_discount(product['price'], quantity, has_discount)
        
        # Format product name with quantity
        product_name = f"{product['name']} - {quantity} créditos"
        
        # Create cart item
        cart_item = CartItem(
            name=product_name,
            price=total_price
        )
        
        # Add to cart
        db.add_to_cart(query.from_user.id, cart_item.to_dict())
        
        # Show confirmation message
        discount_msg = ""
        if has_discount and quantity >= DISCOUNT_THRESHOLD:
            discount_msg = f"\n💯 *Desconto de 5% aplicado!*"
        elif has_discount and quantity == 10:
            discount_msg = f"\n⚠️ *Desconto disponível apenas para 11+ créditos*"
        elif not has_discount and "UPPER PLAY" in product_name:
            discount_msg = f"\n⚠️ *Produto sem desconto disponível*"
        
        message = (
            f"✅ *Produto adicionado ao carrinho!*\n\n"
            f"🎮 {product_name}\n"
            f"💰 Total: R${total_price:.2f}{discount_msg}"
        )
        
        keyboard = [
            [InlineKeyboardButton("🛒 Ver Carrinho", callback_data="view_cart")],
            [InlineKeyboardButton("🛍️ Continuar Comprando", callback_data="back_to_categories")]
        ]
        
        query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        user_id = "Unknown"
        if update.effective_user:
            user_id = update.effective_user.id
            
        log_error(e, f"Error handling quantity for user {user_id}")
        
        # Tratamento de erro seguro
        try:
            if update.callback_query:
                update.callback_query.edit_message_text(
                    "❌ Ocorreu um erro ao selecionar a quantidade. Por favor, tente novamente."
                )
            elif update.message:
                update.message.reply_text(
                    "❌ Ocorreu um erro ao selecionar a quantidade. Por favor, tente novamente.",
                    reply_markup=MAIN_KEYBOARD
                )
        except Exception:
            # Último recurso se nada funcionar
            pass

def collect_product_fields(update: Update, context: CallbackContext):
    """Collect required fields for app products"""
    try:
        # Get required fields and collected fields so far
        required_fields = context.user_data.get('required_fields', [])
        collected_fields = context.user_data.get('collected_fields', {})
        
        if not required_fields:
            update.message.reply_text(
                "❌ Erro: Informações do produto não encontradas. Por favor, comece novamente.",
                reply_markup=MAIN_KEYBOARD
            )
            return ConversationHandler.END
        
        # Get current field based on how many we've already collected
        current_field_index = len(collected_fields)
        if current_field_index >= len(required_fields):
            update.message.reply_text(
                "❌ Erro: Todos os campos já foram coletados. Por favor, comece novamente.",
                reply_markup=MAIN_KEYBOARD
            )
            return ConversationHandler.END
            
        current_field = required_fields[current_field_index]
        
        # Store the field value
        field_value = update.message.text.strip()
        collected_fields[current_field] = field_value
        context.user_data['collected_fields'] = collected_fields
        
        # Check if we have all required fields
        if len(collected_fields) == len(required_fields):
            # All fields collected, add to cart
            product = context.user_data.get('selected_product')
            
            # Create details string from collected fields
            details = {}
            for field, value in collected_fields.items():
                details[field] = value
            
            # Create cart item
            cart_item = CartItem(
                name=product['name'],
                price=product['price'],
                details=details
            )
            
            # Add to cart
            db.add_to_cart(update.effective_user.id, cart_item.to_dict())
            
            # Show confirmation
            message = (
                f"✅ *Produto adicionado ao carrinho!*\n\n"
                f"📱 {product['name']}\n"
                f"💰 Preço: R${product['price']:.2f}\n\n"
                f"*Detalhes informados:*\n"
            )
            
            for field, value in details.items():
                message += f"• {field}: {value}\n"
            
            update.message.reply_text(
                message,
                parse_mode="Markdown",
                reply_markup=MAIN_KEYBOARD
            )
            
            # Clear temporary data
            context.user_data.pop('required_fields', None)
            context.user_data.pop('collected_fields', None)
            context.user_data.pop('selected_product', None)
            
            return ConversationHandler.END
        else:
            # We need more fields, ask for the next one
            next_field_index = current_field_index + 1
            next_field = required_fields[next_field_index]
            
            update.message.reply_text(
                f"Agora, informe o seu *{next_field}*:",
                parse_mode="Markdown"
            )
            
            return COLLECT_FIELDS
    except Exception as e:
        log_error(e, f"Error collecting fields for user {update.effective_user.id}")
        update.message.reply_text(
            "❌ Ocorreu um erro ao processar suas informações. Por favor, tente novamente.",
            reply_markup=MAIN_KEYBOARD
        )
        return ConversationHandler.END

def continue_shopping(update: Update, context: CallbackContext):
    """Handle continue shopping action"""
    try:
        query = update.callback_query
        if not query:
            # Caso não seja um callback, pode ser uma mensagem direta
            if update.message:
                update.message.reply_text(
                    "Por favor, use os botões fornecidos para navegar pelo menu.",
                    reply_markup=MAIN_KEYBOARD
                )
            return
            
        query.answer()
        
        action = query.data
        
        if action == "back_to_categories":
            # Show categories menu
            keyboard = create_categories_keyboard()
            
            query.edit_message_text(
                "🛍️ *Categorias de Produtos*\n\n"
                "Escolha uma categoria para ver os produtos disponíveis:",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        elif action == "back_to_products":
            # Show products in the previously selected category
            category = context.user_data.get('selected_category')
            if not category:
                query.edit_message_text(
                    "❌ Erro: Categoria não encontrada. Por favor, comece novamente."
                )
                return
                
            products = PRODUCT_CATALOG.get(category, [])
            keyboard = create_products_keyboard(products)
            
            query.edit_message_text(
                f"📦 *Produtos na categoria {category}*\n\n"
                f"Escolha um produto para ver detalhes:",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
    except Exception as e:
        user_id = "Unknown"
        if update.effective_user:
            user_id = update.effective_user.id
            
        log_error(e, f"Error continuing shopping for user {user_id}")
        
        # Tratamento de erro seguro
        try:
            if update.callback_query:
                update.callback_query.edit_message_text(
                    "❌ Ocorreu um erro ao navegar. Por favor, tente novamente."
                )
            elif update.message:
                update.message.reply_text(
                    "❌ Ocorreu um erro ao navegar. Por favor, tente novamente.",
                    reply_markup=MAIN_KEYBOARD
                )
        except Exception:
            # Último recurso se nada funcionar
            pass