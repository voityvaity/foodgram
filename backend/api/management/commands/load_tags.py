from django.core.management.base import BaseCommand
from api.models import Tag
from api.constants import TAG_COLORS


class Command(BaseCommand):
    help = 'Load default tags'

    def handle(self, *args, **options):
        # Создаем стандартные теги для рецептов
        tags_data = [
            {
                'name': 'Завтрак',
                'color': TAG_COLORS['breakfast'],
                'slug': 'breakfast'
            },
            {
                'name': 'Обед',
                'color': TAG_COLORS['lunch'],
                'slug': 'lunch'
            },
            {
                'name': 'Ужин',
                'color': TAG_COLORS['dinner'],
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
