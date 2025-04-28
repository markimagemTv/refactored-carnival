import mercadopago
import os
from models import db, CartItem

# Configuração
user_id = int(os.environ.get("ADMIN_ID"))
mp = mercadopago.SDK(os.environ.get("MERCADO_PAGO_TOKEN"))

# Get user info
user = db.get_user(user_id)
if not user:
    print("Usuário não encontrado. Registrando...")
    db.save_user(user_id, "Usuário Teste", "11999999999")
    user = db.get_user(user_id)
    
# Limpar carrinho
db.clear_cart(user_id)

# Adicionar item ao carrinho
item = CartItem(
    name="⚡ FAST PLAYER", 
    price=13.50 * 11, 
    details={"credits": 11, "discount": True, "original_price": 13.50}
)
db.add_to_cart(user_id, item.to_dict())

# Imprimir carrinho
cart = db.get_cart(user_id)
print(f"Carrinho: {[i.name for i in cart]} - Total: R${sum(i.price for i in cart):.2f}")

# Criar pedido
order = db.create_order(user_id, cart)
print(f"Pedido criado: #{order.id}")

# Criar pagamento PIX
description = "Teste: FAST PLAYER"
payment_data = {
    "transaction_amount": float(sum(i.price for i in cart)),
    "description": description,
    "payment_method_id": "pix",
    "payer": {
        "email": f"cliente_{user_id}@exemplo.com",
        "first_name": user.nome,
        "last_name": "Cliente",
        "identification": {
            "type": "CPF",
            "number": "19119119100"
        }
    },
    "external_reference": order.id
}

# Fazer a requisição
payment_response = mp.payment().create(payment_data)

# Verificar resposta
if payment_response["status"] == 201:
    payment = payment_response["response"]
    payment_id = payment["id"]
    
    # Atualizar pedido
    db.update_order_status(order.id, "pendente", payment_id)
    
    # Obter dados do PIX
    pix_data = payment["point_of_interaction"]["transaction_data"]
    pix_copy_paste = pix_data["qr_code"]
    
    print("✅ PAGAMENTO PIX GERADO COM SUCESSO!")
    print(f"ID Pagamento: {payment_id}")
    print("\nCÓDIGO PIX (copia e cola):\n")
    print(pix_copy_paste[:50] + "..." if len(pix_copy_paste) > 50 else pix_copy_paste)
    print("\nQR Code disponível nos dados do pagamento")
    
    # Limpar carrinho após pagar
    db.clear_cart(user_id)
else:
    print(f"❌ Erro ao criar pagamento PIX: {payment_response}")