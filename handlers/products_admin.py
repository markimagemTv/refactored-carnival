from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler

from models import db, CartItem
from utils import MAIN_KEYBOARD, log_error
from config import ADMIN_ID, PRODUCT_CATALOG

# Conversation states
CATEGORY_SELECTION = 1
PRODUCT_ACTION = 2
ADD_PRODUCT_NAME = 3
ADD_PRODUCT_PRICE = 4
ADD_PRODUCT_FIELDS = 5
CONFIRM_DELETE = 6
EDIT_PRODUCT_FIELD = 7
EDIT_PRODUCT_VALUE = 8

# Storage for conversation
product_temp_data = {}

def is_admin(user_id):
    """Check if the user is an admin"""
    return str(user_id) == ADMIN_ID

def admin_products(update: Update, context: CallbackContext):
    """Admin command to manage products"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        update.message.reply_text("❌ Você não tem permissão para acessar esta área administrativa.")
        return ConversationHandler.END
    
    # Create keyboard with categories
    keyboard = []
    for category in PRODUCT_CATALOG.keys():
        keyboard.append([InlineKeyboardButton(f"📂 {category}", callback_data=f"admin_cat_{category}")])
    
    # Add button to add new category
    keyboard.append([InlineKeyboardButton("➕ Adicionar Categoria", callback_data="admin_add_category")])
    
    update.message.reply_text(
        "🛠️ *Gerenciamento de Produtos*\n\n"
        "Selecione uma categoria para gerenciar seus produtos:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CATEGORY_SELECTION

def admin_select_category(update: Update, context: CallbackContext):
    """Handle admin category selection"""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        query.edit_message_text("❌ Você não tem permissão para acessar esta área administrativa.")
        return ConversationHandler.END
    
    data = query.data
    
    # Handle adding new category
    if data == "admin_add_category":
        query.edit_message_text(
            "➕ *Adicionar Nova Categoria*\n\n"
            "Por favor, envie o nome da nova categoria:"
        )
        context.user_data['admin_action'] = 'add_category'
        return ADD_PRODUCT_NAME
    
    # Handle existing category
    category_name = data.split("_")[2]
    context.user_data['admin_category'] = category_name
    
    # Show products in this category
    products = PRODUCT_CATALOG.get(category_name, [])
    
    keyboard = []
    for i, product in enumerate(products):
        keyboard.append([
            InlineKeyboardButton(
                f"{product['name']} - R${product['price']:.2f}", 
                callback_data=f"admin_prod_{i}"
            )
        ])
    
    # Add button to add new product
    keyboard.append([InlineKeyboardButton("➕ Adicionar Produto", callback_data="admin_add_product")])
    # Add button to go back
    keyboard.append([InlineKeyboardButton("◀️ Voltar", callback_data="admin_back_to_categories")])
    
    query.edit_message_text(
        f"🛠️ *Gerenciamento de Produtos: {category_name}*\n\n"
        f"Selecione um produto para editar ou excluir:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return PRODUCT_ACTION

def admin_select_product(update: Update, context: CallbackContext):
    """Handle admin product selection"""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        query.edit_message_text("❌ Você não tem permissão para acessar esta área administrativa.")
        return ConversationHandler.END
    
    data = query.data
    
    # Handle back button
    if data == "admin_back_to_categories":
        # Create keyboard with categories
        keyboard = []
        for category in PRODUCT_CATALOG.keys():
            keyboard.append([InlineKeyboardButton(f"📂 {category}", callback_data=f"admin_cat_{category}")])
        
        # Add button to add new category
        keyboard.append([InlineKeyboardButton("➕ Adicionar Categoria", callback_data="admin_add_category")])
        
        query.edit_message_text(
            "🛠️ *Gerenciamento de Produtos*\n\n"
            "Selecione uma categoria para gerenciar seus produtos:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return CATEGORY_SELECTION
    
    # Handle adding new product
    if data == "admin_add_product":
        category = context.user_data.get('admin_category')
        
        query.edit_message_text(
            f"➕ *Adicionar Novo Produto em {category}*\n\n"
            "Por favor, envie o nome do produto:"
        )
        
        context.user_data['admin_action'] = 'add_product'
        return ADD_PRODUCT_NAME
    
    # Handle existing product
    category = context.user_data.get('admin_category')
    product_index = int(data.split("_")[2])
    
    product = PRODUCT_CATALOG[category][product_index]
    context.user_data['admin_product_index'] = product_index
    
    # Show product details with edit/delete options
    fields_text = ", ".join(product.get('fields', [])) if 'fields' in product else "Nenhum"
    discount_text = "Sim" if product.get('discount', False) else "Não"
    
    product_info = (
        f"🔍 *Detalhes do Produto*\n\n"
        f"📝 Nome: {product['name']}\n"
        f"💰 Preço: R${product['price']:.2f}\n"
    )
    
    if 'fields' in product:
        product_info += f"📋 Campos: {fields_text}\n"
    
    if 'discount' in product:
        product_info += f"🏷️ Desconto: {discount_text}\n"
    
    keyboard = [
        [InlineKeyboardButton("✏️ Editar Nome", callback_data="admin_edit_name")],
        [InlineKeyboardButton("💰 Editar Preço", callback_data="admin_edit_price")]
    ]
    
    if 'fields' in product:
        keyboard.append([InlineKeyboardButton("📋 Editar Campos", callback_data="admin_edit_fields")])
    
    if 'discount' in product:
        keyboard.append([InlineKeyboardButton("🏷️ Alterar Desconto", callback_data="admin_edit_discount")])
    
    keyboard.append([InlineKeyboardButton("❌ Excluir Produto", callback_data="admin_delete_product")])
    keyboard.append([InlineKeyboardButton("◀️ Voltar", callback_data=f"admin_cat_{category}")])
    
    query.edit_message_text(
        product_info,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return EDIT_PRODUCT_FIELD

def admin_edit_product_field(update: Update, context: CallbackContext):
    """Handle product field selection for editing"""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        query.edit_message_text("❌ Você não tem permissão para acessar esta área administrativa.")
        return ConversationHandler.END
    
    data = query.data
    category = context.user_data.get('admin_category')
    
    # Handle back to category
    if data.startswith("admin_cat_"):
        return admin_select_category(update, context)
    
    # Handle delete product
    if data == "admin_delete_product":
        product_index = context.user_data.get('admin_product_index')
        product = PRODUCT_CATALOG[category][product_index]
        
        query.edit_message_text(
            f"❓ *Confirmar Exclusão*\n\n"
            f"Tem certeza que deseja excluir o produto:\n"
            f"*{product['name']}*?\n\n"
            f"Esta ação não pode ser desfeita.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Sim, Excluir", callback_data="admin_confirm_delete")],
                [InlineKeyboardButton("❌ Não, Cancelar", callback_data=f"admin_prod_{product_index}")]
            ])
        )
        
        return CONFIRM_DELETE
    
    # Handle various edit options
    if data.startswith("admin_edit_"):
        field = data.split("_")[2]
        product_index = context.user_data.get('admin_product_index')
        product = PRODUCT_CATALOG[category][product_index]
        
        context.user_data['admin_edit_field'] = field
        
        if field == "name":
            query.edit_message_text(
                f"✏️ *Editar Nome do Produto*\n\n"
                f"Nome atual: {product['name']}\n\n"
                f"Por favor, envie o novo nome para este produto:"
            )
            return EDIT_PRODUCT_VALUE
            
        elif field == "price":
            query.edit_message_text(
                f"💰 *Editar Preço do Produto*\n\n"
                f"Preço atual: R${product['price']:.2f}\n\n"
                f"Por favor, envie o novo preço para este produto (apenas números):"
            )
            return EDIT_PRODUCT_VALUE
            
        elif field == "fields":
            fields_text = ", ".join(product.get('fields', []))
            query.edit_message_text(
                f"📋 *Editar Campos do Produto*\n\n"
                f"Campos atuais: {fields_text}\n\n"
                f"Por favor, envie os novos campos separados por vírgula:"
            )
            return EDIT_PRODUCT_VALUE
            
        elif field == "discount":
            current = "ativado" if product.get('discount', False) else "desativado"
            query.edit_message_text(
                f"🏷️ *Alterar Desconto do Produto*\n\n"
                f"Desconto atual: {current}\n\n"
                f"Escolha uma opção:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Ativar Desconto", callback_data="admin_set_discount_true")],
                    [InlineKeyboardButton("❌ Desativar Desconto", callback_data="admin_set_discount_false")],
                    [InlineKeyboardButton("◀️ Voltar", callback_data=f"admin_prod_{product_index}")]
                ])
            )
            return EDIT_PRODUCT_VALUE
    
    return EDIT_PRODUCT_FIELD

def admin_edit_discount(update: Update, context: CallbackContext):
    """Handle discount setting via inline buttons"""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        query.edit_message_text("❌ Você não tem permissão para acessar esta área administrativa.")
        return ConversationHandler.END
    
    data = query.data
    category = context.user_data.get('admin_category')
    product_index = context.user_data.get('admin_product_index')
    
    if data.startswith("admin_set_discount_"):
        value = data.split("_")[-1] == "true"
        
        # Update product discount
        PRODUCT_CATALOG[category][product_index]['discount'] = value
        
        product = PRODUCT_CATALOG[category][product_index]
        
        query.edit_message_text(
            f"✅ *Desconto Atualizado!*\n\n"
            f"Produto: {product['name']}\n"
            f"Desconto: {'Ativado' if value else 'Desativado'}\n\n"
            f"Voltando para o menu do produto...",
            parse_mode="Markdown"
        )
        
        # Simulate going back to product view
        context.user_data['admin_action'] = None
        context.user_data['admin_edit_field'] = None
        
        # Need to create a new callback query since we can't change data of the existing one
        from telegram import CallbackQuery
        new_data = f"admin_prod_{product_index}"
        
        # Wait a moment before returning to product view
        import time
        time.sleep(1)
        
        # Now get product details again
        return admin_select_product(update, context)
    
    return EDIT_PRODUCT_FIELD

def admin_handle_edit_value(update: Update, context: CallbackContext):
    """Process the new value for product editing"""
    category = context.user_data.get('admin_category')
    product_index = context.user_data.get('admin_product_index')
    field = context.user_data.get('admin_edit_field')
    
    if not all([category, str(product_index).isdigit(), field]):
        update.message.reply_text("❌ Ocorreu um erro. Por favor, tente novamente.")
        return ConversationHandler.END
    
    product_index = int(product_index)
    new_value = update.message.text.strip()
    
    # Validate and update accordingly
    try:
        if field == "name":
            if not new_value:
                update.message.reply_text("❌ O nome não pode ficar vazio. Por favor, tente novamente.")
                return EDIT_PRODUCT_VALUE
            
            PRODUCT_CATALOG[category][product_index]['name'] = new_value
            
        elif field == "price":
            try:
                price = float(new_value.replace(',', '.'))
                if price <= 0:
                    raise ValueError("Price must be positive")
                
                PRODUCT_CATALOG[category][product_index]['price'] = price
            except:
                update.message.reply_text("❌ Preço inválido. Use apenas números (ex: 10.50). Por favor, tente novamente.")
                return EDIT_PRODUCT_VALUE
                
        elif field == "fields":
            fields = [f.strip() for f in new_value.split(',') if f.strip()]
            if not fields:
                update.message.reply_text("❌ Você deve fornecer pelo menos um campo. Por favor, tente novamente.")
                return EDIT_PRODUCT_VALUE
                
            PRODUCT_CATALOG[category][product_index]['fields'] = fields
        
        # Send confirmation and show product menu again
        update.message.reply_text(
            f"✅ *Produto atualizado com sucesso!*\n\n"
            f"Campo: {field}\n"
            f"Novo valor: {new_value}",
            parse_mode="Markdown"
        )
        
        # Show admin menu again
        keyboard = []
        for cat in PRODUCT_CATALOG.keys():
            keyboard.append([InlineKeyboardButton(f"📂 {cat}", callback_data=f"admin_cat_{cat}")])
        
        keyboard.append([InlineKeyboardButton("➕ Adicionar Categoria", callback_data="admin_add_category")])
        
        update.message.reply_text(
            "🛠️ *Gerenciamento de Produtos*\n\n"
            "Selecione uma categoria para gerenciar seus produtos:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return CATEGORY_SELECTION
        
    except Exception as e:
        update.message.reply_text(f"❌ Ocorreu um erro: {str(e)}. Por favor, tente novamente.")
        return EDIT_PRODUCT_VALUE

def admin_confirm_delete_product(update: Update, context: CallbackContext):
    """Confirm and process product deletion"""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        query.edit_message_text("❌ Você não tem permissão para acessar esta área administrativa.")
        return ConversationHandler.END
    
    data = query.data
    
    if data == "admin_confirm_delete":
        category = context.user_data.get('admin_category')
        product_index = context.user_data.get('admin_product_index')
        
        # Get product before deletion for confirmation message
        product = PRODUCT_CATALOG[category][product_index]
        product_name = product['name']
        
        # Delete the product
        del PRODUCT_CATALOG[category][product_index]
        
        query.edit_message_text(
            f"✅ *Produto Excluído!*\n\n"
            f"O produto *{product_name}* foi excluído com sucesso.",
            parse_mode="Markdown"
        )
        
        # Return to category view after a short delay
        import time
        time.sleep(1)
        
        # Show products in this category again
        return admin_select_category(update, context)
    
    # If not confirmed, go back to product details
    product_index = context.user_data.get('admin_product_index')
    context.user_data['admin_action'] = None
    
    return admin_select_product(update, context)

def admin_add_product_name(update: Update, context: CallbackContext):
    """Handle new product name input"""
    if not update.message:
        # Caso anômalo - não temos uma mensagem para processar
        return ConversationHandler.END
        
    action = context.user_data.get('admin_action')
    
    # Add cancel option with a keyboard
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="admin_cancel_add")]]
    
    if action == 'add_category':
        category_name = update.message.text.strip()
        if not category_name:
            update.message.reply_text(
                "❌ O nome da categoria não pode ficar vazio. Tente novamente:", 
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ADD_PRODUCT_NAME
        
        if category_name in PRODUCT_CATALOG:
            update.message.reply_text(
                "❌ Esta categoria já existe. Escolha outro nome:", 
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ADD_PRODUCT_NAME
        
        # Add new empty category
        PRODUCT_CATALOG[category_name] = []
        
        update.message.reply_text(
            f"✅ *Nova Categoria Adicionada!*\n\n"
            f"A categoria *{category_name}* foi criada com sucesso.",
            parse_mode="Markdown"
        )
        
        # Show admin menu again
        keyboard = []
        for cat in PRODUCT_CATALOG.keys():
            keyboard.append([InlineKeyboardButton(f"📂 {cat}", callback_data=f"admin_cat_{cat}")])
        
        keyboard.append([InlineKeyboardButton("➕ Adicionar Categoria", callback_data="admin_add_category")])
        
        update.message.reply_text(
            "🛠️ *Gerenciamento de Produtos*\n\n"
            "Selecione uma categoria para gerenciar seus produtos:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return CATEGORY_SELECTION
        
    elif action == 'add_product':
        product_name = update.message.text.strip()
        if not product_name:
            update.message.reply_text(
                "❌ O nome do produto não pode ficar vazio. Tente novamente:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ADD_PRODUCT_NAME
        
        user_id = update.effective_user.id
        # Store in temporary storage
        product_temp_data[user_id] = {'name': product_name}
        
        # Log para debug
        from utils import log_error
        log_error(f"Produto temp iniciado: {product_temp_data[user_id]}", f"Usuário {user_id}")
        
        update.message.reply_text(
            "💰 *Preço do Produto*\n\n"
            "Por favor, informe o preço do produto (apenas números):",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return ADD_PRODUCT_PRICE
    
    update.message.reply_text(
        "❌ Operação inválida. Use /admin para voltar ao menu administrativo.",
        reply_markup=MAIN_KEYBOARD
    )
    return ConversationHandler.END

def admin_add_product_price(update: Update, context: CallbackContext):
    """Handle new product price input"""
    if not update.message:
        # Caso anômalo - não temos uma mensagem para processar
        return ConversationHandler.END
        
    try:
        price_text = update.message.text.strip().replace(',', '.')
        price = float(price_text)
        
        if price <= 0:
            update.message.reply_text(
                "❌ O preço deve ser maior que zero. Tente novamente:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancelar", callback_data="admin_cancel_add")]])
            )
            return ADD_PRODUCT_PRICE
        
        # Store price in temp data
        user_id = update.effective_user.id
        if user_id not in product_temp_data:
            # Log para debug
            from utils import log_error
            log_error("Produto temp não encontrado ao tentar adicionar preço", f"Usuário {user_id}")
            product_temp_data[user_id] = {}
        
        product_temp_data[user_id]['price'] = price
        
        # Log para debug
        from utils import log_error
        log_error(f"Preço adicionado ao produto temp: {product_temp_data[user_id]}", f"Usuário {user_id}")
        
        # Ask if it's a credit product (with discount) or an app product (with fields)
        update.message.reply_text(
            "📦 *Tipo de Produto*\n\n"
            "Este produto é um aplicativo (requer campos) ou créditos (possui desconto)?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📱 Aplicativo (Campos)", callback_data="admin_type_app")],
                [InlineKeyboardButton("💰 Créditos (Desconto)", callback_data="admin_type_credit")]
            ])
        )
        
        return ADD_PRODUCT_FIELDS
        
    except ValueError:
        update.message.reply_text(
            "❌ Preço inválido. Use apenas números (ex: 10.50). Tente novamente:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancelar", callback_data="admin_cancel_add")]])
        )
        return ADD_PRODUCT_PRICE

def admin_add_product_type(update: Update, context: CallbackContext):
    """Handle product type selection"""
    query = update.callback_query
    query.answer()
    
    data = query.data
    user_id = query.from_user.id
    category = context.user_data.get('admin_category')
    
    if user_id not in product_temp_data:
        query.edit_message_text("❌ Erro nos dados do produto. Por favor, comece novamente.")
        return ConversationHandler.END
    
    # Handle app product (needs fields)
    if data == "admin_type_app":
        query.edit_message_text(
            "📋 *Campos do Produto*\n\n"
            "Por favor, informe os campos necessários, separados por vírgula.\n"
            "Exemplo: MAC, Email, Senha"
        )
        product_temp_data[user_id]['type'] = 'app'
        return ADD_PRODUCT_FIELDS
    
    # Handle credit product (has discount option)
    elif data == "admin_type_credit":
        # Finalize credit product creation
        new_product = {
            'name': product_temp_data[user_id]['name'],
            'price': product_temp_data[user_id]['price'],
            'discount': True  # Default true for credit products
        }
        
        # Add to catalog
        PRODUCT_CATALOG[category].append(new_product)
        
        # Clear temp data
        if user_id in product_temp_data:
            del product_temp_data[user_id]
        
        query.edit_message_text(
            f"✅ *Produto Adicionado!*\n\n"
            f"O produto *{new_product['name']}* foi adicionado à categoria *{category}* com sucesso.",
            parse_mode="Markdown"
        )
        
        # Return to category view after a short delay
        import time
        time.sleep(1)
        
        # Show updated category
        return admin_select_category(update, context)
    
    return ADD_PRODUCT_FIELDS

def admin_add_product_fields(update: Update, context: CallbackContext):
    """Handle product fields input for app products"""
    user_id = update.effective_user.id
    category = context.user_data.get('admin_category')
    
    # Check if this is a callback for cancel
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        if query.data == "admin_cancel_add":
            # Clear temp data
            if user_id in product_temp_data:
                del product_temp_data[user_id]
                
            query.edit_message_text("❌ Adição de produto cancelada.")
            
            # Show categories after a moment
            import time
            time.sleep(1)
            
            # Create keyboard with categories
            keyboard = []
            for cat in PRODUCT_CATALOG.keys():
                keyboard.append([InlineKeyboardButton(f"📂 {cat}", callback_data=f"admin_cat_{cat}")])
            
            keyboard.append([InlineKeyboardButton("➕ Adicionar Categoria", callback_data="admin_add_category")])
            
            context.bot.send_message(
                chat_id=user_id,
                text="🛠️ *Gerenciamento de Produtos*\n\n"
                    "Selecione uma categoria para gerenciar seus produtos:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            return CATEGORY_SELECTION
        return ADD_PRODUCT_FIELDS
    
    # Este é um tratamento para mensagem de texto (não é callback)
    if not update.message:
        # Caso anômalo - nem callback nem mensagem
        return ConversationHandler.END
        
    # Processar mensagem normal
    fields_text = update.message.text.strip()
    fields = [f.strip() for f in fields_text.split(',') if f.strip()]
    
    if user_id not in product_temp_data:
        # Não temos dados temporários - precisamos informar o usuário
        update.message.reply_text(
            "❌ Erro: não encontramos dados do produto em andamento. Por favor, inicie o processo novamente usando o comando de administração.",
            reply_markup=MAIN_KEYBOARD
        )
        return ConversationHandler.END
        
    # Verificar se temos tipo definido (app ou credit)
    if 'type' not in product_temp_data[user_id]:
        product_temp_data[user_id]['type'] = 'app'  # Define padrão como app se não estiver definido
    
    if not fields:
        update.message.reply_text(
            "❌ Você deve fornecer pelo menos um campo. Tente novamente:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancelar", callback_data="admin_cancel_add")]])
        )
        return ADD_PRODUCT_FIELDS
    
    # Create new app product
    new_product = {
        'name': product_temp_data[user_id]['name'],
        'price': product_temp_data[user_id]['price'],
        'fields': fields
    }
    
    # Add to catalog
    PRODUCT_CATALOG[category].append(new_product)
    
    # Clear temp data
    if user_id in product_temp_data:
        del product_temp_data[user_id]
    
    update.message.reply_text(
        f"✅ *Produto Adicionado!*\n\n"
        f"O produto *{new_product['name']}* foi adicionado à categoria *{category}* com sucesso.",
        parse_mode="Markdown"
    )
    
    # Show admin menu again
    keyboard = []
    for cat in PRODUCT_CATALOG.keys():
        keyboard.append([InlineKeyboardButton(f"📂 {cat}", callback_data=f"admin_cat_{cat}")])
    
    keyboard.append([InlineKeyboardButton("➕ Adicionar Categoria", callback_data="admin_add_category")])
    
    update.message.reply_text(
        "🛠️ *Gerenciamento de Produtos*\n\n"
        "Selecione uma categoria para gerenciar seus produtos:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CATEGORY_SELECTION

def admin_cancel(update: Update, context: CallbackContext):
    """Cancel admin operations"""
    user_id = update.effective_user.id
    
    # Clear temp data
    if user_id in product_temp_data:
        del product_temp_data[user_id]
    
    context.user_data.pop('admin_category', None)
    context.user_data.pop('admin_product_index', None)
    context.user_data.pop('admin_action', None)
    context.user_data.pop('admin_edit_field', None)
    
    # Handle callback or message
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            "❌ Operação administrativa cancelada."
        )
        
        # Return to main admin panel after a moment
        import time
        time.sleep(1)
        
        # Create keyboard with categories
        keyboard = []
        for cat in PRODUCT_CATALOG.keys():
            keyboard.append([InlineKeyboardButton(f"📂 {cat}", callback_data=f"admin_cat_{cat}")])
        
        keyboard.append([InlineKeyboardButton("➕ Adicionar Categoria", callback_data="admin_add_category")])
        
        context.bot.send_message(
            chat_id=user_id,
            text="🛠️ *Gerenciamento de Produtos*\n\n"
                "Selecione uma categoria para gerenciar seus produtos:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return CATEGORY_SELECTION
    elif update.message:
        update.message.reply_text(
            "❌ Operação administrativa cancelada.",
            reply_markup=MAIN_KEYBOARD
        )
        
        return ConversationHandler.END
    else:
        # Caso anômalo - nem callback nem mensagem
        return ConversationHandler.END
    
def admin_cancel_callback(update: Update, context: CallbackContext):
    """Handle cancellation via callback query"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    
    # Clear temp data
    if user_id in product_temp_data:
        del product_temp_data[user_id]
    
    context.user_data.pop('admin_category', None)
    context.user_data.pop('admin_product_index', None)
    context.user_data.pop('admin_action', None)
    context.user_data.pop('admin_edit_field', None)
    
    query.edit_message_text("❌ Operação administrativa cancelada.")
    
    # Return to main admin panel after a moment
    import time
    time.sleep(1)
    
    # Create keyboard with categories
    keyboard = []
    for cat in PRODUCT_CATALOG.keys():
        keyboard.append([InlineKeyboardButton(f"📂 {cat}", callback_data=f"admin_cat_{cat}")])
    
    keyboard.append([InlineKeyboardButton("➕ Adicionar Categoria", callback_data="admin_add_category")])
    
    context.bot.send_message(
        chat_id=user_id,
        text="🛠️ *Gerenciamento de Produtos*\n\n"
            "Selecione uma categoria para gerenciar seus produtos:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CATEGORY_SELECTION