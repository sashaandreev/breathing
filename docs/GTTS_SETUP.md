# gTTS (Google Text-to-Speech) Setup Guide

This guide explains how to use gTTS (Google Text-to-Speech) for generating audio files. **gTTS is the recommended option** as it's simpler, free, and doesn't require API keys.

## Overview

**gTTS** (Google Text-to-Speech) is a Python library that provides a simple interface to Google's TTS service. Unlike Google Cloud Text-to-Speech API, it:
- ✅ **No API key required** - completely free
- ✅ **No authentication needed** - works out of the box
- ✅ **Simple setup** - just install the package
- ✅ **Good quality** - uses Google's TTS engine
- ⚠️ **Rate limiting** - may be blocked if overused (unlikely for this project)
- ⚠️ **Less control** - fewer voice options compared to Cloud API

## Installation

Add to `requirements.txt`:
```
gTTS>=2.5.0
```

Install:
```bash
pip install gTTS
```

## Usage

### Basic Example

```python
from gtts import gTTS
import os

# Create audio file
tts = gTTS(text='Вдох', lang='ru', slow=False)
tts.save('static/audio/ru/phase_inhale.mp3')
```

### For This Project

The audio generation script will use gTTS to create all Russian audio files:

**Phase Cues:**
- `phase_inhale.mp3` - "Вдох"
- `phase_exhale.mp3` - "Выдох"
- `phase_hold.mp3` - "Задержка"

**Number Counts (1-10):**
- `count_1.mp3` - "Один"
- `count_2.mp3` - "Два"
- `count_3.mp3` - "Три"
- `count_4.mp3` - "Четыре"
- `count_5.mp3` - "Пять"
- `count_6.mp3` - "Шесть"
- `count_7.mp3` - "Семь"
- `count_8.mp3` - "Восемь"
- `count_9.mp3` - "Девять"
- `count_10.mp3` - "Десять"

## Configuration

No configuration needed! Just install gTTS and it works.

The project is configured to use gTTS by default (see `settings.py`):
```python
TTS_PROVIDER = 'gtts'  # Default
```

## Language and Voice

gTTS supports Russian (`lang='ru'`):
- Uses Google's standard Russian voice
- Good quality for our use case
- Natural pronunciation

## Audio Quality

gTTS generates MP3 files:
- **Format**: MP3
- **Quality**: Good (suitable for mobile)
- **File size**: Reasonable (smaller than Cloud API)

## Rate Limiting

gTTS may have rate limiting if you make too many requests:
- **For this project**: Not an issue (we generate files once, not during runtime)
- **If blocked**: Wait a few minutes and try again
- **Workaround**: Generate files in batches with small delays

## Comparison: gTTS vs Google Cloud TTS

| Feature | gTTS | Google Cloud TTS |
|---------|------|------------------|
| **Cost** | Free | Free tier, then paid |
| **Setup** | Install package | API key/service account |
| **Authentication** | None needed | Required |
| **Voice Quality** | Good | Excellent (WaveNet) |
| **Voice Options** | Limited | Many options |
| **Rate Limits** | Possible | Higher limits |
| **Reliability** | Good | Enterprise-grade |
| **Best For** | Small projects | Production apps |

**For this project**: gTTS is perfect! We only generate audio files once during setup, not during runtime.

## Troubleshooting

### Error: "Failed to connect"

- Check your internet connection
- gTTS requires internet to generate audio
- Try again after a few minutes

### Error: "Rate limit exceeded"

- You've made too many requests
- Wait 10-15 minutes and try again
- Generate files in smaller batches

### Audio quality issues

- gTTS quality is generally good for Russian
- If you need higher quality, consider Google Cloud TTS
- For mobile use, gTTS quality is sufficient

### File not saving

- Check directory permissions
- Ensure `static/audio/ru/` directory exists
- Verify write permissions

## Example Generation Script

```python
from gtts import gTTS
import os

# Create output directory
os.makedirs('static/audio/ru', exist_ok=True)

# Phase cues
phases = {
    'phase_inhale': 'Вдох',
    'phase_exhale': 'Выдох',
    'phase_hold': 'Задержка',
}

# Number counts
numbers = {
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

# Generate phase cues
for filename, text in phases.items():
    print(f"Generating {filename}...")
    tts = gTTS(text=text, lang='ru', slow=False)
    tts.save(f'static/audio/ru/{filename}.mp3')

# Generate number counts
for num, text in numbers.items():
    print(f"Generating count_{num}...")
    tts = gTTS(text=text, lang='ru', slow=False)
    tts.save(f'static/audio/ru/count_{num}.mp3')

print("All audio files generated!")
```

## Next Steps

1. Install gTTS: `pip install gTTS`
2. Run the audio generation script (when implemented)
3. Verify audio files are created in `static/audio/ru/`
4. Test playback in the breathing guide

## References

- [gTTS Documentation](https://gtts.readthedocs.io/)
- [gTTS GitHub](https://github.com/pndurette/gTTS)
- [PyPI Package](https://pypi.org/project/gTTS/)

