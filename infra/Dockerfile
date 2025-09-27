# nginx Dockerfile
FROM nginx:1.22.1

# Установка необходимых пакетов для генерации SSL сертификатов
RUN apt-get update && apt-get install -y openssl

# Создание директорий для SSL сертификатов
RUN mkdir -p /etc/ssl/certs /etc/ssl/private

# Генерация самоподписанного SSL сертификата
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt \
    -subj "/C=RU/ST=State/L=City/O=Organization/CN=localhost"

COPY nginx.conf /etc/nginx/templates/default.conf.template
