import requests
import stripe
from django.conf import settings
from dotenv import load_dotenv
from forex_python.converter import CurrencyRates

from config.settings import API_KEY_FOR_APILAYER, STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY
load_dotenv(override=True)


def create_stripe_product(name, description=None):
    """Создает продукт в Stripe"""
    try:
        product = stripe.Product.create(
            name=name,
            description=description or name,
        )
        return product
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания продукта в Stripe: {str(e)}")


def create_stripe_price(amount, product_id, currency="usd"):
    """Создает цену в Stripe"""
    try:
        price = stripe.Price.create(
            currency=currency,
            unit_amount=int(amount * 100),  # Конвертируем в центы
            product=product_id,
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания цены в Stripe: {str(e)}")


def create_stripe_session(price_id, success_url=None, cancel_url=None):
    """Создает сессию оплаты в Stripe"""
    try:
        session = stripe.checkout.Session.create(
            success_url=success_url or "http://127.0.0.1:8000/payment/success/",
            cancel_url=cancel_url or "http://127.0.0.1:8000/payment/cancel/",
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
        )
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания сессии в Stripe: {str(e)}")


def convert_via_apilayer(amount_rub, target_currency="USD"):
    """Конвертация через APILayer"""
    try:
        API_KEY = getattr(settings, "API_KEY_FOR_APILAYER", None)
        if not API_KEY:
            print("API_KEY_FOR_APILAYER не настроен")
            return None

        headers = {"apikey": API_KEY}
        url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={target_currency}&base=RUB"

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            rate = data["rates"][target_currency]
            result = amount_rub * rate
            print(f"APILayer: 1 RUB = {rate} {target_currency}")
            print(f"APILayer: {amount_rub} RUB = {result:.2f} {target_currency}")
            return result
        else:
            print(f"APILayer HTTP ошибка: {response.status_code}")
            return None

    except Exception as e:
        print(f"Ошибка APILayer: {e}")
        return None


def convert_rub_to_usd(amount_rub):
    """
    Умная конвертация RUB в USD с несколькими fallback-ами
    """
    print(f"=== НАЧАЛО КОНВЕРТАЦИИ ===")
    print(f"Конвертируем: {amount_rub} RUB → USD")

    # 1. Пробуем forex-python (основной способ)
    try:
        c = CurrencyRates()
        result = c.convert("RUB", "USD", amount_rub)
        print(f"forex-python: {amount_rub} RUB = {result:.2f} USD")
        return result
    except Exception as e:
        print(f"forex-python: {e}")

    # 2. Пробуем APILayer (второй вариант)
    print("Пробуем APILayer...")
    apilayer_result = convert_via_apilayer(amount_rub, "USD")
    if apilayer_result is not None:
        return apilayer_result

    # 3. Пробуем Центробанк России (третий вариант)
    print("Пробуем Центробанк РФ...")
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        data = response.json()
        usd_rate = data["Valute"]["USD"]["Value"]
        result = amount_rub / usd_rate
        print(f"ЦБ РФ: 1 USD = {usd_rate} RUB")
        print(f"ЦБ РФ: {amount_rub} RUB = {result:.2f} USD")
        return result
    except Exception as e:
        print(f"ЦБ РФ: {e}")

    # 4. Фиксированный курс (последний fallback)
    exchange_rate = getattr(settings, "EXCHANGE_RATE_USD_RUB", 80.0)
    result = amount_rub / exchange_rate
    print(f"Фиксированный курс: 1 USD = {exchange_rate} RUB")
    print(f"Результат: {amount_rub} RUB = {result:.2f} USD")
    print("=== КОНВЕРТАЦИЯ ЗАВЕРШЕНА ===")

    return result


def get_payment_status(session_id):
    """Получает статус платежа из Stripe"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status
    except stripe.error.StripeError as e:
        return "unknown"
