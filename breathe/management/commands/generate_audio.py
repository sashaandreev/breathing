"""
Django management command to generate TTS audio files for breathing techniques.

This command generates all required Russian audio files using gTTS:
- Phase cues: inhale, exhale, hold
- Number counts: 1-10

Usage:
    python manage.py generate_audio
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import os


class Command(BaseCommand):
    help = 'Generate TTS audio files for breathing techniques using gTTS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--provider',
            type=str,
            default='gtts',
            choices=['gtts', 'google_cloud'],
            help='TTS provider to use (default: gtts)',
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default=None,
            help='Output directory for audio files (default: static/audio/ru/)',
        )
        parser.add_argument(
            '--slow',
            action='store_true',
            help='Use slow speech (default: False)',
        )

    def handle(self, *args, **options):
        provider = options['provider']
        output_dir = options['output_dir']
        slow = options['slow']

        # Determine output directory
        if output_dir:
            audio_dir = Path(output_dir)
        else:
            audio_dir = Path(settings.BASE_DIR) / 'static' / 'audio' / 'ru'

        # Create output directory if it doesn't exist
        audio_dir.mkdir(parents=True, exist_ok=True)
        self.stdout.write(f'Output directory: {audio_dir}')

        # Check if gTTS is available
        if provider == 'gtts':
            try:
                from gtts import gTTS
            except ImportError:
                self.stdout.write(
                    self.style.ERROR(
                        'gTTS is not installed. Install it with: pip install gTTS'
                    )
                )
                return

        # Define audio files to generate
        phase_cues = {
            'phase_inhale': 'Вдох',
            'phase_exhale': 'Выдох',
            'phase_hold': 'Задержка',
        }

        number_counts = {
            1: 'Один',
            2: 'Два',
            3: 'Три',
            4: 'Четыре',
            5: 'Пять',
            6: 'Шесть',
            7: 'Семь',
            8: 'Восемь',
            9: 'Девять',
            10: 'Десять',
        }

        total_files = len(phase_cues) + len(number_counts)
        generated = 0
        errors = []

        # Generate phase cues
        self.stdout.write(self.style.SUCCESS('\nGenerating phase cues...'))
        for filename, text in phase_cues.items():
            output_path = audio_dir / f'{filename}.mp3'
            try:
                if provider == 'gtts':
                    self._generate_gtts(text, output_path, slow)
                    generated += 1
                    self.stdout.write(f'  ✓ {filename}.mp3 - "{text}"')
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ {filename}.mp3 - Google Cloud TTS not implemented yet'
                        )
                    )
            except Exception as e:
                error_msg = f'  ✗ {filename}.mp3 - Error: {str(e)}'
                self.stdout.write(self.style.ERROR(error_msg))
                errors.append(error_msg)

        # Generate number counts
        self.stdout.write(self.style.SUCCESS('\nGenerating number counts...'))
        for num, text in number_counts.items():
            filename = f'count_{num}'
            output_path = audio_dir / f'{filename}.mp3'
            try:
                if provider == 'gtts':
                    self._generate_gtts(text, output_path, slow)
                    generated += 1
                    self.stdout.write(f'  ✓ {filename}.mp3 - "{text}"')
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ {filename}.mp3 - Google Cloud TTS not implemented yet'
                        )
                    )
            except Exception as e:
                error_msg = f'  ✗ {filename}.mp3 - Error: {str(e)}'
                self.stdout.write(self.style.ERROR(error_msg))
                errors.append(error_msg)

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n{"="*50}'))
        self.stdout.write(self.style.SUCCESS(f'Summary:'))
        self.stdout.write(f'  Total files: {total_files}')
        self.stdout.write(f'  Generated: {generated}')
        if errors:
            self.stdout.write(self.style.ERROR(f'  Errors: {len(errors)}'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ All files generated successfully!'))
        self.stdout.write(self.style.SUCCESS(f'{"="*50}'))

        if errors:
            self.stdout.write(self.style.ERROR('\nErrors encountered:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  {error}'))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'\nAll audio files have been generated in: {audio_dir}'
            )
        )

    def _generate_gtts(self, text, output_path, slow=False):
        """Generate audio file using gTTS."""
        from gtts import gTTS

        # Create gTTS object
        tts = gTTS(text=text, lang='ru', slow=slow)

        # Save to file
        tts.save(str(output_path))

        # Verify file was created
        if not output_path.exists():
            raise Exception(f'File was not created: {output_path}')

