from django.db import models
from django.contrib.auth.models import User


class BreathingCategory(models.Model):
    """Organizes breathing techniques into 6 categories."""
    
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="English name (internal, optional)"
    )
    name_ru = models.CharField(
        max_length=100,
        help_text="Russian display name (required)"
    )
    description_ru = models.TextField(
        blank=True,
        null=True,
        help_text="Category description in Russian (optional)"
    )
    order = models.IntegerField(
        blank=True,
        null=True,
        help_text="Display order (not used, categories ordered by PK)"
    )
    
    class Meta:
        verbose_name = "Breathing Category"
        verbose_name_plural = "Breathing Categories"
        ordering = ['pk']  # Order by primary key as per fixture
    
    def __str__(self):
        return self.name_ru


class BreathingTechnique(models.Model):
    """Stores all parameters for breathing exercises. All user-facing content in Russian."""
    
    BREATH_ORIGIN_CHOICES = [
        ('ABDOMEN', 'ABDOMEN'),
        ('CHEST', 'CHEST'),
        ('NOSTRILS', 'NOSTRILS'),
        ('MOUTH', 'MOUTH'),
        ('ALL', 'ALL'),
    ]
    
    category = models.ForeignKey(
        BreathingCategory,
        on_delete=models.CASCADE,
        related_name='techniques',
        help_text="Category this technique belongs to"
    )
    name_ru = models.CharField(
        max_length=200,
        help_text="Display name in Russian"
    )
    inhale = models.IntegerField(
        help_text="Inhale duration (seconds)"
    )
    hold_start = models.IntegerField(
        help_text="Hold after inhale (seconds)"
    )
    exhale = models.IntegerField(
        help_text="Exhale duration (seconds)"
    )
    hold_end = models.IntegerField(
        help_text="Hold after exhale (seconds)"
    )
    recommended_time_min = models.IntegerField(
        help_text="Total session duration (minutes)"
    )
    posture_ru = models.CharField(
        max_length=100,
        help_text="Quick preparation cue (e.g., 'Сидя')"
    )
    breath_origin = models.CharField(
        max_length=20,
        choices=BREATH_ORIGIN_CHOICES,
        help_text="Focus area: ABDOMEN, CHEST, NOSTRILS, MOUTH, or ALL"
    )
    instructions_ru = models.TextField(
        help_text="Detailed step-by-step instructions in Russian"
    )
    use_sound_cue = models.BooleanField(
        default=True,
        help_text="Default sound toggle state"
    )
    use_haptic_cue = models.BooleanField(
        default=True,
        help_text="Default vibration toggle state"
    )
    
    class Meta:
        verbose_name = "Breathing Technique"
        verbose_name_plural = "Breathing Techniques"
        ordering = ['category', 'id']
        indexes = [
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.name_ru
    
    @property
    def cycle_duration_seconds(self):
        """Calculate total duration of one breathing cycle in seconds."""
        return self.inhale + self.hold_start + self.exhale + self.hold_end


class BreathingSession(models.Model):
    """Tracks completed breathing sessions for later analysis."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='breathing_sessions',
        help_text="User who performed the session"
    )
    technique = models.ForeignKey(
        BreathingTechnique,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="Which breathing technique was used"
    )
    started_at = models.DateTimeField(
        help_text="When the session started"
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the session ended (null if cancelled)"
    )
    duration_seconds = models.IntegerField(
        blank=True,
        null=True,
        help_text="Actual session duration in seconds"
    )
    completed = models.BooleanField(
        default=False,
        help_text="Whether session was completed (vs cancelled)"
    )
    cycles_completed = models.IntegerField(
        blank=True,
        null=True,
        help_text="Number of breathing cycles completed"
    )
    sound_enabled = models.BooleanField(
        default=True,
        help_text="Whether sound cues were enabled"
    )
    vibration_enabled = models.BooleanField(
        default=True,
        help_text="Whether vibration cues were enabled"
    )
    
    class Meta:
        verbose_name = "Breathing Session"
        verbose_name_plural = "Breathing Sessions"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['technique']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        status = "Completed" if self.completed else "Cancelled"
        return f"{self.user.username} - {self.technique.name_ru} - {status} - {self.started_at}"
    
    def save(self, *args, **kwargs):
        """Calculate duration_seconds if completed_at is set."""
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
        super().save(*args, **kwargs)
