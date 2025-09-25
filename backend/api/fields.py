import base64
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для работы с base64 изображениями."""

    # Поддерживаемые форматы изображений
    SUPPORTED_FORMATS = ('jpeg', 'jpg', 'png', 'gif', 'webp')
    MAX_BASE64_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

    def to_internal_value(self, data):
        """Преобразование base64 строки в файл."""
        if not isinstance(data, str):
            return super().to_internal_value(data)

        if not data.startswith('data:image'):
            return super().to_internal_value(data)

        try:
            # Проверяем размер base64 строки
            if len(data) > self.MAX_BASE64_SIZE:
                max_size_mb = self.MAX_BASE64_SIZE // (1024 * 1024)
                raise ValidationError(
                    f'Размер изображения не должен превышать {max_size_mb}MB'
                )

            # Парсим data URL
            format_part, imgstr = data.split(';base64,')
            ext = format_part.split('/')[-1].lower()

            # Проверяем поддерживаемый формат
            if ext not in self.SUPPORTED_FORMATS:
                formats_str = ", ".join(self.SUPPORTED_FORMATS)
                raise ValidationError(
                    f'Неподдерживаемый формат изображения. '
                    f'Поддерживаемые форматы: {formats_str}'
                )

            # Декодируем base64
            try:
                decoded_data = base64.b64decode(imgstr)
            except Exception:
                raise ValidationError('Ошибка декодирования base64 данных')

            # Проверяем размер декодированных данных
            if len(decoded_data) > self.MAX_IMAGE_SIZE:
                max_img_mb = self.MAX_IMAGE_SIZE // (1024 * 1024)
                raise ValidationError(
                    f'Размер изображения не должен превышать {max_img_mb}MB'
                )

            # Создаем файл
            data = ContentFile(decoded_data, name=f'temp.{ext}')

        except ValueError:
            raise ValidationError('Неверный формат base64 данных')
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError('Ошибка обработки изображения')

        return super().to_internal_value(data)
