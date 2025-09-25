from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """Модель пользователя с дополнительными полями."""

    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


def validate_hex_color(value):
    """Валидация hex цвета."""
    if not value.startswith('#') or len(value) != 7:
        raise ValidationError('Цвет должен быть в формате HEX (#RRGGBB)')


def validate_positive_cooking_time(value):
    """Валидация времени приготовления."""
    if value <= 0:
        raise ValidationError('Время приготовления должно быть больше 0')


def validate_positive_amount(value):
    """Валидация количества ингредиента."""
    if value <= 0:
        raise ValidationError('Количество должно быть больше 0')


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(max_length=200, db_index=True)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега рецепта."""

    name = models.CharField(max_length=200, unique=True, db_index=True)
    color = models.CharField(max_length=7, validators=[validate_hex_color])
    slug = models.SlugField(max_length=200, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientInRecipe')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField(
        validators=[validate_positive_cooking_time]
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created']

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Промежуточная модель для связи рецепта и ингредиента."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        validators=[validate_positive_amount]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.ingredient.name} - {self.amount}"


class BaseUserRecipeModel(models.Model):
    """Базовая модель для связи пользователя и рецепта."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Favorite(BaseUserRecipeModel):
    """Модель избранных рецептов."""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"


class ShoppingCart(BaseUserRecipeModel):
    """Модель корзины покупок."""

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"


class Subscribe(models.Model):
    """Модель подписок на пользователей."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'author')

    def clean(self):
        """Проверка на самоподписку."""
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя')

    def __str__(self):
        return f"{self.user.username} -> {self.author.username}"
