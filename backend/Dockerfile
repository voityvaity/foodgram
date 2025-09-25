FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        curl \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

# Копируем и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директории для статических и медиа файлов
RUN mkdir -p /app/staticfiles /app/mediafiles /app/data /app/logs && \
    chmod -R 755 /app/staticfiles /app/mediafiles /app/data /app/logs && \
    chown -R appuser:appuser /app

USER appuser

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/ || exit 1

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]