# lms/validators.py
from django.core.exceptions import ValidationError
from urllib.parse import urlparse


def validate_youtube_url(value):
    """Разрешает только ссылки на youtube.com."""
    if not value:
        return

    parsed = urlparse(value)
    domain = parsed.netloc.lower()

    allowed = ('youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com')

    if domain not in allowed:
        raise ValidationError(
            'Ссылка должна вести только на youtube.com. '
            'Сторонние ресурсы запрещены.'
        )
