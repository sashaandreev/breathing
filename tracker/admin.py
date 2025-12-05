from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Admin interface for ActivityLog model."""
    
    list_display = ['id', 'user', 'activity_type', 'timestamp']
    list_filter = ['activity_type', 'timestamp', 'user']
    search_fields = ['user__username', 'activity_type']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'activity_type', 'timestamp')
        }),
    )
