# Business Requirements Document
## Quit Smoking Tracker (Breathe & Resist)

### 1. Project Goal and Scope

**Project Name:** Breathe & Resist (Дыши и Сопротивляйся)

**Purpose:** A private, single-user Django web application designed to help the user quit smoking through:
- Activity tracking (resisting cravings, acknowledging slip-ups, recording positive activities)
- Guided breathing exercises (18 techniques across 6 categories)
- Motivational reinforcement

**Target User:** Single Superuser (private application, no public registration)

**Platform:** Web application optimized for mobile devices (portrait mode)

---

### 2. Authentication and Access Control

- **Authentication System:** Django's standard authentication via Admin interface
- **Login Method:** Users authenticate by logging in at `/admin/`
- **Session Persistence:** Django's session middleware automatically maintains authentication across the entire site after login
- **User Registration:** Disabled - application is strictly for the pre-created Superuser
- **No Login Links:** Main screen has no login links - users access admin directly at `/admin/`
- **Access Levels:**
  - **Superuser (authenticated):** Full access to all features including Activity Tracker on home screen
  - **Guest/Unauthenticated:** Redirected to breathing menu only (`/breathe/`)

---

### 3. Feature A: The Activity Tracker (Superuser Only)

#### 3.1. Main Screen Layout
The main screen features clear visual separation:
- **Top:** Motivational Banner
- **Center:** Counter Badges (three distinct, tappable icons)
- **Bottom:** Breathing Menu access

#### 3.2. Motivational Banner
- **Location:** Top of main screen
- **Visibility:** Always visible, non-dismissible
- **Style:** Green, high-contrast banner
- **Content:** "Есть вещи, которые я не могу изменить. Но это - могу."
- **Purpose:** Constant motivation and brand reinforcement

#### 3.3. Counter System (Badges & Logging)

**Three Activity Types:**

| Activity Type (DB) | Russian UI Label | Color | Purpose |
|-------------------|------------------|-------|---------|
| `RESIST` | Бросил (Brosil - Quit) | Green (#3ABF83) | Track successful resistance to cravings |
| `SMOKED` | Сорвался (Sorvalsya - Slipped Up) | Red-Orange (#DC3545) | Honest tracking of slip-ups |
| `SPORT` | Активность (Aktivnost - Activity) | Blue (#007BFF) | Track positive physical activities |

**Functionality:**
- Each badge displays the individual running total count for that activity (not a net total)
- Each tap is logged with a timestamp in the database
- Badges are tappable icons with bold, clean fonts
- **Rate Limiting:** Server-side rate limit of 3 seconds between logging similar `activity_type` entries (prevents accidental rapid logging)

**Visual Feedback:**
- **Confetti Burst:** Triggered on successful RESIST tap
- **Dull Grey-Out:** Triggered on SMOKED tap
- **Success Glow:** Triggered on SPORT tap

---

### 4. Feature B: The Breathing Guide

#### 4.1. Technique Categories

**Six Categories (18 Total Techniques):**

| Category (Russian) | Category (English) | Techniques |
|-------------------|-------------------|------------|
| Пробуждение | Wakeup | 1. Bellows Breath (1-0-1-0)<br>2. Three-Part Breath (4-0-4-0)<br>3. 4-0-4-0 (Standard Energizing) |
| Фокус | Focus | 1. Box Breathing (4-4-4-4)<br>2. 5-1-5-1 (Focused Flow)<br>3. Bilateral Nostril (5-0-5-0) |
| Перезагрузка | Reset Mind | 1. Physiological Sigh (2-0-6-0)<br>2. Soft Sigh (3-0-6-0)<br>3. 5-0-5-0 (Baseline Breath) |
| Вместо сигареты | Craving Control | 1. 4-7-8 Breath (4-7-8-0)<br>2. Quick Box Breath (3-3-3-3)<br>3. Deep Diaphragmatic (5-0-5-0) |
| Спокойствие | Calm | 1. Brahma Mudra Breath (4-0-6-0)<br>2. Counting Exhales (3-0-5-0)<br>3. Simple Relaxation (6-0-8-0) |
| Снятие стресса | Stress Relief | 1. Box Breathing (4-4-4-4)<br>2. Extended Exhale (4-0-8-0)<br>3. Five Finger Breathing (4-0-4-0) |

#### 4.2. User Flow

1. **Category Selection:** User selects a category from the breathing menu
2. **Technique Selection:** User chooses a specific technique
3. **Preparation Screen:**
   - Displays technique name (Russian)
   - Shows full `instructions_ru` text from database
   - Displays `posture_ru` (e.g., "Сидя")
   - **Summary Confirmation Section:** Shows timing and duration in format:
     - Название: [technique name_ru]
     - Общая длительность: [recommended_time_min] минуты
     - Цикл: Вдох [inhale] с / Задержка [hold_start] с / Выдох [exhale] с
     - Положение: [posture_ru]
     - Фокус: [breath_origin description in Russian]
   - **Toggle Controls:**
     - Toggle 1: Sound Cues (on/off)
     - Toggle 2: Vibration Cues (on/off)
   - Preferences stored in Local Storage (persists across sessions, default: `true`)
   - "Start" button (Начать)
4. **Guide Screen:** Active breathing exercise with visual and audio guidance
5. **Completion:** Success message in Russian, automatic return to Category Menu

#### 4.3. Guide Screen Features

**Layout (Mobile Portrait):**
- **Top:** Progress Bar (shows total session time remaining)
- **Upper Center:** Dynamic Text Cue (e.g., "🧘 Брюшное дыхание")
- **Center:** Large Breathing Balloon and Torso Graphic
- **Bottom:** Sound/Vibration Status Icons
- **Controls:** Pause (⏸️) and Cancel (X) buttons

**Visual Elements:**
- **Balloon:**
  - Size Range: 30% to 80% of viewport width
  - Color: Deep Teal/Cyan (#00A38D)
  - Animation: Smooth growth/shrink cycle synchronized with breathing phases
- **Torso Graphic:**
  - Simple, stylized line drawing
  - Pulse effect during Inhale: 0% to 50% opacity fill, color brightens (light gold/yellow)
  - Dimming effect during Exhale
  - Pulse location based on `breath_origin` field (ABDOMEN, CHEST, NOSTRILS)
- **Progress Bar:**
  - Style: Simple, horizontal linear fill
  - Color: Contrasting gray/blue or matching teal
  - Shows: Total session time remaining (X minutes to 0)

**Audio Cues (Russian TTS):**
- Phase cues: "Вдох" (Inhale), "Задержка" (Hold), "Выдох" (Exhale)
- Number counts: "Один" through "Десять" (1-10)
- Format: MP3, 96 kbps
- Storage: `/static/audio/ru/`
- File naming:
  - Phase cues: `audio/ru/phase_inhale.mp3`, `audio/ru/phase_exhale.mp3`, `audio/ru/phase_hold.mp3`
  - Number counts: `audio/ru/count_1.mp3`, `audio/ru/count_2.mp3`, etc.

**Haptic Feedback:**
- Vibration cues synchronized with breathing phases
- Controlled by user toggle preference

**Session Control:**
- **Pause:** Stops timer and animation, allows resume
- **Cancel:** Returns to Category Menu
- **Background Handling:** JavaScript pauses animation/timer when tab loses focus (Page Visibility API). Audio continues if possible.

#### 4.4. Completion Flow

- **Success Message:** "Сессия завершена! Вы молодец." (Session completed! You're great.)
- **Action:** Automatic return to Category Menu
- **Purpose:** Encourages user to select another technique immediately

---

### 5. Localization Requirements

**Language:** All user-facing content in Russian

**Localized Elements:**
- Category names (from database `name_ru` fields)
- Technique names (from database `name_ru` fields)
- Instructions (from database `instructions_ru` fields)
- Guide screen cues ("Вдох," "Один," "Два," etc.)
- Button labels:
  - Начать (Start)
  - Пауза / Продолжить (Pause / Resume)
  - Отмена (Cancel)
- Error messages:
  - "Ошибка сети. Проверьте подключение." (Network error. Check connection.)
- Success messages:
  - "Сессия завершена! Вы молодец." (Session completed! You're great.)

**Motivational Banner:** Hardcoded Russian phrase in base template

---

### 6. Data Requirements

#### 6.1. Initial Data
- **6 Categories:** Loaded via JSON fixture (`docs/breathing_techniques.json`)
  - Category 1: Пробуждение (Wakeup)
  - Category 2: Фокус (Focus)
  - Category 3: Перезагрузка (Reset Mind)
  - Category 4: Вместо сигареты (Craving Control)
  - Category 5: Спокойствие (Calm)
  - Category 6: Снятие стресса (Stress Relief)
- **18 Techniques:** Complete data with all Russian fields populated (3 techniques per category)
- **Data Source:** Fixture file contains all required data. Superuser can edit via Admin interface.

#### 6.2. Data Persistence
- **Activity Logs:** Timestamped entries for each counter tap
- **Breathing Session History:** Complete records of all breathing sessions for analysis
  - Technique used
  - Start and completion times
  - Duration and cycles completed
  - Completion status (completed vs cancelled)
  - Preferences used (sound/vibration)
- **User Preferences:** Sound/Vibration toggles stored in Local Storage (browser)
- **Session Data:** Technique selection and preferences during active session

---

### 7. Error Handling

- **Missing Audio Files:** Fail silently (no sound, visual guide continues)
- **Network Logging Failures:** Display discreet "Network Error" toast message (Russian) with manual retry option
- **Core Function Priority:** Visual breathing guide never interrupted by non-critical errors

---

### 8. Mobile Optimization

- **Target Screen Sizes:** 375px to 420px width (portrait mode)
- **Orientation:** Portrait-only design
- **Landscape Handling:** Display message asking user to rotate back to portrait
- **Responsive Design:** Vertical stacking critical for UI functionality

---

### 9. Admin Interface Requirements

**Superuser Access:**
- Full CRUD access to `ActivityLog` (manual counter adjustments)
- Full CRUD access to `BreathingSession` (view and analyze session history)
- Full CRUD access to `BreathingTechnique` model
- Full CRUD access to `BreathingCategory` model
- All via Django Admin interface

**Analytics Capabilities:**
- View complete breathing session history
- Analyze technique usage patterns
- Track session completion rates
- Correlate breathing sessions with activity logs
- Export data for external analysis

---

### 10. Deployment Requirements

- **Platform:** DigitalOcean
- **Droplet:** Basic Droplet ($6/mo or equivalent) in nearest regional datacenter
- **Static Files:** Served via Cloudflare
- **Database:** PostgreSQL for production (SQLite for development)
- **Environment:** API keys stored as environment variables (not in codebase)

