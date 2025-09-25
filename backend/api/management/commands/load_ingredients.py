import csv
import json
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from api.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from CSV or JSON'

    def handle(self, *args, **options):
        data_dir = Path('/app/data')

        self.stdout.write(f'Data directory: {data_dir}')
        self.stdout.write(f'Data directory exists: {data_dir.exists()}')
        self.stdout.write(
            f'Files in data directory: {list(data_dir.iterdir())}')

        # Загрузка из CSV
        csv_path = data_dir / 'ingredients.csv'
        self.stdout.write(f'CSV path: {csv_path}')
        self.stdout.write(f'CSV exists: {csv_path.exists()}')
        if csv_path.exists():
            self.stdout.write('Loading from CSV...')
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                count = 0
                for row in reader:
                    if len(row) >= 2:
                        Ingredient.objects.get_or_create(
                            name=row[0],
                            measurement_unit=row[1]
                        )
                        count += 1
                self.stdout.write(f'Loaded {count} ingredients from CSV')
        else:
            self.stdout.write(self.style.WARNING('CSV file not found'))

        # Загрузка из JSON
        json_path = data_dir / 'ingredients.json'
        self.stdout.write(f'JSON path: {json_path}')
        self.stdout.write(f'JSON exists: {json_path.exists()}')
        if json_path.exists():
            self.stdout.write('Loading from JSON...')
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                count = 0
                for item in data:
                    Ingredient.objects.get_or_create(
                        name=item['name'],
                        measurement_unit=item['measurement_unit']
                    )
                    count += 1
                self.stdout.write(f'Loaded {count} ingredients from JSON')
        else:
            self.stdout.write(self.style.WARNING('JSON file not found'))
