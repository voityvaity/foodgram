import django_filters
from .models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов."""

    tags = django_filters.CharFilter(method='filter_by_tags')
    author = django_filters.NumberFilter(field_name='author__id')
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def _is_user_authenticated(self):
        """Проверка аутентификации пользователя."""
        return (hasattr(self.request, 'user')
                and self.request.user.is_authenticated)

    def filter_by_tags(self, queryset, name, value):
        """Фильтр по тегам через slug."""
        if not value:
            return queryset
        return queryset.filter(tags__slug=value)

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр по избранным рецептам."""
        if not value:
            return queryset

        if not self._is_user_authenticated():
            return queryset.none()

        return queryset.filter(favorite__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр по рецептам в корзине покупок."""
        if not value:
            return queryset

        if not self._is_user_authenticated():
            return queryset.none()

        return queryset.filter(shoppingcart__user=self.request.user)
