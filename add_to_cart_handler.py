#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Handler para adicionar produtos ao carrinho.
Este módulo implementa uma função para adicionar produtos ao carrinho
quando o usuário clica no botão "Adicionar ao Carrinho".
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('add_to_cart')

def add_to_cart_handler(update: Update, context: CallbackContext, db):
    """
    Handler para o callback de adicionar ao carrinho.
    
    Args:
        update: Objeto Update do Telegram
        context: CallbackContext do python-telegram-bot
        db: Objeto DataStore para persistência de dados
    
    Returns:
        None
    """
    try:
        query = update.callback_query
        query.answer()
        
        user_id = query.from_user.id
        
        # Verificar se a sessão atual está correta
        product = context.user_data.get('selected_product')
        if not product:
            logger.warning(f"Produto não encontrado na sessão para usuário {user_id}")
            query.edit_message_text(
                "❌ Erro: Produto não encontrado. Por favor, navegue novamente pelo catálogo.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Ver Categorias", callback_data="back_to_categories")
                ]])
            )
            return
        
        # Verificar se o produto tem formato válido
        if not isinstance(product, dict) or 'name' not in product or 'price' not in product:
            logger.error(f"Formato de produto inválido: {product}")
            query.edit_message_text(
                "❌ Erro: Dados do produto inválidos. Por favor, selecione outro produto.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Ver Categorias", callback_data="back_to_categories")
                ]])
            )
            return
        
        # Criar item do carrinho
        from bot_completo import CartItem  # Importação local para evitar dependências circulares
        
        item = CartItem(
            name=product['name'],
            price=product['price']
        )
        
        # Adicionar ao carrinho
        cart_items = db.add_to_cart(user_id, item)
        
        # Mensagem de sucesso
        message = (
            f"✅ *{product['name']}* foi adicionado ao seu carrinho!\n\n"
            f"O que você gostaria de fazer agora?"
        )
        
        # Teclado com opções
        keyboard = [
            [InlineKeyboardButton("🛒 Ver Carrinho", callback_data="view_cart")],
            [InlineKeyboardButton("🛍️ Continuar Comprando", callback_data="back_to_categories")]
        ]
        
        query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        logger.info(f"Produto '{product['name']}' adicionado ao carrinho do usuário {user_id}")
        
    except Exception as e:
        logger.error(f"Erro ao adicionar produto ao carrinho: {e}")
        user_id = "Unknown"
        if update and update.effective_user:
            user_id = update.effective_user.id
        
        try:
            if update and update.callback_query:
                update.callback_query.edit_message_text(
                    "❌ Ocorreu um erro ao adicionar o produto ao carrinho. Por favor, tente novamente.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔄 Ver Categorias", callback_data="back_to_categories")
                    ]])
                )
        except Exception as nested_error:
            logger.error(f"Erro ao tratar exceção: {nested_error}")