from .models import (
    Ingredient,
    IngredientInRecipe,
    Favorite,
    Recipe,
    ShoppingCart,
    Subscribe,
    Tag,
)
import logging
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .fields import Base64ImageField

logger = logging.getLogger(__name__)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя c индикатором подписки на автора."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscribe.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Добавляем полный URL для аватара с временной меткой
        if (representation.get('avatar')
                and self.context.get('request')):
            avatar_url = self.context['request'].build_absolute_uri(
                representation['avatar'])
            # Добавляем временную метку к URL аватара
            import time
            representation['avatar'] = (
                f"{avatar_url}?t={int(time.time())}")
        return representation


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя с проверками уникальности."""
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("Пользователь с таким email уже существует.")
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                _("Пользователь с таким именем уже существует.")
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
            is_active=True
        )
        return user


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега рецепта."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Убедимся, что цвет всегда в верхнем регистре (опционально)
        representation['color'] = representation['color'].upper()
        return representation


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор связи ингредиента с рецептом (чтение)."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для чтения.

    Важно: возможен N+1 при обращении к ингредиентам/тегам без
    предварительного select_related/prefetch_related на уровне views.
    Подходит для небольших выборок.
    """

    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set', many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Добавляем временную метку к URL изображения против кэширования
        if (representation.get('image')
                and self.context.get('request')):
            image_url = self.context['request'].build_absolute_uri(
                representation['image'])
            # Добавляем временную метку к URL изображения
            import time
            representation['image'] = (
                f"{image_url}?t={int(time.time())}")
        return representation


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного пользователя."""
    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор элемента корзины покупок."""
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/обновления рецепта."""
    class IngredientAmountInputSerializer(serializers.Serializer):
        """Входные данные ингредиента: id ингредиента и количество."""
        id = serializers.IntegerField()
        amount = serializers.IntegerField(min_value=1)

    ingredients = IngredientAmountInputSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'name', 'image', 'text', 'cooking_time',
            'ingredients', 'tags'
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "Должен быть хотя бы один ингредиент.")

        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться.")

        existing_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        if existing_ingredients.count() != len(ingredient_ids):
            raise serializers.ValidationError(
                "Один или несколько ингредиентов не найдены.")

        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                "Должен быть хотя бы один тег.")
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        recipe.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.ingredientinrecipe_set.all().delete()
            for ingredient_data in ingredients_data:
                IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredient_id=ingredient_data['id'],
                    amount=ingredient_data['amount']
                )

        return instance


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки пользователя на автора."""
    class Meta:
        model = Subscribe
        fields = '__all__'


class UserSubscriptionSerializer(UserSerializer):
    """Сериализатор автора с его рецептами и их количеством."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', None)

        recipes = obj.recipe_set.all().order_by('-created')
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass

        serializer = RecipeShortSerializer(
            recipes, many=True, context=self.context)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipe_set.count()


class RecipeShortSerializer(serializers.ModelSerializer):
    """Короткое представление рецепта (для списков/подписок)."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Добавляем полный URL для изображения с временной меткой
        if representation.get('image') and self.context.get('request'):
            image_url = self.context['request'].build_absolute_uri(
                representation['image'])
            # Добавляем временную метку к URL изображения
            import time
            representation['image'] = (
                f"{image_url}?t={int(time.time())}")
        return representation


class SetPasswordSerializer(serializers.Serializer):
    """Смена пароля текущего пользователя с проверкой текущего пароля."""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль')
        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {'confirm_password': 'Пароли не совпадают'})

        # стандартные валидаторы Django
        password_validation.validate_password(
            new_password, self.context['request'].user)

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class CustomTokenCreateSerializer(serializers.Serializer):
    """Кастомный сериализатор для создания токена с поддержкой email."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        logger.info(f"Token creation attempt for email: {email}")

        if email and password:
            # Пытаемся найти пользователя по email
            try:
                user = User.objects.get(email=email)
                logger.info(
                    f"User found: {user.email}, is_active: {user.is_active}")

                # Проверяем пароль
                if user.check_password(password) and user.is_active:
                    attrs['user'] = user
                    logger.info(f"Password validation successful for {email}")
                    return attrs
                else:
                    logger.warning(
                        f"Invalid password or inactive user for {email}")
                    raise serializers.ValidationError(
                        'Невозможно войти с предоставленными '
                        'учетными данными.'
                    )
            except User.DoesNotExist:
                logger.warning(f"User not found: {email}")
                raise serializers.ValidationError(
                    'Невозможно войти с предоставленными '
                    'учетными данными.'
                )
        else:
            logger.warning("Missing email or password")
            raise serializers.ValidationError(
                'Необходимо указать email и пароль.'
            )

    def create(self, validated_data):
        """Создает токен для пользователя."""
        from rest_framework.authtoken.models import Token
        user = validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return token
