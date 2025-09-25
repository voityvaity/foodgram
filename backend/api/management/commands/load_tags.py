from django.core.management.base import BaseCommand
from api.models import Tag


class Command(BaseCommand):
    help = 'Load default tags'

    def handle(self, *args, **options):
        # Создаем стандартные теги для рецептов
        tags_data = [
            {
                'name': 'Завтрак',
                'color': '#E26C2D',
                'slug': 'breakfast'
            },
            {
                'name': 'Обед',
                'color': '#49B64E',
                'slug': 'lunch'
            },
            {
                'name': 'Ужин',
                'color': '#8775D2',
                'slug': 'dinner'
            }
        ]

        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults={
                    'name': tag_data['name'],
                    'color': tag_data['color']
                }
            )
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
            else:
                self.stdout.write(f'Tag already exists: {tag.name}')

        self.stdout.write(f'Total tags: {Tag.objects.count()}')
