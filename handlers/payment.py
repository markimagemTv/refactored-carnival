import logging
import mercadopago
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config import MERCADO_PAGO_TOKEN
from models import db, CartItem
from utils import format_cart_message, log_error
from handlers.admin import notify_admin_new_order

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Mercado Pago SDK
mp = mercadopago.SDK(MERCADO_PAGO_TOKEN)

def process_payment(update: Update, context: CallbackContext):
    """Process payment using Mercado Pago"""
    try:
        query = update.callback_query
        if not query:
            # Caso não seja um callback, pode ser uma mensagem direta
            if update.message:
                update.message.reply_text(
                    "Por favor, use os botões fornecidos no carrinho para finalizar a compra."
                )
            return
            
        query.answer()
        
        user_id = update.effective_user.id
        
        # Get user info
        user = db.get_user(user_id)
        if not user:
            query.edit_message_text(
                "❌ Você precisa estar registrado para fazer uma compra. Use /start para se registrar."
            )
            return
        
        # Get cart items
        cart_items = db.get_cart(user_id)
        if not cart_items:
            query.edit_message_text(
                "❌ Seu carrinho está vazio. Adicione produtos antes de finalizar a compra."
            )
            return
    except Exception as e:
        user_id = "Unknown"
        if update.effective_user:
            user_id = update.effective_user.id
            
        log_error(e, f"Error starting payment process for user {user_id}")
        
        # Tratamento de erro seguro
        try:
            if update.callback_query:
                update.callback_query.edit_message_text(
                    "❌ Ocorreu um erro ao processar seu pagamento. Por favor, tente novamente."
                )
            elif update.message:
                update.message.reply_text(
                    "❌ Ocorreu um erro ao processar seu pagamento. Por favor, tente novamente."
                )
        except Exception:
            # Último recurso se nada funcionar
            pass
        return
    
    try:
        # Create order first
        order = db.create_order(user_id, cart_items)
        
        # Calculate total amount
        total_amount = sum(item.price for item in cart_items)
        
        # Create description for payment
        description = "DigiCompras: "
        for item in cart_items:
            description += f"{item.name}, "
        description = description.rstrip(", ")
        
        # Create PIX payment
        payment_data = {
            "transaction_amount": float(total_amount),
            "description": description,
            "payment_method_id": "pix",
            "payer": {
                "email": f"cliente_{user_id}@exemplo.com",  # Email válido para o Mercado Pago
                "first_name": user.nome,
                "last_name": "Cliente",
                "identification": {
                    "type": "CPF",
                    "number": "19119119100"  # CPF placeholder
                }
            },
            "external_reference": order.id
        }
        
        payment_response = mp.payment().create(payment_data)
        
        if payment_response["status"] == 201:
            payment = payment_response["response"]
            payment_id = payment["id"]
            
            # Update order with payment ID
            db.update_order_status(order.id, "pendente", payment_id)
            
            # Get PIX details
            pix_data = payment["point_of_interaction"]["transaction_data"]
            qr_code_base64 = pix_data["qr_code_base64"]
            pix_copy_paste = pix_data["qr_code"]
            
            # Send payment message with PIX details
            message = (
                f"🧾 *Resumo do Pedido #{order.id}*\n\n"
                f"{format_cart_message(cart_items)}\n\n"
                f"*PAGAMENTO VIA PIX*\n"
                f"Copie o código abaixo para pagar via PIX:\n\n"
                f"`{pix_copy_paste}`\n\n"
                f"Abra seu aplicativo bancário, escolha a opção PIX > Copia e Cola, e cole o código acima.\n\n"
                f"Após realizar o pagamento, clique no botão 'Verificar Pagamento' para confirmar."
            )
            
            keyboard = [
                [InlineKeyboardButton("🔍 Verificar Pagamento", callback_data=f"check_payment_{order.id}")]
            ]
            
            # First, edit the current message
            query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            # Não enviamos mais mensagem adicional sobre QR code
            # O texto já foi atualizado na mensagem principal
            
            # Clear cart after generating payment
            db.clear_cart(user_id)
            
            logger.info(f"PIX payment created for order {order.id} by user {user_id}")
            
        else:
            logger.error(f"Error creating PIX payment: {payment_response}")
            query.edit_message_text(
                "❌ Ocorreu um erro ao processar o pagamento PIX. Por favor, tente novamente mais tarde."
            )
            
    except Exception as e:
        log_error(e, f"Error processing payment for user {user_id}")
        query.edit_message_text(
            "❌ Ocorreu um erro ao processar o pagamento. Por favor, tente novamente mais tarde."
        )

def check_payment_status(update: Update, context: CallbackContext):
    """Check payment status for a specific order"""
    try:
        query = update.callback_query
        if not query:
            # Caso não seja um callback, pode ser uma mensagem direta
            if update.message:
                update.message.reply_text(
                    "Por favor, use os botões fornecidos para verificar o status do pagamento."
                )
            return
            
        query.answer()
        
        data = query.data
        order_id = data.split("_")[2]
        
        user_id = update.effective_user.id
    except Exception as e:
        user_id = "Unknown"
        if update.effective_user:
            user_id = update.effective_user.id
            
        log_error(e, f"Error starting payment check for user {user_id}")
        
        # Tratamento de erro seguro
        try:
            if update.callback_query:
                update.callback_query.edit_message_text(
                    "❌ Ocorreu um erro ao verificar o pagamento. Por favor, tente novamente."
                )
            elif update.message:
                update.message.reply_text(
                    "❌ Ocorreu um erro ao verificar o pagamento. Por favor, tente novamente."
                )
        except Exception:
            # Último recurso se nada funcionar
            pass
        return
    
    try:
        # Get order
        order = db.get_order(order_id)
        if not order:
            query.edit_message_text(
                "❌ Pedido não encontrado. Por favor, tente novamente."
            )
            return
        
        # Verify this is the user's order
        if order.user_id != user_id:
            query.edit_message_text(
                "❌ Você não tem permissão para verificar este pedido."
            )
            return
        
        # Get user info (needed for admin notification)
        user = db.get_user(user_id)
        if not user:
            query.edit_message_text(
                "❌ Informações do usuário não encontradas. Por favor, tente novamente."
            )
            return
        
        # Query Mercado Pago for payment status
        payment_status = None  # Initialize payment_status variable
        
        if not order.payment_id:
            # Check by external reference (order ID)
            search_params = {"external_reference": order_id}
            payment_result = mp.payment().search(search_params)
            
            if payment_result["status"] == 200:
                payments = payment_result["response"]["results"]
                
                if payments:
                    # Get latest payment
                    payment = payments[0]
                    payment_id = payment["id"]
                    payment_status = payment["status"]
                    
                    # Update order with payment ID
                    order.payment_id = payment_id
                    # This persists the payment ID to the order
                    db.update_order_status(order_id, order.status)
                    
                else:
                    # No payment found
                    query.edit_message_text(
                        "💰 *Status do Pagamento*\n\n"
                        "Ainda não identificamos seu pagamento.\n"
                        "Se você já pagou, aguarde alguns instantes e verifique novamente.\n\n"
                        "Se precisar pagar novamente, use o botão abaixo:",
                        parse_mode="Markdown",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔍 Verificar Novamente", callback_data=f"check_payment_{order_id}")]
                        ])
                    )
                    return
                    
        else:
            # We already have payment ID, check its status
            payment_id = order.payment_id
            payment_result = mp.payment().get(payment_id)
            
            if payment_result["status"] == 200:
                payment = payment_result["response"]
                payment_status = payment["status"]
            else:
                # Error getting payment info
                query.edit_message_text(
                    "❌ Não foi possível verificar o status do pagamento. Por favor, tente novamente mais tarde."
                )
                return
        
        # Make sure payment_status is defined before proceeding
        if payment_status is None:
            query.edit_message_text(
                "❌ Não foi possível determinar o status do pagamento. Por favor, tente novamente mais tarde."
            )
            return
            
        # Process payment status
        if payment_status == "approved":
            # If order wasn't marked as paid yet
            if order.status != "pago":
                # Update order status
                db.update_order_status(order_id, "pago")
                
                # Send admin notification about new paid order
                notify_admin_new_order(context, order, user)
            
            # Inform user
            query.edit_message_text(
                "✅ *Pagamento Aprovado!*\n\n"
                "Seu pagamento foi confirmado e seu pedido está sendo processado.\n"
                "Você receberá uma notificação quando seu pedido for entregue.\n\n"
                "Obrigado por comprar conosco!",
                parse_mode="Markdown"
            )
            
        elif payment_status == "pending" or payment_status == "in_process":
            query.edit_message_text(
                "⏳ *Pagamento Pendente*\n\n"
                "Seu pagamento está sendo processado.\n"
                "Por favor, verifique novamente em alguns instantes.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔍 Verificar Novamente", callback_data=f"check_payment_{order_id}")]
                ])
            )
            
        elif payment_status == "rejected" or payment_status == "cancelled":
            query.edit_message_text(
                "❌ *Pagamento Rejeitado*\n\n"
                "Infelizmente seu pagamento foi rejeitado ou cancelado.\n"
                "Por favor, tente novamente ou use outro método de pagamento.",
                parse_mode="Markdown"
            )
            
        else:
            query.edit_message_text(
                f"ℹ️ *Status do Pagamento: {payment_status}*\n\n"
                "Por favor, verifique novamente em alguns instantes ou entre em contato com o suporte.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔍 Verificar Novamente", callback_data=f"check_payment_{order_id}")]
                ])
            )
        
    except Exception as e:
        log_error(e, f"Error checking payment status for order {order_id}")
        query.edit_message_text(
            "❌ Ocorreu um erro ao verificar o status do pagamento. Por favor, tente novamente mais tarde.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Tentar Novamente", callback_data=f"check_payment_{order_id}")]
            ])
        )