from django.contrib import admin
from .models import BreathingCategory, BreathingTechnique, BreathingSession


@admin.register(BreathingCategory)
class BreathingCategoryAdmin(admin.ModelAdmin):
    """Admin interface for BreathingCategory model."""
    
    list_display = ['id', 'name_ru', 'name', 'order']
    list_filter = ['order']
    search_fields = ['name_ru', 'name', 'description_ru']
    ordering = ['pk']  # Order by primary key as per fixture
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name_ru', 'name', 'description_ru', 'order')
        }),
    )


@admin.register(BreathingTechnique)
class BreathingTechniqueAdmin(admin.ModelAdmin):
    """Admin interface for BreathingTechnique model."""
    
    list_display = ['id', 'name_ru', 'category', 'breath_origin', 'recommended_time_min']
    list_filter = ['category', 'breath_origin', 'use_sound_cue', 'use_haptic_cue']
    search_fields = ['name_ru', 'instructions_ru', 'posture_ru']
    ordering = ['category', 'id']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name_ru', 'breath_origin', 'posture_ru')
        }),
        ('Timing Parameters', {
            'fields': ('inhale', 'hold_start', 'exhale', 'hold_end', 'recommended_time_min'),
            'description': 'All timing values are in seconds, except recommended_time_min which is in minutes.'
        }),
        ('Instructions', {
            'fields': ('instructions_ru',)
        }),
        ('Default Preferences', {
            'fields': ('use_sound_cue', 'use_haptic_cue')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make cycle_duration_seconds read-only if we add it as a computed field."""
        return []


@admin.register(BreathingSession)
class BreathingSessionAdmin(admin.ModelAdmin):
    """Admin interface for BreathingSession model."""
    
    list_display = ['id', 'user', 'technique', 'started_at', 'completed', 'duration_seconds', 'cycles_completed']
    list_filter = ['completed', 'sound_enabled', 'vibration_enabled', 'started_at', 'technique__category']
    search_fields = ['user__username', 'technique__name_ru']
    readonly_fields = ['started_at', 'completed_at', 'duration_seconds']
    date_hierarchy = 'started_at'
    ordering = ['-started_at']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'technique', 'started_at', 'completed_at', 'duration_seconds')
        }),
        ('Session Status', {
            'fields': ('completed', 'cycles_completed')
        }),
        ('Preferences Used', {
            'fields': ('sound_enabled', 'vibration_enabled')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'technique', 'technique__category')
