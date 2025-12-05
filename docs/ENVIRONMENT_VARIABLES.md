# Environment Variables Guide

This document explains which settings should be stored as environment variables for security and configuration management.

## Required Environment Variables

### 1. `SECRET_KEY` ⚠️ **CRITICAL**
- **Purpose**: Django's secret key used for cryptographic signing
- **Why**: If exposed, attackers can forge session tokens, CSRF tokens, and more
- **Development**: Has a fallback default (for development only)
- **Production**: **MUST** be set to a unique, random value
- **Generate**: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### 2. `DEBUG`
- **Purpose**: Enable/disable Django debug mode
- **Development**: `True` (default)
- **Production**: **MUST** be `False`
- **Why**: Debug mode exposes sensitive information and should never be enabled in production

### 3. `ALLOWED_HOSTS`
- **Purpose**: List of hosts/domains that Django can serve
- **Development**: Empty (default)
- **Production**: Comma-separated list (e.g., `yourdomain.com,www.yourdomain.com`)
- **Why**: Prevents HTTP Host header attacks

## Database Configuration (Production Only)

### Option 1: `DATABASE_URL` (Recommended)
- **Format**: `postgresql://user:password@host:port/dbname`
- **Example**: `postgresql://breathing_user:password123@localhost:5432/breathing_db`
- **Why**: Single variable, works well with cloud providers (DigitalOcean, Heroku, etc.)

### Option 2: Individual Database Variables
- `DB_ENGINE`: `postgresql` (to enable PostgreSQL)
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host (default: `localhost`)
- `DB_PORT`: Database port (default: `5432`)

**Note**: For development, leave these empty to use SQLite.

## Text-to-Speech Configuration (Future Implementation)

### ✅ gTTS (Default - Recommended)
- **No environment variables needed!**
- **No API keys needed!**
- Just install: `pip install gTTS`
- That's it - works out of the box
- **See**: `docs/GTTS_SETUP.md` for details

### Optional: Google Cloud Text-to-Speech API
**Only needed if you want to use Google Cloud TTS instead of gTTS:**
- `TTS_PROVIDER`: Set to `'google_cloud'` (default is `'gtts'`)
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON file
- OR `GOOGLE_TTS_API_KEY`: Google Cloud TTS API key
- **See**: `docs/GOOGLE_TTS_SETUP.md` for setup instructions

**For this project, you don't need any of these - gTTS is sufficient!**

## Setup Instructions

### 1. Create `.env` file
```bash
cp .env.example .env
```

### 2. Edit `.env` file
Fill in your actual values (never commit this file to git!)

### 3. For Production
Set environment variables on your hosting platform:
- **DigitalOcean**: Use App Platform environment variables or manually set in server
- **Heroku**: `heroku config:set SECRET_KEY=your-key`
- **Other platforms**: Check their documentation for setting environment variables

## Security Best Practices

1. ✅ **Never commit `.env` to version control** (already in `.gitignore`)
2. ✅ **Use different `SECRET_KEY` for each environment** (dev, staging, production)
3. ✅ **Rotate `SECRET_KEY` if it's ever exposed**
4. ✅ **Use strong database passwords** (at least 16 characters, mix of letters, numbers, symbols)
5. ✅ **Limit database user permissions** (only grant necessary permissions)
6. ✅ **Use service accounts for Google Cloud** (not API keys) in production
7. ✅ **Review `.env.example`** to document all required variables

## Current Status

- ✅ `SECRET_KEY` - Uses environment variable with development fallback
- ✅ `DEBUG` - Uses environment variable
- ✅ `ALLOWED_HOSTS` - Uses environment variable
- ✅ Database - Supports both SQLite (dev) and PostgreSQL (prod) via env vars
- ⏳ `GOOGLE_TTS_API_KEY` - Ready for when TTS is implemented

## Testing Environment Variables

To verify your environment variables are loaded correctly:

```python
# In Django shell: python manage.py shell
from django.conf import settings
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"SECRET_KEY: {'*' * 20} (hidden)")
```

