# Implementation Plan
## Quit Smoking Tracker (Breathe & Resist)

### Overview

The implementation is broken down into **5 sequential phases**. Each phase builds upon the previous one, ensuring a solid foundation before adding complexity.

---

## Phase 1: Foundation and Data Setup (Backend Core)

### 1.1. Project Initialization

**Tasks:**
- [ ] Verify Django project structure exists
- [ ] Create Django apps: `tracker` and `breathe`
- [ ] Install dependencies:
  - Django
  - psycopg2-binary (for PostgreSQL)
  - python-docx (for documentation, if needed)
- [ ] Set up virtual environment (`.venv`)
- [ ] Create `requirements.txt`
- [ ] Configure `settings.py`:
  - Add apps to `INSTALLED_APPS`
  - Configure database (SQLite for dev)
  - Set up static files configuration
  - Configure media files (if needed)

**Deliverables:**
- Working Django project structure
- Two apps created and registered
- Development database configured

---

### 1.2. Data Models

**Tasks:**
- [ ] Create `ActivityLog` model in `tracker/models.py`:
  - `user` (ForeignKey to User)
  - `activity_type` (CharField with choices: RESIST, SMOKED, SPORT)
  - `timestamp` (DateTimeField, auto_now_add)
- [ ] Create `BreathingCategory` model in `breathe/models.py`:
  - `name` (CharField, English)
  - `name_ru` (CharField, Russian)
  - `description_ru` (TextField, optional)
  - `order` (IntegerField, optional)
- [ ] Create `BreathingTechnique` model in `breathe/models.py`:
  - All fields as specified in Design Document
  - Proper ForeignKey relationships
  - Field validations
- [ ] Create `BreathingSession` model in `breathe/models.py`:
  - `user` (ForeignKey to User)
  - `technique` (ForeignKey to BreathingTechnique)
  - `started_at` (DateTimeField)
  - `completed_at` (DateTimeField, nullable)
  - `duration_seconds` (IntegerField, nullable)
  - `completed` (BooleanField, default=False)
  - `cycles_completed` (IntegerField, nullable)
  - `sound_enabled` (BooleanField)
  - `vibration_enabled` (BooleanField)
- [ ] Create and run migrations:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

**Deliverables:**
- Four models defined and migrated (ActivityLog, BreathingSession, BreathingCategory, BreathingTechnique)
- Database schema created

---

### 1.3. Admin Interface

**Tasks:**
- [ ] Register `ActivityLog` in `tracker/admin.py`
- [ ] Register `BreathingSession` in `breathe/admin.py`
- [ ] Register `BreathingCategory` in `breathe/admin.py`
- [ ] Register `BreathingTechnique` in `breathe/admin.py`
- [ ] Configure admin display:
  - List displays
  - Search fields
  - Filters
  - Inline editing (if applicable)
- [ ] Create Superuser:
  ```bash
  python manage.py createsuperuser
  ```

**Deliverables:**
- All models accessible in Django Admin
- Superuser account created
- Session history tracking ready

---

### 1.4. Localization Data (Fixtures)

**Tasks:**
- [ ] Copy fixture file:
  - Source: `docs/breathing_techniques.json`
  - Destination: `breathe/fixtures/breathing_techniques.json`
  - Update model names: Replace `app_name` with `breathe`
- [ ] Verify JSON validity:
  - JSON is valid (no comments)
  - Contains 6 categories (PK 1-6)
  - Contains 18 techniques (PK 1-18)
  - Category mapping:
    - PK 1: Пробуждение (Wakeup)
    - PK 2: Фокус (Focus)
    - PK 3: Перезагрузка (Reset Mind)
    - PK 4: Вместо сигареты (Craving Control)
    - PK 5: Спокойствие (Calm)
    - PK 6: Снятие стресса (Stress Relief)
- [ ] Load fixtures:
  ```bash
  python manage.py loaddata breathing_techniques.json
  ```

**Deliverables:**
- Complete fixture files with all 6 categories and 18 techniques
- Data loaded into database
- Verified via Django Admin

---

### 1.5. Testing

**Tasks:**
- [ ] Verify all models in Admin:
  - Create, read, update, delete operations
  - Foreign key relationships work
- [ ] Verify fixture data:
  - All categories present
  - All techniques present
  - Russian text displays correctly
  - Relationships correct
- [ ] Test database queries:
  - Filter techniques by category
  - Count activities by type
  - Verify timestamp functionality

**Deliverables:**
- All data integrity verified
- Admin interface fully functional
- Ready for Phase 2

---

## Phase 2: Authentication and Core Navigation

### 2.1. User Authentication

**Authentication Approach:**
- **Login:** Users authenticate via Django Admin (`/admin/`)
- **Session:** Django's session middleware automatically handles authentication across the entire site
- **No separate login page:** No `/login/` URL or login template needed
- **No login links:** Main screen has no login links - users login via `/admin/`

**Tasks:**
- [ ] Verify Django authentication middleware is configured (already in settings.py)
- [ ] Configure `LOGIN_REDIRECT_URL` in settings.py (optional, admin has its own redirect)
- [ ] Test that logging in at `/admin/` authenticates user across entire site
- [ ] Verify session persistence works correctly

**Deliverables:**
- Authentication via admin interface working
- Session persists across entire site
- No login links on main screen

---

### 2.2. Home View Logic

**Tasks:**
- [ ] Create `home_view` in `tracker/views.py`:
  - Check authentication status
  - Check if user is superuser
  - Calculate activity counts (RESIST, SMOKED, SPORT)
  - Render appropriate template
- [ ] Create URL route for home (`/`)
- [ ] Create base template (`templates/base.html`):
  - Include motivational banner
  - Russian phrase hardcoded
  - Mobile-responsive structure
- [ ] Create home template (`templates/home.html`):
  - Superuser: Full template with Activity Tracker
  - Guest: Redirect handled in view

**Deliverables:**
- Home view with conditional rendering
- Motivational banner integrated
- Proper authentication checks

---

### 2.3. Static UI Foundation

**Tasks:**
- [ ] Create base CSS (`static/css/base.css`):
  - Mobile-first responsive design
  - Portrait-only layout
  - Typography (Russian-friendly fonts)
  - Color scheme (green banner, activity colors)
- [ ] Create base template structure:
  - Header with banner
  - Main content area
  - Navigation (if needed)
- [ ] Test responsive design:
  - 375px to 420px width
  - Portrait orientation
  - Landscape warning message

**Deliverables:**
- Base template and CSS complete
- Mobile-responsive foundation
- Motivational banner styled

---

### 2.4. Breathing Menu

**Tasks:**
- [ ] Create `category_list_view` in `breathe/views.py`:
  - Fetch all categories
  - Order by `order` field or name
  - Render Russian names
- [ ] Create `technique_list_view`:
  - Filter techniques by category
  - Display Russian names
- [ ] Create templates:
  - `templates/breathe/categories.html` (category menu)
  - `templates/breathe/techniques.html` (techniques in category)
- [ ] Create URL routes:
  - `/breathe/` (categories)
  - `/breathe/<category_id>/` (techniques)
- [ ] Style breathing menu:
  - Mobile-friendly card layout
  - Russian text display
  - Navigation back to categories

**Deliverables:**
- Category browsing functional
- Technique selection functional
- All Russian text displaying correctly

---

## Phase 3: The Activity Tracker Implementation

### 3.1. Counter Logic

**Tasks:**
- [ ] Update `home_view` to calculate counts:
  - Query `ActivityLog` filtered by user
  - Count by `activity_type`
  - Pass counts to template
- [ ] Create helper function for count calculation:
  ```python
  def get_activity_counts(user):
      return {
          'resist': ActivityLog.objects.filter(
              user=user, activity_type='RESIST'
          ).count(),
          'smoked': ActivityLog.objects.filter(
              user=user, activity_type='SMOKED'
          ).count(),
          'sport': ActivityLog.objects.filter(
              user=user, activity_type='SPORT'
          ).count(),
      }
  ```

**Deliverables:**
- Accurate count calculations
- Efficient database queries

---

### 3.2. Logging Endpoint

**Tasks:**
- [ ] Create `activity_tap` view in `tracker/views.py`:
  - Accept AJAX POST request
  - Validate user authentication
  - Validate `activity_type` (RESIST, SMOKED, SPORT)
  - Implement rate limiting (3 seconds between similar types)
  - Save `ActivityLog` entry
  - Return JSON response
- [ ] Create URL route: `/api/activity/tap/`
- [ ] Add CSRF token handling for AJAX
- [ ] Test rate limiting:
  - Rapid taps should be limited
  - Different activity types can be logged quickly

**Deliverables:**
- AJAX endpoint functional
- Rate limiting working
- Proper error handling

---

### 3.3. Frontend (Superuser)

**Tasks:**
- [ ] Create activity tracker HTML in `templates/home.html`:
  - Three counter badges
  - Color-coded (Green, Red-Orange, Blue)
  - Display counts
  - Russian labels (Бросил, Сорвался, Активность)
- [ ] Create `static/js/activity-tracker.js`:
  - AJAX POST on badge tap
  - Handle success response
  - Update badge count display
  - Trigger visual feedback animations
- [ ] Implement visual feedback:
  - Confetti burst (RESIST) - use library or CSS animation
  - Dull grey-out (SMOKED) - CSS transition
  - Success glow (SPORT) - CSS animation
- [ ] Style badges:
  - Bold, clean fonts
  - Large tap targets
  - Mobile-friendly sizing

**Deliverables:**
- Interactive counter badges
- Visual feedback working
- AJAX integration complete

---

### 3.4. Testing

**Tasks:**
- [ ] Test counter functionality:
  - Tap each badge
  - Verify count increments
  - Verify database entry created
  - Verify rate limiting
- [ ] Test visual feedback:
  - Each activity type triggers correct animation
  - Animations don't interfere with functionality
- [ ] Test on mobile device:
  - Tap targets large enough
  - Responsive layout works

**Deliverables:**
- Activity Tracker fully functional
- All edge cases handled
- Ready for Phase 4

---

## Phase 4: The Breathing Guide (UX/UI & Logic)

### 4.1. Audio Generation

**Tasks:**
- [ ] Set up Google Cloud TTS:
  - Create service account
  - Store API key as environment variable
  - Install `google-cloud-texttospeech` library
- [ ] Create script to generate audio files:
  - Generate phase cues (inhale, exhale, hold)
  - Generate number counts (1-10)
  - Use Wavenet voice (ru-RU-Wavenet-D or E)
  - Export as MP3, 96 kbps
  - Save to `static/audio/ru/`
- [ ] Verify all audio files generated:
  - 3 phase cues
  - 10 number counts
  - Total: 13 files
- [ ] Test audio playback:
  - Files load correctly
  - Playback works in browser
  - Quality acceptable

**Deliverables:**
- All Russian TTS audio files generated
- Files stored in correct location
- Audio playback verified

---

### 4.2. Preparation Screen

**Tasks:**
- [ ] Create `preparation_view` in `breathe/views.py`:
  - Fetch technique by ID
  - Pass technique data to template
- [ ] Create `templates/breathe/preparation.html`:
  - Display technique name (Russian)
  - Display `instructions_ru` (full text)
  - Display `posture_ru`
  - **Summary Confirmation Section:**
    - Название: [technique name_ru]
    - Общая длительность: [recommended_time_min] минуты
    - Цикл: Вдох [inhale] с / Задержка [hold_start] с / Выдох [exhale] с
    - Положение: [posture_ru]
    - Фокус: [breath_origin description in Russian]
  - Sound toggle (on/off)
  - Vibration toggle (on/off)
  - "Start" button (Начать)
- [ ] Create JavaScript for toggles:
  - Store preferences in Local Storage (`soundCueEnabled`, `vibrationCueEnabled`)
  - Default to `true` if keys don't exist
  - Update UI state
- [ ] Create URL route: `/breathe/technique/<id>/`
- [ ] Style preparation screen:
  - Mobile-friendly layout
  - Readable instructions
  - Clear toggle controls

**Deliverables:**
- Preparation screen functional
- Toggles working with Local Storage
- Russian text displaying correctly

---

### 4.3. Guide Screen Layout

**Tasks:**
- [ ] Create `guide_view` in `breathe/views.py`:
  - Fetch technique by ID
  - Pass technique data to template
- [ ] Create `templates/breathe/guide.html`:
  - Progress bar (top)
  - Dynamic text cue area
  - Balloon container (center)
  - Torso graphic container (center)
  - Status icons (sound/vibration)
  - Pause button (⏸️)
  - Cancel button (X)
- [ ] Create `static/css/guide.css`:
  - Mobile portrait layout
  - Balloon styling (Deep Teal #00A38D)
  - Torso graphic styling
  - Progress bar styling
  - Control button styling
- [ ] Create SVG/CSS for torso graphic:
  - **Reference:** See `docs/TORSO_IMPLEMENTATION.md` for complete implementation details
  - Simple line drawing (SVG-based)
  - Base color: #E0E0E0 (faint light gray)
  - Distinct horizontal line separating Chest from Abdomen
  - Areas for abdomen, chest clearly defined
  - Ready for pulse effects based on `breath_origin`
  - Implement `TorsoPulseController` JavaScript class for state management
  - Synchronize pulse animations with breathing phases

**Deliverables:**
- Guide screen HTML/CSS complete
- All visual elements positioned
- Mobile-responsive layout

---

### 4.4. JavaScript Engine (Core Logic)

**Tasks:**
- [ ] Create `static/js/breathing-guide.js`:
  - Main function: `startBreathingTechnique(technique)`
  - Read timing parameters
  - Initialize animation loop
- [ ] Implement balloon animation:
  - `requestAnimationFrame` loop
  - Calculate current phase based on elapsed time
  - Animate size: 30% to 80% Vw
  - Smooth transitions
- [ ] Implement torso pulse:
  - Map `breath_origin` to body area
  - Inhale: 0% to 50% opacity, color brighten
  - Exhale: 50% to 0% opacity, color dim
  - Synchronize with balloon
- [ ] Implement progress bar:
  - Calculate total time remaining
  - Update every second
  - Visual fill animation
- [ ] Integrate audio:
  - Check Local Storage for sound preference (default: `true` if not set)
  - Load audio files using Django static paths: `/static/audio/ru/`
  - Use JavaScript Audio API: `new Audio('/static/audio/ru/phase_inhale.mp3')`
  - Preload audio files on-demand when technique starts
  - Measure phase cue duration at runtime to prevent overlap
  - Play phase cues at phase start (0s)
  - Play number counts every second during all phases
  - Handle missing files gracefully
- [ ] Integrate haptic feedback:
  - Check Local Storage for vibration preference
  - Use Web Vibration API
  - Trigger at phase transitions
  - Handle unsupported devices
- [ ] Implement pause/resume:
  - Pause button stops timer and animation
  - Resume button continues from pause point
  - Update button text (Пауза / Продолжить)
- [ ] Implement cancel:
  - Update BreathingSession record if exists (mark as incomplete)
  - Cancel button stops session
  - Returns to category menu
  - Clears session data
- [ ] Implement Page Visibility API:
  - Pause on tab blur
  - Resume on tab focus
  - Continue audio if possible
- [ ] Implement completion:
  - Detect when session time complete
  - Save BreathingSession record to database:
    - Set `started_at` (from session start)
    - Set `completed_at` (current time)
    - Calculate `duration_seconds`
    - Set `completed=True`
    - Record `cycles_completed`
    - Record `sound_enabled` and `vibration_enabled` from Local Storage
  - Display success message (Russian)
  - Auto-redirect to category menu
- [ ] Implement session tracking on start:
  - Create BreathingSession record when user clicks "Start"
  - Set `started_at` to current time
  - Set `technique`, `user`, `sound_enabled`, `vibration_enabled`
  - Set `completed=False` initially
- [ ] Handle cancel:
  - Update BreathingSession record if exists:
    - Set `completed_at` to current time
    - Calculate `duration_seconds`
    - Set `completed=False`
    - Record `cycles_completed` up to cancellation point

**Deliverables:**
- Complete breathing guide JavaScript
- All animations working
- Audio and haptic integrated
- Pause/cancel functional
- Completion flow working

---

### 4.5. Testing

**Tasks:**
- [ ] Test all 18 techniques:
  - Each technique loads correctly
  - Timing parameters correct
  - Animations synchronized
  - Audio cues play (if enabled)
  - Haptic feedback works (if enabled)
- [ ] Test pause/resume:
  - Pause stops correctly
  - Resume continues correctly
  - State preserved
- [ ] Test cancel:
  - Returns to menu
  - No errors
- [ ] Test completion:
  - Success message displays
  - Auto-redirect works
- [ ] Test on mobile device:
  - Touch interactions work
  - Animations smooth
  - Audio plays
  - Vibration works (if supported)
- [ ] Test edge cases:
  - Missing audio files
  - Network errors
  - Tab switching
  - Device rotation (portrait lock)

**Deliverables:**
- All breathing techniques functional
- All features tested
- Ready for Phase 5

---

## Phase 5: Deployment and Finalization

### 5.1. Mobile Optimization

**Tasks:**
- [ ] Final responsive design audit:
  - Test on multiple screen sizes (375px, 390px, 420px)
  - Verify portrait-only behavior
  - Test landscape warning message
  - Check touch target sizes
- [ ] Performance optimization:
  - Minify JavaScript
  - Optimize CSS
  - Compress images (if any)
  - Verify audio file sizes
- [ ] Cross-browser testing:
  - Chrome (Android)
  - Safari (iOS)
  - Firefox (Android)
  - Edge (if applicable)
- [ ] Accessibility check:
  - Color contrast
  - Touch target sizes
  - Text readability

**Deliverables:**
- Mobile-optimized application
- Cross-browser compatible
- Performance optimized

---

### 5.2. Production Setup

**Tasks:**
- [ ] Configure PostgreSQL:
  - Create production database
  - Update `settings.py` for production
  - Test database connection
- [ ] Set up environment variables:
  - `SECRET_KEY`
  - `DATABASE_URL`
  - `TTS_API_KEY` (if needed for future)
  - `DEBUG=False`
- [ ] Configure static files:
  - Collect static files: `python manage.py collectstatic`
  - Verify Cloudflare configuration
  - Test static file serving
- [ ] Set up Gunicorn:
  - Install Gunicorn
  - Create systemd service (if applicable)
  - Configure worker processes
- [ ] Configure Nginx (if needed):
  - Reverse proxy setup
  - Static file serving
  - SSL configuration

**Deliverables:**
- Production environment configured
- Static files served correctly
- Database configured

---

### 5.3. Deployment

**Tasks:**
- [ ] Set up DigitalOcean droplet:
  - Choose Basic Droplet ($6/mo)
  - Select nearest regional datacenter
  - Configure SSH access
- [ ] Deploy application:
  - Clone repository
  - Set up virtual environment
  - Install dependencies
  - Run migrations
  - Load fixtures
  - Create superuser
  - Collect static files
- [ ] Configure Cloudflare:
  - Add domain
  - Configure DNS
  - Enable CDN for static files
  - Set up SSL
- [ ] Test production deployment:
  - Verify all URLs work
  - Test authentication
  - Test activity tracker
  - Test breathing guide
  - Verify static files load
  - Check database operations

**Deliverables:**
- Application deployed to production
- All features working in production
- SSL configured

---

### 5.4. Final Testing

**Tasks:**
- [ ] End-to-end testing:
  - Authentication flow
  - Activity tracker (all three types)
  - All 18 breathing techniques
  - Audio cues (enabled/disabled)
  - Haptic feedback (enabled/disabled)
  - Pause/resume
  - Cancel
  - Completion
- [ ] Error handling testing:
  - Missing audio files
  - Network errors
  - Invalid inputs
  - Rate limiting
- [ ] Performance testing:
  - Page load times
  - Animation smoothness
  - Audio playback
  - Database query performance
- [ ] Security testing:
  - CSRF protection
  - Authentication required
  - Rate limiting
  - Input validation

**Deliverables:**
- Complete application tested
- All issues resolved
- Production-ready

---

## Post-Deployment

### Maintenance Tasks

- [ ] Monitor application performance
- [ ] Set up error logging (Sentry or similar)
- [ ] Regular database backups
- [ ] Update dependencies as needed
- [ ] Monitor Cloudflare/CDN usage

---

## Timeline Estimate

- **Phase 1:** 2-3 days
- **Phase 2:** 2-3 days
- **Phase 3:** 2-3 days
- **Phase 4:** 5-7 days (most complex)
- **Phase 5:** 2-3 days

**Total:** 13-19 days (approximately 2.5-4 weeks)

---

## Dependencies

- Django 4.x or 5.x
- PostgreSQL (production)
- Google Cloud Text-to-Speech API
- DigitalOcean account
- Cloudflare account
- Domain name (optional)

---

## Notes

- All Russian text should be verified by native speaker
- Audio files should be tested on multiple devices
- Mobile testing should be done on actual devices, not just emulators
- Keep security best practices in mind throughout development

