# Clarifications Summary
## Final Technical and UX Specifications

This document consolidates all clarifications from clarification_3.docx and breathing_techniques.json to resolve implementation ambiguities.

---

## I. Critical Missing Details - RESOLVED

### 1. Complete Technique Data ✅
**Status:** Complete data provided in `docs/breathing_techniques.json`

All 18 techniques with complete specifications:
- 6 categories (PK 1-6)
- 18 techniques (PK 1-18)
- All Russian fields populated
- All timing parameters specified
- All `breath_origin` values defined

**Note:** The JSON file includes additional `breath_origin` values:
- `MOUTH` (for Physiological Sigh techniques)
- `ALL` (for neutral breathing techniques)

These should be added to the model choices.

---

### 2. Breathing Cycle Logic ✅

**Session Type:** Strictly time-based (`recommended_time_min`)

**Mid-Cycle End Behavior:**
- If session time expires mid-cycle, the session **must allow the current cycle to finish**
- This prevents abrupt stops and maintains the calming effect
- Session only stops after a complete `hold_end` phase is reached after `recommended_time_min` has elapsed

**Pre-Time End Behavior:**
- If time ends exactly as a cycle completes, the session stops immediately

**Implementation:**
- Track elapsed time vs `recommended_time_min`
- Check at the start of each cycle if time has expired
- If expired, complete current cycle, then end session
- If not expired, continue to next cycle

---

### 3. Number Count Audio Timing ✅

**Timing Rules:**
- Number counts play **every second** during phases where countdown is active
- Applies to: `inhale`, `hold_start`, `exhale`, and `hold_end` phases
- Example for 4s Inhale:
  - 0s: Phase cue "Вдох" plays
  - 1s: Count "Один" plays
  - 2s: Count "Два" plays
  - 3s: Count "Три" plays
  - 4s: Count "Четыре" plays

**Overlap Prevention:**
- Number counts **must not overlap** with phase cues
- Phase cue plays once at phase start (0s)
- Number counts begin immediately after phase cue finishes
- Requires pre-calculating phase cue audio duration to ensure no overlap

**Implementation:**
- Load phase cue audio and measure duration
- Schedule number counts to start after phase cue completes
- Use precise timing to avoid audio overlap

---

### 4. Summary Confirmation Screen Details ✅

**Format (Russian):**
```
Название: [technique name_ru]
Общая длительность: [recommended_time_min] минуты
Цикл: Вдох [inhale] с / Задержка [hold_start] с / Выдох [exhale] с
Положение: [posture_ru]
Фокус: [breath_origin description in Russian]
```

**Example:**
```
Название: Дыхание 4-7-8
Общая длительность: 3 минуты
Цикл: Вдох 4 с / Задержка 7 с / Выдох 8 с
Положение: Сидя
Фокус: Дыхание носом
```

**Display Location:** On preparation screen, before "Start" button

---

## II. Ambiguities - RESOLVED

### 5. Torso Graphic Implementation ✅

**Base Color:**
- Minimal line drawing on background
- Faint, light gray line color: `#E0E0E0`

**NOSTRILS/MOUTH Logic:**
- For `NOSTRILS` and `MOUTH` techniques (where physical location isn't primary focus):
  - Entire torso outline performs a **minimal visual pulse/glow**
  - Faintly brightens in sync with `Inhale` phase
  - Ensures timing cues without emphasizing specific area

**Separation:**
- Use distinct horizontal line or color gradient
- Clearly separate Chest (lungs) area from Abdomen (diaphragm) area
- Visual distinction needed for `ABDOMEN` vs `CHEST` pulse effects

**Pulse Effects:**
- `ABDOMEN`: Lower torso pulses (0% → 50% opacity, light gold/yellow #FFD700)
- `CHEST`: Upper torso pulses (0% → 50% opacity, light gold/yellow #FFD700)
- `NOSTRILS`/`MOUTH`/`ALL`: Entire torso outline minimal pulse/glow

---

### 6. Dynamic Text Cue Content ✅

**Content:**
- Displays the `breath_origin` instruction
- **Does not change** during the session
- Static text based on technique's `breath_origin` field

**Examples:**
- `ABDOMEN`: "🧘 Брюшное дыхание" (Abdominal Breathing)
- `CHEST`: "🫁 Грудное дыхание" (Chest Breathing)
- `NOSTRILS`: "👃 Дыхание носом" (Nasal Breathing)
- `MOUTH`: "👄 Дыхание ртом" (Mouth Breathing)
- `ALL`: "🌬️ Естественное дыхание" (Natural Breathing)

**Location:** Upper center of guide screen

---

### 7. Rate Limiting Error Handling ✅

**HTTP Status Code:** `429 Too Many Requests`

**Server Response:**
- Russian error message: "Слишком часто. Попробуйте через 3 секунды."
- Returned in JSON response

**Frontend Action:**
- Display brief, non-intrusive toast message with Russian error
- Fail silently (badge count does not update)
- Toast disappears after 3-4 seconds

---

### 8. Activity Badge Icons ✅

**Icons (Unicode Symbols):**

| Activity Type | Icon | Color |
|--------------|------|-------|
| Бросил (RESIST) | ✅ (Check Mark) | Green (#3ABF83) |
| Сорвался (SMOKED) | 🚫 (No Symbol) | Red-Orange (#DC3545) |
| Активность (SPORT) | 🏃‍♂️ (Running Person) | Blue (#007BFF) |

**Styling:**
- Clear, large font size: 24px
- Bold, clean fonts
- Large tap targets (mobile-friendly)
- Color-coded backgrounds

---

### 9. Landscape Warning Message ✅

**Russian Text:**
"Пожалуйста, поверните устройство вертикально для продолжения."

(Please turn your device vertically to continue.)

**Visibility:**
- Always visible when aspect ratio is incorrect (landscape mode)
- Main UI should be disabled/grayed out until corrected
- Full-screen overlay or prominent banner

**Detection:**
- Use CSS media queries or JavaScript orientation detection
- Display immediately on rotation to landscape

---

### 10. Confetti Animation ✅

**Library:** `canvas-confetti` (JavaScript library)

**Style:**
- Short, high-density burst
- Green/blue confetti colors
- Duration: approximately 2 seconds

**Trigger:** On successful RESIST activity tap

**Implementation:**
- Install via npm or CDN
- Configure for green/blue color scheme
- Trigger on AJAX success response

---

### 11. Progress Bar Format ✅

**Format:** Minutes:seconds (MM:SS)

**Examples:**
- "3:00" (3 minutes remaining)
- "2:45" (2 minutes 45 seconds remaining)
- "0:30" (30 seconds remaining)
- "0:00" (session complete)

**Update Frequency:** Every second

**Display:** Clear, readable format with proper zero-padding

---

### 12. Audio Playback Details ✅

**Phase Cues:**
- Play exactly at the start of corresponding phase (0s)
- "Вдох" at inhale start
- "Выдох" at exhale start
- "Задержка" at hold start (if applicable)

**Overlap Prevention:**
- Phase cue must finish before number counts begin
- Requires pre-calculating phase cue audio duration
- No overlap between phase cues and number counts

**Volume:**
- Medium volume level
- Clear but not startling
- Consistent across all audio files

**Implementation:**
- Load and measure phase cue audio duration
- Schedule number counts after phase cue completes
- Use precise timing to prevent overlap

---

### 13. Haptic Feedback Details ✅

**Pattern:**
- Single, sharp, medium-intensity pulse
- Duration: 100ms

**Trigger:**
- Only at exact start of new phase
- Phases: `Inhale`, `Hold`, `Exhale`, `End Hold`
- One pulse per phase transition

**Implementation:**
- Use Web Vibration API: `navigator.vibrate(100)`
- Check Local Storage for vibration preference
- Handle unsupported devices gracefully (no error)

---

### 14. Breathing Menu Access ✅

**From Home Screen:**
- Large, prominent button below counter badges
- Only visible to Superuser

**Button Text (Russian):**
"Начать Дыхание" (Nachat Dykhaniye - Start Breathing)

**Navigation:**
- Button leads to category list: `/breathe/`
- Styled to match mobile-friendly design
- Clear, visible call-to-action

---

### 15. Session Completion Logic ✅

**Behavior:**
- Session must allow current cycle to finish if time expires mid-cycle
- Session only stops after complete `hold_end` phase is reached
- This occurs after `recommended_time_min` has elapsed

**Implementation:**
- Check time expiration at cycle start
- If expired, complete current cycle, then end
- If not expired, continue to next cycle
- Display success message after final cycle completes

**Success Message:**
"Сессия завершена! Вы молодец." (Session completed! You're great.)

**Action:** Auto-redirect to category menu after 2-3 seconds

---

## III. Minor Clarifications

### Model Field Defaults

**BreathingCategory.order:**
- Default value: 0
- Or auto-incrementing to manage list order
- Used for display ordering

**BreathingCategory.description_ru:**
- Optional field
- Not required for every category

---

### Admin Interface Details

**Inline Editing:**
- No inline editing of techniques within category list
- Use standard foreign key linking
- Standard Django admin interface

**Custom Actions:**
- No custom admin actions needed at this time
- Rely on standard Django features

---

### Error Message Localization

**Requirement:**
- All error messages must be fully localized in Russian on frontend
- Includes: network errors, rate limiting, validation errors
- Consistent Russian user experience

**Examples:**
- Network error: "Ошибка сети. Проверьте подключение."
- Rate limiting: "Слишком часто. Попробуйте через 3 секунды."
- Validation errors: Appropriate Russian messages

---

### Static File Organization

**Audio Files:**
- Should not be versioned (simplifies JS path)
- Use Cloudflare to handle cache-busting
- Efficient serving via CDN

**Structure:**
```
static/
└── audio/
    └── ru/
        ├── phase_inhale.mp3
        ├── phase_exhale.mp3
        ├── phase_hold.mp3
        ├── count_1.mp3
        ├── count_2.mp3
        └── ... (count_10.mp3)
```

---

### Database Indexes

**Required Indexes:**
- `ActivityLog.user` - Optimize counter calculation queries
- `ActivityLog.activity_type` - Optimize filtering by type
- `ActivityLog.timestamp` - Optimize time-based queries
- `BreathingTechnique.category` - Optimize category filtering

**Implementation:**
- Add indexes in model Meta class or migrations
- Essential for query performance in Phase 3

---

### Breath Origin Choices Update

**Original Choices:**
- `ABDOMEN`
- `CHEST`
- `NOSTRILS`

**Additional Choices (from JSON):**
- `MOUTH` - For mouth breathing techniques
- `ALL` - For neutral/natural breathing techniques

**Update Required:**
- Model choices should include all five options
- Dynamic text cue mapping should handle all five:
  - `ABDOMEN`: "🧘 Брюшное дыхание"
  - `CHEST`: "🫁 Грудное дыхание"
  - `NOSTRILS`: "👃 Дыхание носом"
  - `MOUTH`: "👄 Дыхание ртом"
  - `ALL`: "🌬️ Естественное дыхание"

---

## Implementation Notes

1. **Breathing Cycle Logic:** Most critical - ensure time-based completion with cycle finish
2. **Audio Timing:** Requires precise scheduling to prevent overlap
3. **Torso Graphic:** Need to handle 5 different `breath_origin` types
4. **Complete Data:** All 18 techniques fully specified in JSON file
5. **Error Handling:** All errors must be in Russian

---

## Files Referenced

- `docs/breathing_techniques.json` - Complete technique data (valid JSON, no comments)
- `docs/clarification_3.docx` - Source of these clarifications

---

## Final Clarifications (Post-Review)

### Category Model Fields
- **Required:** Only `name_ru`
- **Optional:** `name`, `description_ru`, `order`
- Categories ordered by PK (1-6) in fixture file

### Audio File Loading
- **Django Templates:** Use `{% static 'audio/ru/phase_inhale.mp3' %}`
- **JavaScript:** Use `new Audio('/static/audio/ru/phase_inhale.mp3')`
- **Preloading:** On-demand when technique starts (not all at page load)
- **Duration Measurement:** At runtime to prevent overlap

### Local Storage Defaults
- `soundCueEnabled`: Default `true` if key doesn't exist
- `vibrationCueEnabled`: Default `true` if key doesn't exist

### Summary Confirmation
- Part of preparation screen (not separate)
- Displayed before "Start" button
- Format specified in clarifications

### Torso Graphic
- Exact SVG structure to be determined during Phase 4 implementation
- Base color: #E0E0E0
- Clear separation between chest and abdomen areas

### Breathing Menu Button
- Only visible to Superuser (below counter badges)
- Guest users access `/breathe/` directly (no button needed)

---

## Status

✅ All critical ambiguities resolved
✅ All missing details provided
✅ JSON file validated and category numbers confirmed
✅ Ready for implementation

