# Breathe & Resist

A Django-based web application for tracking smoking cessation progress and guided breathing exercises.

## Features

- **Activity Tracker**: Log resistance, relapses, and physical activity
- **Breathing Techniques**: 18 guided breathing exercises across 6 categories
- **Session History**: Track and analyze breathing session data
- **Mobile-First Design**: Optimized for portrait mobile devices
- **Russian Localization**: Full Russian language support

## Requirements

- Python 3.8+
- Django 6.0
- PostgreSQL (production) or SQLite (development)
- Virtual environment (recommended)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd breathing
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root (copy from `.env.example` if available):

```bash
# Copy example file (if exists)
cp .env.example .env
```

**Required for Production:**

```env
# Django Secret Key (CRITICAL - Generate a new one!)
SECRET_KEY=your-secret-key-here

# Debug Mode (MUST be False in production)
DEBUG=False

# Allowed Hosts (comma-separated)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

**Optional (for development, defaults are provided):**

```env
# For development, these have defaults
# SECRET_KEY=django-insecure-... (development only)
# DEBUG=True (development only)
# ALLOWED_HOSTS= (empty for development)
```

**Database Configuration (Production Only):**

```env
# Option 1: DATABASE_URL (Recommended)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Option 2: Individual credentials
DB_ENGINE=postgresql
DB_NAME=breathing_db
DB_USER=breathing_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

**Note:** For development, SQLite is used by default (no database configuration needed).

**Text-to-Speech (Optional):**

No configuration needed! The project uses gTTS by default (free, no API keys required).

If you want to use Google Cloud TTS instead:
```env
TTS_PROVIDER=google_cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
# OR
GOOGLE_TTS_API_KEY=your-api-key
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 6. Load Initial Data

Load breathing categories and techniques:

```bash
python manage.py load_breathing_data
```

This loads:
- 6 Breathing Categories
- 18 Breathing Techniques

To clear existing data and reload:
```bash
python manage.py load_breathing_data --clear
```

### 7. Generate Audio Files

Generate Russian TTS audio files for breathing cues:

```bash
python manage.py generate_audio
```

This creates:
- 3 phase cues: `phase_inhale.mp3`, `phase_exhale.mp3`, `phase_hold.mp3`
- 10 number counts: `count_1.mp3` through `count_10.mp3`

All files are saved to `static/audio/ru/`

**Note:** Requires internet connection and gTTS library (installed via requirements.txt).

### 8. Collect Static Files (Production)

```bash
python manage.py collectstatic
```

### 9. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Quick Start Checklist

After installation, run these commands in order:

```bash
# 1. Activate virtual environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Load initial data
python manage.py load_breathing_data

# 6. Generate audio files
python manage.py generate_audio

# 7. Run server
python manage.py runserver
```

## Project Structure

```
breathing/
├── breathe/              # Breathing techniques app
│   ├── fixtures/         # Initial data (categories + techniques)
│   ├── management/       # Custom management commands
│   │   └── commands/
│   │       ├── generate_audio.py      # Generate TTS audio files
│   │       └── load_breathing_data.py # Load initial data
│   ├── models.py         # BreathingCategory, BreathingTechnique, BreathingSession
│   └── views.py          # Breathing-related views
├── tracker/              # Activity tracking app
│   ├── models.py         # ActivityLog model
│   └── views.py          # Home view, activity tap endpoint
├── static/               # Static files (CSS, JS, audio)
│   ├── css/
│   ├── js/
│   └── audio/ru/         # Generated TTS audio files
├── templates/            # HTML templates
├── breathing/            # Django project settings
│   └── settings.py       # Main settings file
├── .env                  # Environment variables (not in git)
├── requirements.txt      # Python dependencies
└── manage.py             # Django management script
```

## Management Commands

### Load Breathing Data

```bash
# Load categories and techniques
python manage.py load_breathing_data

# Clear existing data and reload
python manage.py load_breathing_data --clear
```

### Generate Audio Files

```bash
# Generate all audio files (default: gTTS)
python manage.py generate_audio

# Use slow speech
python manage.py generate_audio --slow

# Custom output directory
python manage.py generate_audio --output-dir /path/to/audio
```

## Accessing the Application

### Admin Interface

- URL: `http://127.0.0.1:8000/admin/`
- Login with the superuser account you created
- Session persists across the entire site after login

### User Interface

- **Home** (superuser only): `http://127.0.0.1:8000/`
  - Activity tracker with counters
  - Link to breathing menu
- **Breathing Menu**: `http://127.0.0.1:8000/breathe/`
  - Available to all users (no login required)
  - Browse categories and techniques

## Environment Variables Reference

See `docs/ENVIRONMENT_VARIABLES.md` for detailed information about all environment variables.

### Quick Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Production: Yes | Dev default | Django secret key |
| `DEBUG` | Production: Yes | `True` | Debug mode |
| `ALLOWED_HOSTS` | Production: Yes | Empty | Allowed hostnames |
| `DATABASE_URL` | Production: Optional | None | PostgreSQL connection string |
| `TTS_PROVIDER` | No | `gtts` | TTS provider (`gtts` or `google_cloud`) |

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Django Shell

```bash
python manage.py shell
```

## Production Deployment

### Key Steps

1. Set `DEBUG=False` in environment variables
2. Set a strong `SECRET_KEY` (generate new one)
3. Configure `ALLOWED_HOSTS`
4. Set up PostgreSQL database
5. Run `collectstatic`
6. Configure web server (Nginx, Apache, etc.)
7. Set up process manager (systemd, supervisor, etc.)

### Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (not the default)
- [ ] `ALLOWED_HOSTS` configured
- [ ] Database credentials secure
- [ ] HTTPS enabled
- [ ] Static files served via CDN (Cloudflare recommended)
- [ ] Environment variables not in version control

## Troubleshooting

### "ModuleNotFoundError: No module named 'gTTS'"

```bash
pip install gTTS
```

### "Fixture file not found"

Make sure you're running the command from the project root directory:
```bash
python manage.py load_breathing_data
```

### "No such table" errors

Run migrations:
```bash
python manage.py migrate
```

### Audio generation fails

- Check internet connection (gTTS requires internet)
- Verify gTTS is installed: `pip install gTTS`
- Check output directory permissions

## Documentation

- `docs/BUSINESS_REQUIREMENTS.md` - Project requirements
- `docs/DESIGN.md` - System design and architecture
- `docs/IMPLEMENTATION_PLAN.md` - Implementation phases
- `docs/ENVIRONMENT_VARIABLES.md` - Environment variables guide
- `docs/GTTS_SETUP.md` - gTTS setup guide
- `docs/GOOGLE_TTS_SETUP.md` - Google Cloud TTS setup (optional)

## License

[Add your license here]

## Support

[Add support contact information here]

