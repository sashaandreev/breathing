from django.db import models
from django.contrib.auth.models import User


class ActivityLog(models.Model):
    """Stores every interaction with the three counter buttons."""
    
    ACTIVITY_CHOICES = [
        ('RESIST', 'RESIST'),
        ('SMOKED', 'SMOKED'),
        ('SPORT', 'SPORT'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES,
        help_text="Type of activity: RESIST, SMOKED, or SPORT"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the activity was logged"
    )
    
    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.timestamp}"
