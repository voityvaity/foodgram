Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

## 🚀 Технологии

### Backend
- **Django 4.2** - веб-фреймворк
- **Django REST Framework** - API
- **PostgreSQL** - база данных
- **Gunicorn** - WSGI сервер
- **Docker** - контейнеризация

### Frontend
- **React 18** - пользовательский интерфейс
- **JavaScript (ES6+)** - язык программирования
- **CSS Modules** - стилизация
- **Docker** - контейнеризация

### Infrastructure
- **Nginx** - веб-сервер и прокси
- **Docker Compose** - оркестрация контейнеров
- **SSL/TLS** - безопасное соединение

## 📋 Функциональность

- 🔐 **Аутентификация и авторизация** - регистрация, вход, смена пароля
- 📝 **Управление рецептами** - создание, редактирование, удаление
- 🏷️ **Теги и ингредиенты** - категоризация и поиск
- ❤️ **Избранное** - сохранение понравившихся рецептов
- 🛒 **Список покупок** - формирование списка ингредиентов
- 👥 **Подписки** - слежение за авторами
- 📱 **Адаптивный дизайн** - работа на всех устройствах

## 🛠️ Установка и запуск

### Локальная разработка
```bash
cd infra
docker compose up -d
docker compose build
docker compose up -d
```

### Деплой на сервер
```bash
# Сборка образов
docker build -t your-username/foodgram-backend:latest backend/
docker build -t your-username/foodgram-frontend:latest frontend/
docker build -t your-username/foodgram-nginx:latest infra/

# Отправка в Docker Hub
docker push your-username/foodgram-backend:latest
docker push your-username/foodgram-frontend:latest
docker push your-username/foodgram-nginx:latest

# На сервере
docker-compose up -d
```

## 📚 API Документация
Полная документация API доступна по адресу `/api/docs/` после запуска проекта.

## 👨‍💻 Автор
**Егор Фенин** - [@resgep](https://t.me/resgep)

## 📝 Лицензия
MIT License

