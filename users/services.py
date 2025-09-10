import stripe
from dotenv import load_dotenv
from config.settings import STRIPE_API_KEY
from forex_python.converter import CurrencyRates

stripe.api_key = STRIPE_API_KEY
load_dotenv(override=True)

def convert_rub_into_usd(amount):
    """Конвертирует рубли в доллары"""
    c = CurrencyRates()
    rub_rate = c.get_rate('RUB', 'USD')
    return round(amount * rub_rate, 2)

def create_stripe_price(amount):
    """Создает цену в сервисе stripe"""

    price = stripe.Price.create(
        currency="usd",
        unit_amount=amount*100,
        product_data={"name": "Курс"},
    )
    return price

def create_stripe_session(price):
    """Создает сессию на оплату в stripe"""
    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/",
        line_items=[{"price": price.get('id'), "quantity": 1}],
        mode="payment",
    )
    return session.get('id'), session.get('url')