from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import timedelta
import json
from .models import ActivityLog


def get_activity_counts(user):
    """
    Helper function to calculate activity counts for a user.
    Returns a dictionary with 'resist', 'smoked', and 'sport' counts.
    Optimized to use a single query with aggregation instead of 3 separate queries.
    """
    from django.db.models import Count, Q
    
    # Single query with aggregation - much faster than 3 separate queries
    counts = ActivityLog.objects.filter(user=user).aggregate(
        resist=Count('id', filter=Q(activity_type='RESIST')),
        smoked=Count('id', filter=Q(activity_type='SMOKED')),
        sport=Count('id', filter=Q(activity_type='SPORT'))
    )
    
    return {
        'resist': counts['resist'] or 0,
        'smoked': counts['smoked'] or 0,
        'sport': counts['sport'] or 0,
    }


def home_view(request):
    """
    Home view that checks authentication and renders appropriate content.
    - Superuser: Shows full home with Activity Tracker
    - Guest/Unauthenticated: Redirects to breathing menu
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # Guest user - redirect to breathing menu
        return redirect('breathe:categories')
    
    # Check if user is superuser
    if not request.user.is_superuser:
        # Authenticated but not superuser - redirect to breathing menu
        return redirect('breathe:categories')
    
    # Superuser - calculate activity counts using helper function
    activity_counts = get_activity_counts(request.user)
    
    context = {
        'activity_counts': activity_counts,
    }
    
    return render(request, 'home.html', context)


@require_http_methods(["POST"])
@login_required
def activity_tap(request):
    """
    AJAX endpoint for logging activity taps.
    Validates user authentication, activity type, and implements rate limiting.
    """
    # Check if user is authenticated (login_required decorator handles this, but double-check)
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Требуется авторизация.'
        }, status=401)
    
    # Parse JSON request body
    try:
        data = json.loads(request.body)
        activity_type = data.get('activity_type')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат запроса.'
        }, status=400)
    
    # Validate activity_type
    valid_types = ['RESIST', 'SMOKED', 'SPORT']
    if activity_type not in valid_types:
        return JsonResponse({
            'success': False,
            'error': 'Неверный тип активности.'
        }, status=400)
    
    # Rate limiting: Check if there's a recent entry of the same type (within 3 seconds)
    three_seconds_ago = timezone.now() - timedelta(seconds=3)
    recent_entry = ActivityLog.objects.filter(
        user=request.user,
        activity_type=activity_type,
        timestamp__gte=three_seconds_ago
    ).first()
    
    if recent_entry:
        return JsonResponse({
            'success': False,
            'error': 'Слишком часто. Попробуйте через 3 секунды.',
            'rate_limited': True
        }, status=429)
    
    # Create new ActivityLog entry
    try:
        activity_log = ActivityLog.objects.create(
            user=request.user,
            activity_type=activity_type
        )
        
        # Get updated counts
        counts = get_activity_counts(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Активность зарегистрирована.',
            'counts': counts,
            'activity_id': activity_log.id
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Ошибка при сохранении.'
        }, status=500)
