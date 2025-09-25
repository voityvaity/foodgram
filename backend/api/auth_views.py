import logging
import re
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


def _get_user_data(user):
    """Получение данных пользователя для ответа."""
    return {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'avatar': user.avatar.url if user.avatar else None,
    }


def _validate_email(email):
    """Валидация email адреса."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@api_view(['POST'])
@permission_classes([AllowAny])
def custom_login(request):
    """Кастомный эндпоинт для входа в систему."""
    email = request.data.get('email')
    password = request.data.get('password')

    logger.info("Login attempt received")

    if not email or not password:
        logger.warning("Missing email or password")
        return Response(
            {'error': 'Необходимо указать email и пароль.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not _validate_email(email):
        logger.warning("Invalid email format")
        return Response(
            {'error': 'Неверный формат email адреса.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
        logger.info(f"User found: {user.email}, is_active: {user.is_active}")

        if user.check_password(password) and user.is_active:
            # Создаем или получаем существующий токен из базы данных
            token, created = Token.objects.get_or_create(user=user)
            logger.info(f"Token {'created' if created else 'retrieved'}")
            return Response({
                'auth_token': token.key,
                'user': _get_user_data(user)
            })
        else:
            logger.warning("Invalid password or inactive user")
            return Response(
                {'error': 'Неверный пароль или неактивный пользователь.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        logger.warning("User not found")
        return Response(
            {'error': 'Пользователь с таким email не найден.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def custom_me(request):
    """Кастомный эндпоинт для получения данных текущего пользователя."""
    user = request.user
    return Response(_get_user_data(user))
