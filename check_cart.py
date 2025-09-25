#!/usr/bin/env python
import os
import sys
import django

# Добавляем путь к Django проекту
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from api.models import ShoppingCart, User, Recipe

print("=== Проверка корзины ===")
print(f"Общее количество записей в корзине: {ShoppingCart.objects.count()}")

# Проверяем по пользователям
users = User.objects.all()
for user in users:
    cart_items = ShoppingCart.objects.filter(user=user)
    print(f"Пользователь {user.username}: {cart_items.count()} рецептов в корзине")
    for item in cart_items:
        print(f"  - {item.recipe.name}")

# Проверяем дубликаты
from django.db.models import Count
duplicates = ShoppingCart.objects.values('user', 'recipe').annotate(count=Count('id')).filter(count__gt=1)
if duplicates.exists():
    print("\n=== ДУБЛИКАТЫ НАЙДЕНЫ ===")
    for dup in duplicates:
        print(f"User {dup['user']}, Recipe {dup['recipe']}: {dup['count']} записей")
else:
    print("\nДубликатов не найдено")
