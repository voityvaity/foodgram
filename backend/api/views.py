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
from rest_framework.decorators import action
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
from .constants import (
    FILTER_TRUE_VALUE, CACHE_EXPIRES, CONTENT_TYPE_TEXT_PLAIN, BASE64_SEPARATOR
)


User = get_user_model()
logger = logging.getLogger(__name__)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет чтения ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = []
    pagination_class = None

    def get_queryset(self):
        """Кастомная фильтрация по параметру name."""
        queryset = Ingredient.objects.all()
        name = self.request.GET.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset

    def list(self, request, *args, **kwargs):
        """Переопределяем list для отключения пагинации."""
        queryset = Ingredient.objects.all()
        name = request.GET.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)

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
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly]

    def list(self, request, *args, **kwargs):
        """Переопределяем list для добавления заголовков отключения
        кэширования."""
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = CACHE_EXPIRES
        return response

    def get_permissions(self):
        special_actions = [
            'favorite', 'shopping_cart', 'download_shopping_cart'
        ]
        if self.action in special_actions:
            return [permissions.IsAuthenticated()]
        return [IsAuthorOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        """Кастомная фильтрация для правильной работы с тегами."""
        queryset = Recipe.objects.all()

        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        ingredients = self.request.query_params.getlist('ingredients')
        if ingredients:
            queryset = queryset.filter(
                ingredients__id__in=ingredients
            ).distinct()

        is_favorited = self.request.query_params.get('is_favorited')
        if (is_favorited == FILTER_TRUE_VALUE
                and self.request.user.is_authenticated):
            queryset = queryset.filter(favorite__user=self.request.user)

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if (is_in_shopping_cart == FILTER_TRUE_VALUE
                and self.request.user.is_authenticated):
            queryset = queryset.filter(shoppingcart__user=self.request.user)

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
        shopping_cart = request.user.shopping_cart.all()

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
            shopping_list, content_type=CONTENT_TYPE_TEXT_PLAIN
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
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
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
            format, imgstr = avatar_data.split(BASE64_SEPARATOR)
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
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if author.following.filter(user=request.user).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Subscribe.objects.create(user=request.user, author=author)
            serializer = UserSubscriptionSerializer(
                author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = author.following.filter(user=request.user)
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

        update_session_auth_hash(request, user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Оптимизировано: сразу подтягиваем author через select_related"""
        subscriptions = request.user.follower.select_related('author')

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
