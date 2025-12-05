"""
Django management command to load initial breathing categories and techniques.

This command loads the fixture file containing:
- 6 Breathing Categories
- 18 Breathing Techniques

Usage:
    python manage.py load_breathing_data
    python manage.py load_breathing_data --clear  # Clear existing data first
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.management.color import no_style
from breathe.models import BreathingCategory, BreathingTechnique
from pathlib import Path
import os


class Command(BaseCommand):
    help = 'Load initial breathing categories and techniques from fixture file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing categories and techniques before loading',
        )
        parser.add_argument(
            '--fixture',
            type=str,
            default='breathing_techniques.json',
            help='Fixture file name (default: breathing_techniques.json)',
        )

    def handle(self, *args, **options):
        clear = options['clear']
        fixture_name = options['fixture']

        # Find fixture file
        fixture_path = Path(__file__).parent.parent.parent / 'fixtures' / fixture_name

        if not fixture_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f'Fixture file not found: {fixture_path}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Expected location: breathe/fixtures/breathing_techniques.json'
                )
            )
            return

        # Show current counts
        categories_count = BreathingCategory.objects.count()
        techniques_count = BreathingTechnique.objects.count()

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Loading Breathing Data'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'\nCurrent data:')
        self.stdout.write(f'  Categories: {categories_count}')
        self.stdout.write(f'  Techniques: {techniques_count}')

        # Clear existing data if requested
        if clear:
            if categories_count > 0 or techniques_count > 0:
                self.stdout.write(
                    self.style.WARNING('\nClearing existing data...')
                )
                BreathingTechnique.objects.all().delete()
                BreathingCategory.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('  ✓ Existing data cleared')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('\nNo existing data to clear')
                )

        # Load fixture
        self.stdout.write(
            self.style.SUCCESS(f'\nLoading fixture: {fixture_name}')
        )

        try:
            # Use Django's loaddata command
            call_command(
                'loaddata',
                fixture_name,
                app_label='breathe',
                verbosity=1,
            )

            # Verify what was loaded
            new_categories_count = BreathingCategory.objects.count()
            new_techniques_count = BreathingTechnique.objects.count()

            categories_added = new_categories_count - categories_count
            techniques_added = new_techniques_count - techniques_count

            self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
            self.stdout.write(self.style.SUCCESS('Summary:'))
            self.stdout.write(f'  Categories loaded: {categories_added}')
            self.stdout.write(f'  Techniques loaded: {techniques_added}')
            self.stdout.write(f'\nTotal in database:')
            self.stdout.write(f'  Categories: {new_categories_count}')
            self.stdout.write(f'  Techniques: {new_techniques_count}')

            # Show categories
            if new_categories_count > 0:
                self.stdout.write(self.style.SUCCESS('\nCategories:'))
                for category in BreathingCategory.objects.all().order_by('pk'):
                    technique_count = category.techniques.count()
                    self.stdout.write(
                        f'  {category.pk}. {category.name_ru} '
                        f'({technique_count} technique{"s" if technique_count != 1 else ""})'
                    )

            self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
            self.stdout.write(
                self.style.SUCCESS('✓ Data loaded successfully!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\nError loading fixture: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING(
                    '\nMake sure:'
                    '\n  1. Migrations are applied (python manage.py migrate)'
                    '\n  2. Fixture file exists and is valid JSON'
                    '\n  3. All required fields are present in fixture'
                )
            )
            raise

