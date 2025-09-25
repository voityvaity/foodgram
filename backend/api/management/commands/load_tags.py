from django.core.management.base import BaseCommand
from api.models import Tag


class Command(BaseCommand):
    help = 'Load default tags'

    def handle(self, *args, **options):
        self.stdout.write('Loading default tags...')
        
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

        created_count = 0
        for tag_data in tags_data:
            if self._validate_color(tag_data['color']):
                tag, created = Tag.objects.get_or_create(
                    slug=tag_data['slug'],
                    defaults={
                        'name': tag_data['name'],
                        'color': tag_data['color']
                    }
                )
                if created:
                    self.stdout.write(f'Created tag: {tag.name}')
                    created_count += 1
                else:
                    self.stdout.write(f'Tag already exists: {tag.name}')
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Invalid color format: {tag_data["color"]}'
                    )
                )

        self.stdout.write(f'Created {created_count} new tags')
        self.stdout.write(f'Total tags: {Tag.objects.count()}')

    def _validate_color(self, color):
        """Валидация hex цвета."""
        if not color.startswith('#'):
            return False
        if len(color) != 7:
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
