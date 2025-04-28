from config import DISCOUNT_THRESHOLD, DISCOUNT_PERCENTAGE
from utils import apply_discount

# Simular cada um dos produtos de crédito
test_products = [
    {"name": "⚡ FAST PLAYER (13,50und)", "price": 13.50, "discount": True},
    {"name": "👑 GOLD PLAY (13,50und)", "price": 13.50, "discount": True},
    {"name": "📺 EI TV (13,50und)", "price": 13.50, "discount": True},
    {"name": "🛰️ Z TECH (13,50und)", "price": 13.50, "discount": True},
    {"name": "🧠 GENIAL PLAY (13,50und)", "price": 13.50, "discount": True},
    {"name": "🚀 UPPER PLAY (14,50und)", "price": 14.50, "discount": False}
]

test_quantities = [10, 11, 20, 50, 100]

print(f"Teste de desconto - Limiar: {DISCOUNT_THRESHOLD} créditos")
print(f"Percentual de desconto: {(1 - DISCOUNT_PERCENTAGE) * 100:.1f}%")
print("-" * 80)

# Testar todos os produtos com todas as quantidades
for product in test_products:
    product_name = product["name"]
    price = product["price"]
    has_discount = product["discount"]
    
    print(f"\nProduto: {product_name} (Desconto habilitado: {has_discount})")
    print("-" * 60)
    
    for qty in test_quantities:
        # Calcular preço sem desconto (referência)
        price_without_discount = price * qty
        
        # Calcular preço com possível desconto
        price_with_discount = apply_discount(price, qty, has_discount)
        
        # Verificar se desconto foi aplicado
        discount_applied = price_with_discount < price_without_discount
        
        # Mostrar resultado
        print(f"Quantidade: {qty} créditos")
        print(f"  Preço sem desconto: R${price_without_discount:.2f}")
        print(f"  Preço com desconto: R${price_with_discount:.2f}")
        print(f"  Desconto aplicado: {'✅ SIM' if discount_applied else '❌ NÃO'}")
        
        # Verificação extra para debugging
        expected_discount = has_discount and qty >= DISCOUNT_THRESHOLD
        correct_behavior = expected_discount == discount_applied
        
        if not correct_behavior:
            print(f"  ⚠️ ERRO: Comportamento incorreto do desconto!")
            print(f"     Esperado: {'Aplicar desconto' if expected_discount else 'Não aplicar desconto'}")