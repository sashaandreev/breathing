# Google Cloud Text-to-Speech API Setup Guide

This guide explains how to set up Google Cloud Text-to-Speech API for generating audio files for breathing techniques.

## Overview

Google Cloud Text-to-Speech API allows you to generate audio files from text. For this project, it will be used to create Russian audio cues for breathing techniques.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. A GCP project (or create a new one)
3. Billing enabled on your GCP project (Text-to-Speech API requires billing)

## Option 1: Service Account (Recommended for Production)

Service accounts are more secure and recommended for production deployments.

### Step 1: Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Click **Create Service Account**
5. Fill in:
   - **Service account name**: `breathing-tts-service` (or any name you prefer)
   - **Service account ID**: Auto-generated
   - **Description**: "Service account for Text-to-Speech API"
6. Click **Create and Continue**

### Step 2: Grant Permissions

1. In **Grant this service account access to project**, add role:
   - **Cloud Text-to-Speech API User** (or `roles/cloudtts.user`)
2. Click **Continue**
3. Click **Done** (skip optional user access step)

### Step 3: Create and Download Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON** format
5. Click **Create**
6. The JSON key file will download automatically

### Step 4: Enable Text-to-Speech API

1. Go to [APIs & Services](https://console.cloud.google.com/apis/library)
2. Search for "Cloud Text-to-Speech API"
3. Click on it and click **Enable**

### Step 5: Configure in Your Project

1. Save the downloaded JSON file securely (e.g., `google-tts-service-account.json`)
2. **DO NOT commit this file to git** (it's already in `.gitignore`)
3. Set environment variable:
   ```bash
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-tts-service-account.json
   ```

**For DigitalOcean/Linux server:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/home/youruser/breathing/google-tts-service-account.json
```

**For local development (Windows):**
```bash
# In PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="D:\Private\breathing\google-tts-service-account.json"
```

**Or add to `.env` file:**
```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-tts-service-account.json
```

## Option 2: API Key (Simpler, Less Secure)

API keys are easier to set up but less secure. Use only for development or if service accounts aren't suitable.

### Step 1: Enable Text-to-Speech API

1. Go to [APIs & Services](https://console.cloud.google.com/apis/library)
2. Search for "Cloud Text-to-Speech API"
3. Click on it and click **Enable**

### Step 2: Create API Key

1. Go to [APIs & Services](https://console.cloud.google.com/apis/credentials) → **Credentials**
2. Click **Create Credentials** → **API Key**
3. Copy the generated API key
4. (Optional) Click **Restrict Key** to:
   - Restrict to "Cloud Text-to-Speech API" only
   - Restrict to specific IP addresses (for production)

### Step 3: Configure in Your Project

**Add to `.env` file:**
```
GOOGLE_TTS_API_KEY=your-api-key-here
```

## Pricing

Google Cloud Text-to-Speech API pricing (as of 2024):
- **Free tier**: First 0-4 million characters per month
- **Standard voices**: $4.00 per 1 million characters after free tier
- **WaveNet voices** (premium): $16.00 per 1 million characters after free tier

For this project, you'll likely stay within the free tier unless generating many audio files.

## Testing Your Setup

Once configured, you can test the API connection:

```python
# Test script (test_tts.py)
from google.cloud import texttospeech
import os

# For service account
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/service-account.json'

# Or for API key
# os.environ['GOOGLE_TTS_API_KEY'] = 'your-api-key'

client = texttospeech.TextToSpeechClient()

# Test synthesis
synthesis_input = texttospeech.SynthesisInput(text="Привет")
voice = texttospeech.VoiceSelectionParams(
    language_code="ru-RU",
    name="ru-RU-Wavenet-A"  # Russian WaveNet voice
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

response = client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)

print("Success! Audio generated.")
```

## Security Best Practices

1. ✅ **Never commit service account JSON files or API keys to git**
2. ✅ **Use service accounts for production** (not API keys)
3. ✅ **Restrict API keys** to specific APIs and IPs
4. ✅ **Rotate keys** if they're ever exposed
5. ✅ **Use least privilege** - only grant necessary permissions
6. ✅ **Store keys securely** - use environment variables or secret management services

## Troubleshooting

### Error: "Could not automatically determine credentials"

- Make sure `GOOGLE_APPLICATION_CREDENTIALS` points to the correct JSON file path
- Verify the JSON file is valid and not corrupted
- Check file permissions (should be readable)

### Error: "API not enabled"

- Enable "Cloud Text-to-Speech API" in Google Cloud Console
- Wait a few minutes after enabling for changes to propagate

### Error: "Permission denied"

- Verify the service account has "Cloud Text-to-Speech API User" role
- Check that billing is enabled on your GCP project

### Error: "Quota exceeded"

- Check your usage in [Google Cloud Console](https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/quotas)
- Consider upgrading your quota or waiting for the next billing cycle

## Next Steps

Once you have the credentials set up:

1. The TTS implementation will use these credentials automatically
2. Audio files will be generated and stored in `static/audio/ru/`
3. Files will be named according to the pattern: `phase_inhale.mp3`, `count_1.mp3`, etc.

## References

- [Google Cloud Text-to-Speech Documentation](https://cloud.google.com/text-to-speech/docs)
- [Python Client Library](https://cloud.google.com/python/docs/reference/texttospeech/latest)
- [Pricing Information](https://cloud.google.com/text-to-speech/pricing)
- [Authentication Guide](https://cloud.google.com/docs/authentication)

