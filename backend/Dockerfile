FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директории для статических и медиа файлов
RUN mkdir -p /app/staticfiles /app/mediafiles
RUN chmod -R 755 /app/staticfiles /app/mediafiles

# Создаем пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

USER appuser

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]