from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import (
    Ingredient, Tag, Recipe, IngredientInRecipe,
    Favorite, ShoppingCart
)

User = get_user_model()


class UserAPITestCase(APITestCase):
    """Тесты для API пользователей."""

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_user_registration(self):
        """Тест регистрации пользователя."""
        url = reverse('user-list')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_user_login(self):
        """Тест входа пользователя."""
        url = reverse('custom-login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_token', response.data)

    def test_get_user_profile(self):
        """Тест получения профиля пользователя."""
        url = reverse('custom-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')


class IngredientAPITestCase(APITestCase):
    """Тесты для API ингредиентов."""

    def setUp(self):
        self.ingredient1 = Ingredient.objects.create(
            name='Мука',
            measurement_unit='г'
        )
        self.ingredient2 = Ingredient.objects.create(
            name='Молоко',
            measurement_unit='мл'
        )

    def test_get_ingredients_list(self):
        """Тест получения списка ингредиентов."""
        url = reverse('ingredient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_ingredients(self):
        """Тест поиска ингредиентов."""
        url = reverse('ingredient-list')
        response = self.client.get(url, {'name': 'Мука'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Мука')


class RecipeAPITestCase(APITestCase):
    """Тесты для API рецептов."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )

        self.ingredient1 = Ingredient.objects.create(
            name='Мука',
            measurement_unit='г'
        )
        self.ingredient2 = Ingredient.objects.create(
            name='Молоко',
            measurement_unit='мл'
        )

        self.tag1 = Tag.objects.create(
            name='Завтрак',
            color='#E26C2D',
            slug='breakfast'
        )

    def test_get_recipes_list(self):
        """Тест получения списка рецептов."""
        recipe = Recipe.objects.create(
            author=self.user,
            name='Тестовый рецепт',
            text='Описание',
            cooking_time=30
        )
        recipe.tags.add(self.tag1)

        url = reverse('recipe-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_recipe_favorite(self):
        """Тест добавления рецепта в избранное."""
        recipe = Recipe.objects.create(
            author=self.user,
            name='Тестовый рецепт',
            text='Описание',
            cooking_time=30
        )

        url = reverse('recipe-favorite', kwargs={'pk': recipe.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Favorite.objects.filter(user=self.user, recipe=recipe).exists()
        )

    def test_recipe_shopping_cart(self):
        """Тест добавления рецепта в корзину покупок."""
        recipe = Recipe.objects.create(
            author=self.user,
            name='Тестовый рецепт',
            text='Описание',
            cooking_time=30
        )

        url = reverse('recipe-shopping-cart', kwargs={'pk': recipe.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ShoppingCart.objects.filter(user=self.user, recipe=recipe).exists()
        )

    def test_recipe_filtering_by_tags(self):
        """Тест фильтрации рецептов по тегам."""
        recipe1 = Recipe.objects.create(
            author=self.user,
            name='Рецепт 1',
            text='Описание',
            cooking_time=30
        )
        recipe1.tags.add(self.tag1)

        Recipe.objects.create(
            author=self.user,
            name='Рецепт 2',
            text='Описание',
            cooking_time=30
        )

        url = reverse('recipe-list')
        response = self.client.get(url, {'tags': 'breakfast'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_download_shopping_cart(self):
        """Тест скачивания списка покупок."""
        recipe = Recipe.objects.create(
            author=self.user,
            name='Тестовый рецепт',
            text='Описание',
            cooking_time=30
        )

        # Добавляем ингредиенты в рецепт
        IngredientInRecipe.objects.create(
            recipe=recipe,
            ingredient=self.ingredient1,
            amount=200
        )
        IngredientInRecipe.objects.create(
            recipe=recipe,
            ingredient=self.ingredient2,
            amount=300
        )

        # Добавляем рецепт в корзину
        ShoppingCart.objects.create(user=self.user, recipe=recipe)

        url = reverse('recipe-download-shopping-cart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')

    def test_ingredient_summing_in_shopping_cart(self):
        """Тест суммирования ингредиентов в списке покупок."""
        # Создаем два рецепта с одинаковыми ингредиентами
        recipe1 = Recipe.objects.create(
            author=self.user,
            name='Рецепт 1',
            text='Описание',
            cooking_time=30
        )
        recipe2 = Recipe.objects.create(
            author=self.user,
            name='Рецепт 2',
            text='Описание',
            cooking_time=30
        )

        # Добавляем одинаковые ингредиенты в оба рецепта
        IngredientInRecipe.objects.create(
            recipe=recipe1,
            ingredient=self.ingredient1,
            amount=200
        )
        IngredientInRecipe.objects.create(
            recipe=recipe2,
            ingredient=self.ingredient1,
            amount=300
        )

        # Добавляем рецепты в корзину
        ShoppingCart.objects.create(user=self.user, recipe=recipe1)
        ShoppingCart.objects.create(user=self.user, recipe=recipe2)

        url = reverse('recipe-download-shopping-cart')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что ингредиенты суммировались
        content = response.content.decode('utf-8')
        self.assertIn('Мука — 500 г', content)  # 200 + 300 = 500


class PostgreSQLTestCase(APITestCase):
    """Тесты для проверки работы с PostgreSQL."""

    def test_database_connection(self):
        """Тест подключения к базе данных."""
        from django.db import connection

        with connection.cursor() as cursor:
            # Проверяем, что можем выполнить простой запрос
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()[0]
            self.assertEqual(result, 1)

    def test_database_operations(self):
        """Тест операций с базой данных."""
        # Создаем пользователя
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        # Создаем ингредиент
        ingredient = Ingredient.objects.create(
            name='Тестовый ингредиент',
            measurement_unit='г'
        )

        # Создаем рецепт
        recipe = Recipe.objects.create(
            author=user,
            name='Тестовый рецепт',
            text='Описание',
            cooking_time=30
        )

        # Проверяем, что данные сохранились
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Ingredient.objects.count(), 1)
        self.assertEqual(Recipe.objects.count(), 1)

        # Проверяем связи
        self.assertEqual(recipe.author, user)

        # Проверяем сложные запросы
        recipes_with_ingredients = Recipe.objects.filter(
            ingredientinrecipe__ingredient=ingredient
        ).distinct()
        self.assertEqual(recipes_with_ingredients.count(), 0)
