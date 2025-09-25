import base64
import logging
import uuid

from django.contrib.auth import get_user_model, update_session_auth_hash
from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import parsers, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import (
    Ingredient,
    IngredientInRecipe,
    Favorite,
    Recipe,
    ShoppingCart,
    Subscribe,
    Tag,
)
from .permissions import (
    IsAuthenticatedOrCreateOnly,
    IsAuthorOrReadOnly,
    IsOwnerOrReadOnly,
)
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    UserSerializer,
    RecipeShortSerializer,
    UserSubscriptionSerializer,
    SetPasswordSerializer,
)


@api_view(['GET'])
def test_ingredients(request):
    """Тестовый endpoint для проверки фильтрации ингредиентов."""
    name = request.GET.get('name')
    logger.debug(f"name parameter = {name}")

    queryset = Ingredient.objects.all()
    if name:
        queryset = queryset.filter(name__istartswith=name)
        logger.debug(f"filtered queryset count = {queryset.count()}")
    else:
        logger.debug("no name parameter, returning all ingredients")

    serializer = IngredientSerializer(queryset, many=True)
    return Response(serializer.data)


User = get_user_model()
logger = logging.getLogger(__name__)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет чтения ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # Убираем SearchFilter, используем только кастомную фильтрацию
    filter_backends = []
    # Отключаем пагинацию для ингредиентов
    pagination_class = None

    def _filter_by_name(self, queryset):
        """Фильтрация по имени ингредиента."""
        name = self.request.GET.get('name')
        logger.debug(f"name parameter = {name}")
        if name:
            queryset = queryset.filter(name__istartswith=name)
            logger.debug(f"filtered queryset count = {queryset.count()}")
        else:
            logger.debug("no name parameter, returning all ingredients")
        return queryset

    def get_queryset(self):
        """Кастомная фильтрация по параметру name."""
        queryset = Ingredient.objects.all()
        return self._filter_by_name(queryset)

    def list(self, request, *args, **kwargs):
        """Переопределяем list для отключения пагинации."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет чтения тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD рецептов и действия: избранное, корзина, выгрузка."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly]

    def get_permissions(self):
        authenticated_actions = [
            'create', 'update', 'partial_update', 'destroy',
            'favorite', 'shopping_cart', 'download_shopping_cart'
        ]

        if self.action in authenticated_actions:
            return [permissions.IsAuthenticated()]
        return [IsAuthorOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise permissions.PermissionDenied(
                'Вы можете редактировать только свои рецепты')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise permissions.PermissionDenied(
                'Вы можете удалять только свои рецепты')
        instance.delete()

    def get_queryset(self):
        """Получение queryset с оптимизацией запросов."""
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'tags', 'ingredients', 'favorite_set', 'shoppingcart_set'
        )

        # Фильтрация по тегам
        tags = self.request.query_params.get('tags')
        if tags:
            queryset = queryset.filter(tags__slug=tags).distinct()

        # Фильтрация по автору
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author_id=author)

        # Фильтрация по избранному
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited and self.request.user.is_authenticated:
            if is_favorited.lower() == 'true':
                queryset = queryset.filter(favorite__user=self.request.user)

        # Фильтрация по корзине
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart and self.request.user.is_authenticated:
            if is_in_shopping_cart.lower() == 'true':
                queryset = queryset.filter(
                    shoppingcart__user=self.request.user)

        return queryset.order_by('-created')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        response_serializer = RecipeSerializer(
            recipe, context={'request': request}
        )
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    def _relation_action(
        self, request, pk, model, exists_message, not_exists_message
    ):
        recipe = get_object_or_404(Recipe, pk=pk)
        relation_qs = model.objects.filter(user=request.user, recipe=recipe)

        if request.method == 'POST':
            if relation_qs.exists():
                return Response(
                    {'errors': exists_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not relation_qs.exists():
                return Response(
                    {'errors': not_exists_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            relation_qs.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        response_serializer = RecipeSerializer(
            recipe, context={'request': request})
        return Response(response_serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return self._relation_action(
            request,
            pk,
            Favorite,
            exists_message='Рецепт уже в избранном',
            not_exists_message='Рецепт не был в избранном',
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        return self._relation_action(
            request,
            pk,
            ShoppingCart,
            exists_message='Рецепт уже в корзине покупок',
            not_exists_message='Рецепт не был в корзине покупок',
        )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=request.user)

        if not shopping_cart.exists():
            return Response(
                {'errors': 'Список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe_ids = shopping_cart.values_list('recipe_id', flat=True)

        ingredients = IngredientInRecipe.objects.filter(
            recipe_id__in=recipe_ids
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        shopping_list = "Список покупок:\n\n"
        for ingredient in ingredients:
            shopping_list += (
                f"• {ingredient['ingredient__name']} "
                f"— {ingredient['total_amount']} "
                f"{ingredient['ingredient__measurement_unit']}\n"
            )

        response = HttpResponse(
            shopping_list, content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class UserViewSet(viewsets.ModelViewSet):
    r"""Профили, аватар, пароль, подписки."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrCreateOnly]

    def get_permissions(self):
        # Только владелец может редактировать или удалять свой профиль
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        # Авторизация обязательна для работы с аватаром, паролем, подписками
        elif self.action in ['me', 'avatar', 'delete_avatar',
                             'set_password', 'subscriptions',
                             'subscribe']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='me/avatar',
            parser_classes=[parsers.JSONParser])
    def avatar(self, request):
        user = request.user
        avatar_data = request.data.get('avatar')

        if not avatar_data:
            return Response(
                {'errors': 'Данные аватара не предоставлены'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            format, imgstr = avatar_data.split(';base64,')
            ext = format.split('/')[-1]
            filename = f"{uuid.uuid4().hex}.{ext}"

            user.avatar.save(filename, ContentFile(base64.b64decode(imgstr)))
            user.save()

            return Response(
                {'avatar': request.build_absolute_uri(user.avatar.url)},
                status=status.HTTP_200_OK
            )

        except Exception:
            logger.exception("Ошибка при загрузке аватара")

            return Response(
                {'errors': 'Неверный формат данных аватара'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        if not user.avatar:
            return Response(
                {'errors': 'Аватар отсутствует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.avatar.delete()
        user.avatar = None
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            # Проверяем, не пытается ли пользователь подписаться на себя
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Проверяем, не подписан ли уже пользователь
            if Subscribe.objects.filter(
                    user=request.user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Создаем подписку
            Subscribe.objects.create(user=request.user, author=author)

            # Возвращаем данные пользователя
            serializer = UserSubscriptionSerializer(
                author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Subscribe.objects.filter(
                user=request.user, author=author)
            if not subscription.exists():
                return Response(
                    {'errors': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        # оставляем пользователя залогиненным
        update_session_auth_hash(request, user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Оптимизировано: сразу подтягиваем author через select_related"""
        subscriptions = Subscribe.objects.filter(
            user=request.user
        ).select_related('author')

        authors = [sub.author for sub in subscriptions]

        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = UserSubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserSubscriptionSerializer(
            authors, many=True, context={'request': request}
        )
        return Response(serializer.data)
