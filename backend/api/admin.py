# api/admin.py
from django.contrib import admin
from django.db.models import Count
from .models import (
    Ingredient, Tag, Recipe, Favorite, ShoppingCart, Subscribe,
    IngredientInRecipe
)


class IngredientInRecipeInline(admin.TabularInline):
    """Inline для ингредиентов в рецепте."""
    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'cooking_time', 'favorites_count', 'created'
    )
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags', 'created', 'cooking_time')
    readonly_fields = ('created',)
    inlines = [IngredientInRecipeInline]

    def get_queryset(self, request):
        """Оптимизация запросов и аннотации."""
        queryset = super().get_queryset(request)
        return queryset.select_related('author').annotate(
            favorites_count=Count('favorite', distinct=True)
        )

    def favorites_count(self, obj):
        """Количество добавлений в избранное."""
        return obj.favorites_count
    favorites_count.short_description = 'В избранном'
    favorites_count.admin_order_field = 'favorites_count'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created')
    list_filter = ('user', 'created')
    search_fields = ('user__username', 'recipe__name')
    readonly_fields = ('created',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created')
    list_filter = ('user', 'created')
    search_fields = ('user__username', 'recipe__name')
    readonly_fields = ('created',)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', 'created')
    list_filter = ('user', 'author', 'created')
    search_fields = (
        'user__username', 'author__username', 'user__email', 'author__email'
    )
    readonly_fields = ('created',)
