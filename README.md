# Foodgram

Foodgram — сервис рецептов с REST API. Пользователь может публиковать рецепты, собирать избранное, подписываться на авторов и формировать список покупок с суммированием ингредиентов.

## Что реализовано

- регистрация и токен-аутентификация пользователей;
- создание, просмотр, изменение и удаление рецептов;
- поиск ингредиентов и фильтрация рецептов по тегам;
- избранное, подписки и список покупок;
- загрузка изображений и выгрузка списка ингредиентов;
- разграничение прав на изменение объектов;
- API-документация;
- контейнерный запуск backend, frontend, PostgreSQL и Nginx;
- автоматические проверки backend в GitHub Actions.

## Стек

- Backend: Python 3.11, Django 3.2, Django REST Framework, Djoser, PostgreSQL, Gunicorn.
- Frontend: React 17, JavaScript, CSS Modules.
- Инфраструктура: Docker, Docker Compose, Nginx.
- Проверки: Django test runner, Flake8, GitHub Actions.

## Архитектура

- `backend/` — модели, сериализаторы, permissions, viewsets, фильтры и API-тесты;
- `frontend/` — клиентское приложение;
- `infra/` — локальная Docker Compose-конфигурация и Nginx;
- `data/` — исходные данные ингредиентов;
- `docs/` — OpenAPI-схема и документация;
- `postman_collection/` — коллекция запросов для ручной проверки API.

## Локальный запуск через Docker

1. Склонируйте репозиторий.
2. Скопируйте `.env.example` в `infra/.env` и замените демонстрационные значения.
3. Запустите сервисы:

```bash
cd infra
docker compose up --build
```

После запуска приложение доступно на `http://localhost:8080/`, документация API — на `http://localhost:8080/api/docs/`.

## Проверки backend без PostgreSQL

Для быстрых локальных проверок и CI предусмотрен режим SQLite:

```powershell
$env:USE_SQLITE = "1"
$env:SECRET_KEY = "local-test-key"
cd backend
python manage.py check
python manage.py test api
```

Основной Docker-запуск использует PostgreSQL.

## Что демонстрирует проект

Проект показывает проектирование REST API на Django REST Framework, моделирование связей в базе данных, валидацию и разграничение доступа, работу со списком покупок, контейнеризацию и настройку reverse proxy.

## Автор

Егор Фенин — [voityvaity](https://github.com/voityvaity)
