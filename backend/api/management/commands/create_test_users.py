from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает тестовых пользователей'

    def handle(self, *args, **options):
        # Создаем тестовых пользователей
        users_data = [
            {
                'username': 'chef_maria',
                'email': 'maria@example.com',
                'first_name': 'Мария',
                'last_name': 'Петрова'
            },
            {
                'username': 'cook_alex',
                'email': 'alex@example.com',
                'first_name': 'Алексей',
                'last_name': 'Сидоров'
            },
            {
                'username': 'food_lover',
                'email': 'anna@example.com',
                'first_name': 'Анна',
                'last_name': 'Козлова'
            },
            {
                'username': 'kitchen_master',
                'email': 'dmitry@example.com',
                'first_name': 'Дмитрий',
                'last_name': 'Волков'
            },
            {
                'username': 'recipe_queen',
                'email': 'elena@example.com',
                'first_name': 'Елена',
                'last_name': 'Морозова'
            }
        ]

        created_count = 0

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )

            if created:
                user.set_password('testpass123')
                user.save()
                created_count += 1
                self.stdout.write(f'Создан пользователь: {user.username}')
            else:
                self.stdout.write(
                    f'Пользователь уже существует: {user.username}')

        self.stdout.write(
            self.style.SUCCESS(f'Создано {created_count} новых пользователей!')
        )
