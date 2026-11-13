# lms/services.py
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name: str) -> stripe.Product:
    """Создаёт продукт в Stripe."""
    return stripe.Product.create(name=name)


def create_stripe_price(product_id: str, amount: int) -> stripe.Price:
    """
    Создаёт цену в Stripe.
    amount — в копейках (цена * 100).
    """
    return stripe.Price.create(
        product=product_id,
        unit_amount=amount,  # копейки
        currency='rub',
    )


def create_stripe_session(price_id: str, success_url: str, cancel_url: str) -> stripe.checkout.Session:
    """Создаёт сессию оплаты и возвращает ссылку."""
    return stripe.checkout.Session.create(
        line_items=[{'price': price_id, 'quantity': 1}],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
def retrieve_stripe_session(session_id: str) -> stripe.checkout.Session:
    """Получает данные о сессии по ID."""
    return stripe.checkout.Session.retrieve(session_id)

