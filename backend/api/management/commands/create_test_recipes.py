import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from api.models import Recipe, Tag, Ingredient, IngredientInRecipe

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает тестовые рецепты с ингредиентами и тегами'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=12,
            help='Количество рецептов для создания'
        )

    def handle(self, *args, **options):
        count = options['count']

        # Получаем существующие данные
        users = User.objects.all()
        tags = Tag.objects.all()
        ingredients = Ingredient.objects.all()

        if not users.exists():
            self.stdout.write(
                self.style.ERROR(
                    'Нет пользователей! Создайте пользователей сначала.')
            )
            return

        if not tags.exists():
            self.stdout.write(
                self.style.ERROR(
                    'Нет тегов! Запустите: python manage.py load_tags')
            )
            return

        if not ingredients.exists():
            self.stdout.write(
                self.style.ERROR(
                    'Нет ингредиентов! Запустите: '
                    'python manage.py load_ingredients')
            )
            return

        # Список рецептов для создания
        recipes_data = [
            {
                'name': 'Борщ украинский',
                'text': ('Классический украинский борщ с говядиной и свеклой. '
                         'Подается со сметаной и зеленью.'),
                'cooking_time': 120,
                'ingredients': [
                    {'name': 'Говядина', 'amount': 500},
                    {'name': 'Свекла', 'amount': 2},
                    {'name': 'Капуста', 'amount': 300},
                    {'name': 'Морковь', 'amount': 1},
                    {'name': 'Лук', 'amount': 1},
                    {'name': 'Картофель', 'amount': 3},
                    {'name': 'Томатная паста', 'amount': 2},
                    {'name': 'Чеснок', 'amount': 3},
                    {'name': 'Укроп', 'amount': 1},
                    {'name': 'Сметана', 'amount': 200}
                ],
                'tags': ['Обед']
            },
            {
                'name': 'Паста карбонара',
                'text': ('Итальянская паста с беконом, яйцами и пармезаном. '
                         'Классический рецепт из Рима.'),
                'cooking_time': 20,
                'ingredients': [
                    {'name': 'Спагетти', 'amount': 400},
                    {'name': 'Бекон', 'amount': 200},
                    {'name': 'Яйца', 'amount': 4},
                    {'name': 'Пармезан', 'amount': 100},
                    {'name': 'Чеснок', 'amount': 2},
                    {'name': 'Черный перец', 'amount': 1},
                    {'name': 'Соль', 'amount': 1}
                ],
                'tags': ['Обед']
            },
            {
                'name': 'Омлет с сыром',
                'text': ('Нежный омлет с сыром и зеленью. '
                         'Идеальный завтрак для всей семьи.'),
                'cooking_time': 10,
                'ingredients': [
                    {'name': 'Яйца', 'amount': 6},
                    {'name': 'Молоко', 'amount': 100},
                    {'name': 'Сыр', 'amount': 100},
                    {'name': 'Зелень', 'amount': 1},
                    {'name': 'Соль', 'amount': 1},
                    {'name': 'Масло сливочное', 'amount': 30}
                ],
                'tags': ['Завтрак']
            },
            {
                'name': 'Салат Цезарь',
                'text': ('Классический салат Цезарь с курицей, '
                         'сухариками и соусом. Легкий и сытный.'),
                'cooking_time': 25,
                'ingredients': [
                    {'name': 'Куриная грудка', 'amount': 300},
                    {'name': 'Салат романо', 'amount': 1},
                    {'name': 'Сухарики', 'amount': 100},
                    {'name': 'Пармезан', 'amount': 80},
                    {'name': 'Яйца', 'amount': 2},
                    {'name': 'Чеснок', 'amount': 2},
                    {'name': 'Горчица', 'amount': 1},
                    {'name': 'Лимонный сок', 'amount': 2},
                    {'name': 'Оливковое масло', 'amount': 50}
                ],
                'tags': ['Обед']
            },
            {
                'name': 'Пицца Маргарита',
                'text': ('Классическая итальянская пицца с томатами, '
                         'моцареллой и базиликом.'),
                'cooking_time': 45,
                'ingredients': [
                    {'name': 'Тесто для пиццы', 'amount': 500},
                    {'name': 'Томатный соус', 'amount': 200},
                    {'name': 'Моцарелла', 'amount': 200},
                    {'name': 'Базилик', 'amount': 1},
                    {'name': 'Оливковое масло', 'amount': 30},
                    {'name': 'Соль', 'amount': 1},
                    {'name': 'Орегано', 'amount': 1}
                ],
                'tags': ['Ужин']
            },
            {
                'name': 'Творожная запеканка',
                'text': ('Нежная творожная запеканка с изюмом. '
                         'Отличный десерт или завтрак.'),
                'cooking_time': 40,
                'ingredients': [
                    {'name': 'Творог', 'amount': 500},
                    {'name': 'Яйца', 'amount': 3},
                    {'name': 'Сахар', 'amount': 100},
                    {'name': 'Манная крупа', 'amount': 50},
                    {'name': 'Изюм', 'amount': 100},
                    {'name': 'Ванилин', 'amount': 1},
                    {'name': 'Сметана', 'amount': 100}
                ],
                'tags': ['Завтрак']
            },
            {
                'name': 'Греческий салат',
                'text': ('Свежий греческий салат с фетой, оливками и овощами. '
                         'Легкий и полезный.'),
                'cooking_time': 15,
                'ingredients': [
                    {'name': 'Помидоры', 'amount': 4},
                    {'name': 'Огурцы', 'amount': 2},
                    {'name': 'Лук красный', 'amount': 1},
                    {'name': 'Сыр фета', 'amount': 150},
                    {'name': 'Оливки', 'amount': 100},
                    {'name': 'Оливковое масло', 'amount': 50},
                    {'name': 'Лимонный сок', 'amount': 2},
                    {'name': 'Орегано', 'amount': 1}
                ],
                'tags': ['Обед']
            },
            {
                'name': 'Плов узбекский',
                'text': ('Настоящий узбекский плов с бараниной и морковью. '
                         'Традиционный рецепт.'),
                'cooking_time': 90,
                'ingredients': [
                    {'name': 'Баранина', 'amount': 600},
                    {'name': 'Рис', 'amount': 400},
                    {'name': 'Морковь', 'amount': 3},
                    {'name': 'Лук', 'amount': 2},
                    {'name': 'Чеснок', 'amount': 1},
                    {'name': 'Зира', 'amount': 1},
                    {'name': 'Барбарис', 'amount': 1},
                    {'name': 'Масло растительное', 'amount': 100}
                ],
                'tags': ['Обед']
            },
            {
                'name': 'Блинчики с творогом',
                'text': ('Тонкие блинчики с творожной начинкой. '
                         'Идеальный завтрак или десерт.'),
                'cooking_time': 30,
                'ingredients': [
                    {'name': 'Мука', 'amount': 200},
                    {'name': 'Яйца', 'amount': 3},
                    {'name': 'Молоко', 'amount': 500},
                    {'name': 'Творог', 'amount': 300},
                    {'name': 'Сахар', 'amount': 80},
                    {'name': 'Масло сливочное', 'amount': 50},
                    {'name': 'Соль', 'amount': 1}
                ],
                'tags': ['Завтрак']
            },
            {
                'name': 'Суп-пюре из тыквы',
                'text': ('Кремовый суп-пюре из тыквы с имбирем. '
                         'Согревающий и полезный.'),
                'cooking_time': 35,
                'ingredients': [
                    {'name': 'Тыква', 'amount': 800},
                    {'name': 'Лук', 'amount': 1},
                    {'name': 'Чеснок', 'amount': 2},
                    {'name': 'Имбирь', 'amount': 1},
                    {'name': 'Сливки', 'amount': 200},
                    {'name': 'Масло сливочное', 'amount': 30},
                    {'name': 'Соль', 'amount': 1},
                    {'name': 'Перец черный', 'amount': 1}
                ],
                'tags': ['Обед']
            },
            {
                'name': 'Шашлык из свинины',
                'text': ('Сочный шашлык из свиной шеи с луком и специями. '
                         'Для пикника или дачи.'),
                'cooking_time': 60,
                'ingredients': [
                    {'name': 'Свиная шея', 'amount': 1000},
                    {'name': 'Лук', 'amount': 3},
                    {'name': 'Чеснок', 'amount': 1},
                    {'name': 'Лимон', 'amount': 1},
                    {'name': 'Масло растительное', 'amount': 50},
                    {'name': 'Соль', 'amount': 1},
                    {'name': 'Перец черный', 'amount': 1},
                    {'name': 'Паприка', 'amount': 1}
                ],
                'tags': ['Ужин']
            },
            {
                'name': 'Тирамису',
                'text': ('Классический итальянский десерт тирамису '
                         'с маскарпоне и кофе.'),
                'cooking_time': 120,
                'ingredients': [
                    {'name': 'Маскарпоне', 'amount': 500},
                    {'name': 'Яйца', 'amount': 4},
                    {'name': 'Сахар', 'amount': 100},
                    {'name': 'Кофе эспрессо', 'amount': 200},
                    {'name': 'Печенье савоярди', 'amount': 200},
                    {'name': 'Какао', 'amount': 50},
                    {'name': 'Ликер', 'amount': 50}
                ],
                'tags': ['Ужин']
            }
        ]

        created_count = 0

        for i in range(min(count, len(recipes_data))):
            recipe_data = recipes_data[i]

            # Выбираем случайного пользователя
            author = random.choice(users)

            # Создаем рецепт
            recipe = Recipe.objects.create(
                name=recipe_data['name'],
                text=recipe_data['text'],
                cooking_time=recipe_data['cooking_time'],
                author=author,
                image='recipes/default_recipe.jpg'  # Заглушка
            )

            # Добавляем теги
            for tag_name in recipe_data['tags']:
                tag = tags.get(name=tag_name)
                recipe.tags.add(tag)

            # Добавляем ингредиенты
            for ingredient_data in recipe_data['ingredients']:
                try:
                    # Ищем точное совпадение по имени
                    ingredient = ingredients.get(
                        name__iexact=ingredient_data['name'])
                    IngredientInRecipe.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=ingredient_data['amount']
                    )
                except Ingredient.DoesNotExist:
                    # Если точное совпадение не найдено, ищем по частичному
                    try:
                        ingredient = ingredients.filter(
                            name__icontains=ingredient_data['name']
                        ).first()
                        if ingredient:
                            IngredientInRecipe.objects.create(
                                recipe=recipe,
                                ingredient=ingredient,
                                amount=ingredient_data['amount']
                            )
                    except Exception:
                        # Если ингредиент не найден, пропускаем
                        continue

            created_count += 1
            self.stdout.write(f'Создан рецепт: {recipe.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно создано {created_count} рецептов!')
        )
