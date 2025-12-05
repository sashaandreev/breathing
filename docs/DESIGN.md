# Technical Design Document
## Quit Smoking Tracker (Breathe & Resist)

### 1. High-Level Architecture

**Architecture Pattern:** Django MVT (Model-View-Template)

**Technology Stack:**
- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (development), PostgreSQL (production)
- **Static Files:** Django static files served via Cloudflare
- **TTS:** Google Cloud Text-to-Speech (one-time generation)
- **Deployment:** DigitalOcean + Cloudflare

**Application Structure:**
```
breathing/
├── breathing/          # Django project settings
├── tracker/            # Main app (Activity Tracker)
├── breathe/            # Breathing Guide app
├── templates/          # HTML templates
├── static/             # Static files
│   ├── css/
│   ├── js/
│   └── audio/
│       └── ru/         # Russian TTS audio files
└── fixtures/           # Initial data (JSON/YAML)
```

---

### 2. Database Model Design

#### 2.1. ActivityLog Model

**Purpose:** Stores every interaction with the three counter buttons.

**Fields:**

| Field Name | Type | Constraints | Notes |
|------------|------|-------------|-------|
| `user` | ForeignKey(User) | Required | Links to User model for permissions |
| `activity_type` | CharField | max_length=20, choices | Choices: 'RESIST', 'SMOKED', 'SPORT' |
| `timestamp` | DateTimeField | auto_now_add=True | Automatic timestamp on creation |

**Admin Access:** Full CRUD for Superuser

**Rate Limiting:** Server-side validation - 3 seconds minimum between similar `activity_type` entries

---

#### 2.2. BreathingSession Model

**Purpose:** Tracks completed breathing sessions for later analysis.

**Fields:**

| Field Name | Type | Constraints | Notes |
|------------|------|-------------|-------|
| `user` | ForeignKey(User) | Required | Links to User model |
| `technique` | ForeignKey(BreathingTechnique) | Required | Which technique was used |
| `started_at` | DateTimeField | auto_now_add=False | Session start timestamp (set manually) |
| `completed_at` | DateTimeField | Nullable | Session completion timestamp |
| `duration_seconds` | IntegerField | Nullable | Actual session duration in seconds |
| `completed` | BooleanField | default=False | Whether session was completed (vs cancelled) |
| `cycles_completed` | IntegerField | Nullable | Number of breathing cycles completed |
| `sound_enabled` | BooleanField | default=True | Whether sound cues were enabled |
| `vibration_enabled` | BooleanField | default=True | Whether vibration cues were enabled |

**Admin Access:** Full CRUD for Superuser

**Analytics Use Cases:**
- Track which techniques are used most frequently
- Analyze session completion rates
- Track average session duration
- Identify patterns in technique usage over time
- Correlate with ActivityLog data (RESIST, SMOKED, SPORT)

---

#### 2.3. BreathingCategory Model

**Purpose:** Organizes breathing techniques into 6 categories.

**Fields:**

| Field Name | Type | Constraints | Notes |
|------------|------|-------------|-------|
| `name_ru` | CharField | max_length=100 | Russian display name (Required) |
| `name` | CharField | max_length=100 | English name (internal, Optional) |
| `description_ru` | TextField | Optional | Category description in Russian |
| `order` | IntegerField | Optional | Display order (not used, categories ordered by PK) |

**Note:** Only `name_ru` is required. All other fields are optional. Categories are ordered by primary key (PK) in the fixture file.

**Categories (from fixture):**
1. PK 1: Пробуждение (Wakeup)
2. PK 2: Фокус (Focus)
3. PK 3: Перезагрузка (Reset Mind)
4. PK 4: Вместо сигареты (Craving Control)
5. PK 5: Спокойствие (Calm)
6. PK 6: Снятие стресса (Stress Relief)

---

#### 2.4. BreathingTechnique Model

**Purpose:** Stores all parameters for breathing exercises. All user-facing content in Russian.

**Fields:**

| Field Name | Type | Constraints | Notes |
|------------|------|-------------|-------|
| `category` | ForeignKey(BreathingCategory) | Required | Links to category |
| `name_ru` | CharField | max_length=200 | Display name in Russian |
| `inhale` | IntegerField | Required | Inhale duration (seconds) |
| `hold_start` | IntegerField | Required | Hold after inhale (seconds) |
| `exhale` | IntegerField | Required | Exhale duration (seconds) |
| `hold_end` | IntegerField | Required | Hold after exhale (seconds) |
| `recommended_time_min` | IntegerField | Required | Total session duration (minutes) |
| `posture_ru` | CharField | max_length=100 | Quick preparation cue (e.g., "Сидя") |
| `breath_origin` | CharField | max_length=20, choices | Focus area: 'ABDOMEN', 'CHEST', 'NOSTRILS', 'MOUTH', 'ALL' |
| `instructions_ru` | TextField | Required | Detailed step-by-step instructions in Russian |
| `use_sound_cue` | BooleanField | default=True | Default sound toggle state |
| `use_haptic_cue` | BooleanField | default=True | Default vibration toggle state |

**Example Data (Craving Control: 4-7-8):**
- `name_ru`: "Дыхание 4-7-8"
- `category`: "Craving Control" (FK)
- `inhale`: 4
- `hold_start`: 7
- `exhale`: 8
- `hold_end`: 0
- `recommended_time_min`: 3
- `posture_ru`: "Сидя"
- `breath_origin`: "NOSTRILS"
- `instructions_ru`: [Detailed Russian instructions]

---

### 3. URL Routing

**URL Structure:**

```
/                          # Home (redirects based on auth)
/login/                    # Django login
/logout/                   # Django logout
/breathe/                  # Breathing menu (categories)
/breathe/<category_id>/    # Techniques in category
/breathe/technique/<id>/   # Technique detail/preparation
/breathe/guide/<id>/       # Active guide screen
/api/activity/tap/         # AJAX endpoint for counter taps
/admin/                    # Django admin
```

**View Logic:**
- `home_view`: Checks authentication
  - Superuser → Full template with Activity Tracker
  - Guest → Redirect to `/breathe/`
- `activity_tap`: Handles AJAX POST, validates rate limit, saves ActivityLog

---

### 4. Localization and Audio Design

#### 4.1. Localization Strategy

**UI Language:**
- All user-visible elements rendered in Russian
- Superuser inputs Russian text directly into Admin fields
- Template variables use `name_ru`, `instructions_ru`, etc.

**Motivational Banner:**
- Hardcoded in base template: "Есть вещи, которые я не могу изменить. Но это - могу."

**Template Structure:**
```django
{% load i18n %}
{% load static %}
<!-- All text in Russian -->
```

#### 4.2. Text-to-Speech (TTS) Generation

**Service:** Google Cloud Text-to-Speech

**Voice Selection:**
- High-quality Wavenet voice (e.g., `ru-RU-Wavenet-D` or `ru-RU-Wavenet-E`)
- Single, consistent, neutral-calm Russian voice for all audio assets
- Female or male voice known for calmness

**Audio Files to Generate:**

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

**Audio Specifications:**
- Format: MP3
- Quality: 96 kbps (moderate quality for clarity and fast mobile loading)
- Storage: `/static/audio/ru/`

**Generation Process:**
- One-time generation using TTS API
- Store API key as environment variable
- Generate all files during development/setup phase
- Cost incurred only once (not during runtime)

---

### 5. Frontend UI/UX Logic

#### 5.1. Mobile Screen Layout

**Guide Screen (Portrait Mode):**

```
┌─────────────────────────────┐
│  [Progress Bar]             │ ← Top: Time countdown
│                             │
│  🧘 Брюшное дыхание         │ ← Upper Center: Dynamic text cue
│                             │
│      ⭕                      │
│     ⭕⭕⭕                    │ ← Center: Breathing Balloon
│    ⭕⭕⭕⭕⭕                  │    (30% to 80% Vw)
│                             │
│    [Torso Graphic]          │ ← Center: Torso with pulse
│                             │
│  🔊 [Sound]  📳 [Vibration] │ ← Bottom: Status icons
│                             │
│  [⏸️ Pause]  [X Cancel]     │ ← Controls
└─────────────────────────────┘
```

**Responsive Breakpoints:**
- Target: 375px to 420px width (portrait)
- Orientation: Portrait-only
- Landscape: Display rotation message
  - Text: "Пожалуйста, поверните устройство вертикально для продолжения."
  - Main UI disabled/grayed out until corrected

#### 5.2. Visual Synchronization Logic

**Balloon Animation:**
- **Inhale Phase:**
  - Balloon grows from 30% to 80% Vw
  - Smooth animation using `requestAnimationFrame`
  - Duration: `inhale` seconds
- **Hold Phase:**
  - Balloon maintains 80% Vw
  - Duration: `hold_start` seconds
- **Exhale Phase:**
  - Balloon shrinks from 80% to 30% Vw
  - Duration: `exhale` seconds
- **Hold End Phase:**
  - Balloon maintains 30% Vw
  - Duration: `hold_end` seconds

**Torso Graphic Pulse:**
- **Base Design:**
  - Minimal line drawing on background (SVG or CSS-based)
  - Faint, light gray line color: #E0E0E0
  - Distinct horizontal line/gradient separating Chest from Abdomen
  - Exact SVG structure/implementation to be determined during Phase 4 development
- **Breath Origin Mapping:**
  - `ABDOMEN`: Lower torso (abdomen area) pulses
  - `CHEST`: Upper torso (chest area) pulses
  - `NOSTRILS`: Entire torso outline minimal pulse/glow (faintly brightens)
  - `MOUTH`: Entire torso outline minimal pulse/glow (faintly brightens)
  - `ALL`: Entire torso outline minimal pulse/glow (faintly brightens) - Text: "🌬️ Естественное дыхание"
- **Inhale Effect:**
  - Target area: 0% opacity → 50% opacity fill
  - Color brightens to light gold/yellow (#FFD700)
  - Synchronized with balloon growth
- **Exhale Effect:**
  - Target area: 50% opacity → 0% opacity
  - Color dims
  - Synchronized with balloon shrink

**Progress Bar:**
- Shows total session time remaining
- **Format:** Minutes:seconds (MM:SS), e.g., "3:00", "2:45", "0:30"
- Calculation: `recommended_time_min` - elapsed time
- Updates every second
- Visual: Horizontal linear fill

#### 5.3. JavaScript Engine (Core Logic)

**Primary Function:**
```javascript
function startBreathingTechnique(technique) {
    // Read timing parameters
    const { inhale, hold_start, exhale, hold_end, recommended_time_min } = technique;
    
    // Initialize animation loop
    // Coordinate balloon animation
    // Coordinate torso pulse
    // Play audio cues (if enabled)
    // Trigger haptic feedback (if enabled)
    // Update progress bar
    // Handle pause/resume
    // Handle cancel
    // Handle completion
}
```

**Animation Loop:**
- Uses `requestAnimationFrame` for smooth 60fps animation
- Calculates current phase based on elapsed time
- Updates balloon size proportionally
- Updates torso opacity/color
- Triggers audio at phase transitions
- Triggers haptic feedback at phase transitions

**Audio Integration:**
- Check Local Storage for sound preference (`soundCueEnabled`, default: `true` if not set)
- **Loading:** Use Django static tags in templates: `{% static 'audio/ru/phase_inhale.mp3' %}`
- **JavaScript:** Use Audio API: `new Audio('/static/audio/ru/phase_inhale.mp3')` or relative paths from static root
- **Preloading:** Load audio files on-demand when technique starts (not all at page load)
- **Phase Cues:** Play exactly at phase start (0s), must finish before number counts begin
- **Number Counts:** Play every second during all phases (inhale, hold_start, exhale, hold_end)
- **Timing:** Measure phase cue duration at runtime to prevent overlap with number counts
- **Volume:** Medium level, clear but not startling
- Handle missing files gracefully (fail silently)

**Haptic Integration:**
- Check Local Storage for vibration preference
- Use Web Vibration API: `navigator.vibrate(100)`
- **Pattern:** Single, sharp, medium-intensity pulse (100ms duration)
- **Trigger:** Only at exact start of new phase (Inhale, Hold, Exhale, End Hold)
- Handle unsupported devices gracefully

**Page Visibility API:**
- Pause animation/timer when tab loses focus
- Continue audio if possible
- Resume on tab focus

**Session Completion:**
- Session is strictly time-based (`recommended_time_min`)
- If time expires mid-cycle, allow current cycle to finish
- Session only stops after complete `hold_end` phase after time elapsed
- Success message: "Сессия завершена! Вы молодец."
- Auto-redirect to category menu after 2-3 seconds

#### 5.4. Activity Tracker Frontend

**Counter Badges:**
- Three distinct Unicode icons with color coding:
  - RESIST: ✅ (Check Mark) - Green (#3ABF83)
  - SMOKED: 🚫 (No Symbol) - Red-Orange (#DC3545)
  - SPORT: 🏃‍♂️ (Running Person) - Blue (#007BFF)
- Display individual running totals
- AJAX POST to `/api/activity/tap/` on tap
- Visual feedback on successful response:
  - RESIST: Confetti burst (canvas-confetti library, green/blue, 2 seconds)
  - SMOKED: Dull grey-out
  - SPORT: Success glow

**Badge Design:**
- Clear, large font size: 24px
- Bold, clean fonts
- Large tap targets (mobile-friendly)
- Color-coded backgrounds
- Count displayed prominently

---

### 6. Static File Structure

```
static/
├── css/
│   ├── base.css
│   ├── home.css
│   └── guide.css
├── js/
│   ├── activity-tracker.js
│   ├── breathing-guide.js
│   └── utils.js
└── audio/
    └── ru/
        ├── phase_inhale.mp3
        ├── phase_exhale.mp3
        ├── phase_hold.mp3
        ├── count_1.mp3
        ├── count_2.mp3
        ├── ...
        └── count_10.mp3
```

---

### 7. Session and Storage

**Local Storage Keys:**
- `soundCueEnabled`: Boolean (default: `true` if key doesn't exist)
- `vibrationCueEnabled`: Boolean (default: `true` if key doesn't exist)
- **Implementation:** Check if key exists, if not, default to `true`

**Session Storage:**
- Current technique ID
- Session start time
- Pause state

**Database:**
- ActivityLog entries (persistent)
- BreathingSession entries (persistent - session history for analysis)
- User preferences (if needed for future features)

---

### 8. Error Handling

**Missing Audio Files:**
- JavaScript checks file existence before playing
- Fails silently if file not found
- Visual guide continues uninterrupted

**Network Errors:**
- Activity tap failures: Display toast message (Russian)
- Retry mechanism: Manual retry button
- Offline detection: Graceful degradation

**Validation Errors:**
- Rate limiting: Server returns 429 Too Many Requests
- Error message (Russian): "Слишком часто. Попробуйте через 3 секунды."
- Frontend displays brief, non-intrusive toast message
- Badge count does not update (fail silently)
- Prevents duplicate submissions

---

### 9. Security Considerations

**Authentication:**
- Django's built-in authentication
- CSRF protection on all POST requests
- Session security

**API Endpoints:**
- Rate limiting on activity taps
- User validation (only logged-in users)
- Activity type validation

**Environment Variables:**
- TTS API key stored as environment variable
- Database credentials in environment
- Secret key in environment
- Never committed to repository

---

### 10. Performance Optimization

**Static Files:**
- Served via Cloudflare CDN
- Compression enabled
- Cache headers set appropriately

**Database:**
- Indexes on frequently queried fields:
  - `ActivityLog.user` (essential for counter calculations)
  - `ActivityLog.activity_type` (essential for filtering)
  - `ActivityLog.timestamp` (for time-based queries)
  - `BreathingTechnique.category` (for category filtering)
  - `BreathingSession.user` (for user session history)
  - `BreathingSession.technique` (for technique usage analysis)
  - `BreathingSession.started_at` (for time-based queries)
- Add indexes in model Meta class or migrations

**Frontend:**
- Minified JavaScript in production
- Optimized images
- Lazy loading for non-critical assets

**Mobile:**
- Optimized for 3G/4G connections
- Audio files compressed (96 kbps)
- Minimal JavaScript bundle size

