# Breathing Session History Feature

## Overview

The application tracks all breathing sessions in the database for later analysis. This allows the user to analyze patterns, track progress, and correlate breathing exercises with activity logs.

## Model: BreathingSession

**Location:** `breathe/models.py`

**Purpose:** Store complete records of every breathing session attempt.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey(User) | User who performed the session |
| `technique` | ForeignKey(BreathingTechnique) | Which breathing technique was used |
| `started_at` | DateTimeField | When the session started |
| `completed_at` | DateTimeField (nullable) | When the session ended (null if cancelled) |
| `duration_seconds` | IntegerField (nullable) | Actual duration in seconds |
| `completed` | BooleanField | True if completed, False if cancelled |
| `cycles_completed` | IntegerField (nullable) | Number of breathing cycles completed |
| `sound_enabled` | BooleanField | Whether sound cues were enabled |
| `vibration_enabled` | BooleanField | Whether vibration cues were enabled |

### Usage

**On Session Start:**
- Create new `BreathingSession` record
- Set `started_at` = current time
- Set `technique` = selected technique
- Set `user` = current user
- Set `sound_enabled` and `vibration_enabled` from Local Storage
- Set `completed` = False
- Set `cycles_completed` = 0

**During Session:**
- Track `cycles_completed` as user progresses

**On Session Completion:**
- Set `completed_at` = current time
- Calculate `duration_seconds` = `completed_at` - `started_at`
- Set `completed` = True
- Save final `cycles_completed` count

**On Session Cancel:**
- Set `completed_at` = current time
- Calculate `duration_seconds` = `completed_at` - `started_at`
- Set `completed` = False
- Save current `cycles_completed` count

## Analytics Use Cases

### 1. Technique Usage Analysis
- Which techniques are used most frequently?
- Which categories are preferred?
- Usage patterns over time (daily, weekly, monthly)

### 2. Completion Rate Analysis
- What percentage of sessions are completed vs cancelled?
- Average session duration
- Correlation between technique and completion rate

### 3. Progress Tracking
- Total sessions completed
- Total time spent on breathing exercises
- Trends over time (increasing/decreasing usage)

### 4. Correlation Analysis
- Relationship between breathing sessions and activity logs
- Do breathing sessions correlate with RESIST activities?
- Patterns before/after SMOKED events

### 5. Preference Analysis
- Most common sound/vibration settings
- Do preferences affect completion rates?

## Admin Interface

**Access:** Django Admin (`/admin/breathe/breathingsession/`)

**Features:**
- View all sessions
- Filter by user, technique, date, completion status
- Search by technique name
- Export data for external analysis
- View statistics and summaries

**Display Fields:**
- User
- Technique (with category)
- Started at
- Duration
- Completed status
- Cycles completed
- Preferences

## Implementation Notes

- **Performance:** Add database indexes on `user`, `technique`, and `started_at` for efficient queries
- **Privacy:** Since this is a single-user application, all sessions belong to the superuser
- **Data Retention:** No automatic deletion - all history is preserved for analysis
- **Export:** Can export to CSV/JSON via Django Admin for external analysis tools

## Example Queries

```python
# Total sessions completed
BreathingSession.objects.filter(completed=True).count()

# Most used technique
BreathingSession.objects.values('technique__name_ru').annotate(
    count=Count('id')
).order_by('-count').first()

# Average session duration
BreathingSession.objects.filter(completed=True).aggregate(
    avg_duration=Avg('duration_seconds')
)

# Sessions this month
from datetime import datetime, timedelta
month_start = datetime.now().replace(day=1)
BreathingSession.objects.filter(started_at__gte=month_start)
```

## Integration Points

1. **Session Start:** Create record when user clicks "Start" button
2. **Cycle Tracking:** Update `cycles_completed` during session
3. **Session End:** Update record on completion or cancellation
4. **Admin View:** Access via Django Admin for analysis

