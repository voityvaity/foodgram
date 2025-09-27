# Константы для валидации времени приготовления
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000

# Константы пагинации
DEFAULT_PAGE_SIZE = 6
MAX_PAGE_SIZE = 999

# Константы для подписок
DEFAULT_RECIPES_LIMIT = 3

# Константы для тегов (цвета)
TAG_COLORS = {
    'breakfast': '#E26C2D',
    'lunch': '#49B64E',
    'dinner': '#8775D2'
}

# Константы для фильтрации
FILTER_TRUE_VALUE = '1'
FILTER_FALSE_VALUE = '0'

# Константы для HTTP заголовков
CACHE_EXPIRES = '0'
CONTENT_TYPE_TEXT_PLAIN = 'text/plain; charset=utf-8'
BASE64_SEPARATOR = ';base64,'

# Константы для валидации
MIN_INGREDIENT_AMOUNT = 1

# Константы для полей сериализаторов
FIELDS_ALL = '__all__'
WRITE_ONLY = 'write_only'
READ_ONLY = 'read_only'
REQUIRED = 'required'

# Константы для сообщений об ошибках
ERROR_EMAIL_EXISTS = "Пользователь с таким email уже существует."
ERROR_USERNAME_EXISTS = "Пользователь с таким именем уже существует."
ERROR_NO_INGREDIENTS = "Должен быть хотя бы один ингредиент."
ERROR_NO_TAGS = "Должен быть хотя бы один тег."
ERROR_DUPLICATE_INGREDIENTS = "Ингредиенты не должны повторяться."
ERROR_INGREDIENTS_NOT_FOUND = "Один или несколько ингредиентов не найдены."
ERROR_WRONG_PASSWORD = "Неверный текущий пароль"
ERROR_PASSWORDS_NOT_MATCH = "Пароли не совпадают"
