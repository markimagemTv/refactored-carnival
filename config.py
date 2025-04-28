import os

# Bot token
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Mercado Pago token
MERCADO_PAGO_TOKEN = os.getenv("MERCADO_PAGO_TOKEN")

# Admin Telegram ID
ADMIN_ID = os.getenv("ADMIN_ID")

# Product catalog
PRODUCT_CATALOG = {
    "ATIVAR APP": [
        {"name": "⚡ QUICK PLAYER R$65", "price": 65.00, "fields": ["MAC"]},
        {"name": "📱 NINJA PLAYER R$65", "price": 65.00, "fields": ["MAC", "CHAVE OTP"]},
        {"name": "📺 MEGA IPTV R$ 65", "price": 65.00, "fields": ["MAC"]},
        {"name": "🧠 SMART ONE R$60", "price": 60.00, "fields": ["MAC"]},
        {"name": "🎮 IBO PRO PLAYER R$50", "price": 50.00, "fields": ["MAC"]},
        {"name": "📡 IBO TV OFICIAL R$50", "price": 50.00, "fields": ["MAC"]},
        {"name": "🧩 DUPLECAST R$60", "price": 60.00, "fields": ["MAC"]},
        {"name": "🌐 BAY TV R$60", "price": 60.00, "fields": ["MAC"]},
        {"name": "🎥 VU PLAYER R$50", "price": 50.00, "fields": ["MAC"]},
        {"name": "🔥 SUPER PLAY R$50", "price": 50.00, "fields": ["MAC"]},
        {"name": "☁️ CLOUDDY R$65", "price": 65.00, "fields": ["E-mail", "Senha do app"]},
    ],
    "COMPRAR CRÉDITOS": [
        {"name": "⚡ FAST PLAYER (13,50und)", "price": 13.50, "discount": True},
        {"name": "👑 GOLD PLAY (13,50und)", "price": 13.50, "discount": True},
        {"name": "📺 EI TV (13,50und)", "price": 13.50, "discount": True},
        {"name": "🛰️ Z TECH (13,50und)", "price": 13.50, "discount": True},
        {"name": "🧠 GENIAL PLAY (13,50und)", "price": 13.50, "discount": True},
        {"name": "🚀 UPPER PLAY (14,50und)", "price": 14.50, "discount": False},
    ],
    "🔥 PROMOÇÕES": [
        {"name": "📺 PACOTE 10 CRÉDITOS EI TV", "price": 300.00, "discount": False},
    ]
}

# Discount percentage for credit purchases over threshold (5% discount)
DISCOUNT_PERCENTAGE = 0.95
DISCOUNT_THRESHOLD = 11  # Aplicar apenas para 11 créditos ou mais

# Logging level
LOG_LEVEL = "INFO"