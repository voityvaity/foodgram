# Как добавить фотографии рецептов

## Способ 1: Через Django Admin (Рекомендуется)

1. Откройте админку: `http://localhost:8080/admin/`
2. Войдите как суперпользователь
3. Перейдите в раздел "Recipes"
4. Выберите рецепт для редактирования
5. В поле "Image" нажмите "Choose File"
6. Выберите изображение (JPG, PNG, WebP)
7. Нажмите "Save"

## Способ 2: Через API

### Загрузка изображения через API:

```bash
# 1. Получите токен авторизации
curl -X POST http://localhost:8080/api/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your_password"}'

# 2. Создайте рецепт с изображением
curl -X POST http://localhost:8080/api/recipes/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "name=Название рецепта" \
  -F "text=Описание рецепта" \
  -F "cooking_time=30" \
  -F "image=@/path/to/image.jpg" \
  -F "tags=1,2,3" \
  -F "ingredients=[{\"id\": 1, \"amount\": 100}]"
```

## Способ 3: Программно через Django Shell

```python
# В Django shell
from api.models import Recipe
from django.core.files import File

# Откройте рецепт
recipe = Recipe.objects.get(name="Борщ украинский")

# Загрузите изображение
with open('/path/to/borch.jpg', 'rb') as f:
    recipe.image.save('borch.jpg', File(f), save=True)
```

## Способ 4: Массовая загрузка через Management Command

Создайте команду `load_recipe_images.py`:

```python
import os
from django.core.management.base import BaseCommand
from api.models import Recipe
from django.core.files import File

class Command(BaseCommand):
    def handle(self, *args, **options):
        images_dir = '/path/to/images/'
        
        for recipe in Recipe.objects.all():
            image_name = f"{recipe.name.lower().replace(' ', '_')}.jpg"
            image_path = os.path.join(images_dir, image_name)
            
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    recipe.image.save(image_name, File(f), save=True)
                print(f"Загружено изображение для: {recipe.name}")
```

## Требования к изображениям

- **Формат:** JPG, PNG, WebP
- **Размер:** Рекомендуется 800x600 пикселей
- **Вес:** Не более 5 МБ
- **Название:** Лучше использовать латинские символы

## Структура папки с изображениями

```
images/
├── borch_ukrainskiy.jpg
├── pasta_carbonara.jpg
├── omlet_s_syrom.jpg
├── salad_cezar.jpg
├── pizza_margarita.jpg
├── tvorozhnaya_zapekanka.jpg
├── grecheskiy_salat.jpg
├── plov_uzbekskiy.jpg
├── blinchiki_s_tvorogom.jpg
├── sup_pure_iz_tykvy.jpg
├── shashlyk_iz_svininy.jpg
└── tiramisu.jpg
```

## Автоматическая загрузка

Для автоматической загрузки изображений при создании рецептов:

1. Поместите изображения в папку `media/recipes/`
2. Запустите команду: `python manage.py load_recipe_images`
3. Изображения будут автоматически привязаны к рецептам

## Проверка загрузки

После загрузки изображения будут доступны по адресам:
- `http://localhost:8080/media/recipes/image_name.jpg`
- `https://foodgram.bazooza.ru/media/recipes/image_name.jpg`
