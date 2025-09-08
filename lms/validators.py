from rest_framework import serializers
from urllib.parse import urlparse
import re


class YouTubeLinkValidator:
    """
    Валидатор для проверки, что ссылки ведут только на YouTube
    """

    def __init__(self, fields):
        self.fields = fields if isinstance(fields, list) else [fields]
        self.allowed_domains = [
            'youtube.com',
            'www.youtube.com',
            'youtu.be',
            'www.youtu.be',
            'm.youtube.com',
        ]

    def __call__(self, attrs):
        for field in self.fields:
            field_value = attrs.get(field)

            if not field_value:
                continue

            # Ищем все URL в тексте
            url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
            urls = re.findall(url_pattern, str(field_value))

            for url in urls:
                self.validate_single_url(url, field)

        return attrs

    def validate_single_url(self, url, field_name):
        """Проверяет одну ссылку на соответствие YouTube"""
        # Добавляем http:// если отсутствует схема
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()

            # Убираем www. для унификации проверки
            domain = domain.replace('www.', '')

            # Проверяем, что домен разрешен
            is_valid = False
            for allowed_domain in self.allowed_domains:
                if allowed_domain in domain:
                    is_valid = True
                    break

            if not is_valid:
                raise serializers.ValidationError({
                    field_name: f'Ссылки разрешены только на YouTube. Найден запрещенный ресурс: {domain}'
                })

        except Exception as e:
            raise serializers.ValidationError({
                field_name: f'Ошибка проверки ссылки: {str(e)}'
            })