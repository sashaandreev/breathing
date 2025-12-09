from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
from .models import BreathingCategory, BreathingTechnique, BreathingSession


def category_list_view(request):
    """Display all breathing categories."""
    # Use prefetch_related to optimize queries - related_name is 'techniques'
    categories = BreathingCategory.objects.all().order_by('pk').prefetch_related('techniques')
    context = {
        'categories': categories,
    }
    return render(request, 'breathe/categories.html', context)


def technique_list_view(request, category_id):
    """Display all techniques for a specific category."""
    category = get_object_or_404(BreathingCategory, pk=category_id)
    # Use select_related to optimize foreign key lookups
    techniques = BreathingTechnique.objects.filter(category=category).select_related('category').order_by('id')
    context = {
        'category': category,
        'techniques': techniques,
    }
    return render(request, 'breathe/techniques.html', context)


def technique_detail_view(request, technique_id):
    """Display technique detail/preparation screen."""
    technique = get_object_or_404(BreathingTechnique.objects.select_related('category'), pk=technique_id)
    # Map breath_origin to Russian description for display
    breath_origin_map = {
        'ABDOMEN': 'Брюшное дыхание',
        'CHEST': 'Грудное дыхание',
        'NOSTRILS': 'Дыхание носом',
        'MOUTH': 'Дыхание ртом',
        'ALL': 'Естественное дыхание',
    }
    technique_breath_origin_ru = breath_origin_map.get(technique.breath_origin, technique.breath_origin)
    
    context = {
        'technique': technique,
        'technique_breath_origin_ru': technique_breath_origin_ru,
    }
    return render(request, 'breathe/preparation.html', context)


def guide_view(request, technique_id):
    """Display active breathing guide screen."""
    technique = get_object_or_404(BreathingTechnique.objects.select_related('category'), pk=technique_id)
    # Map breath_origin to Russian description for display
    breath_origin_map = {
        'ABDOMEN': 'Брюшное дыхание',
        'CHEST': 'Грудное дыхание',
        'NOSTRILS': 'Дыхание носом',
        'MOUTH': 'Дыхание ртом',
        'ALL': 'Естественное дыхание',
    }
    technique_breath_origin_ru = breath_origin_map.get(technique.breath_origin, technique.breath_origin)
    
    context = {
        'technique': technique,
        'technique_breath_origin_ru': technique_breath_origin_ru,
    }
    return render(request, 'breathe/guide.html', context)


@require_http_methods(["POST"])
@login_required
def session_manage(request):
    """
    AJAX endpoint for creating and updating BreathingSession records.
    Handles session start, completion, and cancellation.
    """
    try:
        data = json.loads(request.body)
        action = data.get('action')  # 'start', 'complete', 'cancel'
        technique_id = data.get('technique_id')
        
        if not technique_id:
            return JsonResponse({'success': False, 'error': 'Technique ID required'}, status=400)
        
        technique = get_object_or_404(BreathingTechnique.objects.select_related('category'), pk=technique_id)
        
        if action == 'start':
            # Create new session
            sound_enabled = data.get('sound_enabled', True)
            vibration_enabled = data.get('vibration_enabled', True)
            
            session = BreathingSession.objects.create(
                user=request.user,
                technique=technique,
                started_at=timezone.now(),
                sound_enabled=sound_enabled,
                vibration_enabled=vibration_enabled,
                completed=False,
                cycles_completed=0
            )
            
            return JsonResponse({
                'success': True,
                'session_id': session.id,
                'message': 'Session started'
            })
        
        elif action == 'update':
            # Update existing session (cycles_completed)
            session_id = data.get('session_id')
            cycles_completed = data.get('cycles_completed', 0)
            
            if not session_id:
                return JsonResponse({'success': False, 'error': 'Session ID required'}, status=400)
            
            try:
                session = BreathingSession.objects.select_related('technique', 'technique__category').get(pk=session_id, user=request.user)
                session.cycles_completed = cycles_completed
                session.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Session updated'
                })
            except BreathingSession.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
        
        elif action == 'complete':
            # Mark session as completed
            session_id = data.get('session_id')
            cycles_completed = data.get('cycles_completed', 0)
            
            if not session_id:
                return JsonResponse({'success': False, 'error': 'Session ID required'}, status=400)
            
            try:
                session = BreathingSession.objects.select_related('technique', 'technique__category').get(pk=session_id, user=request.user)
                session.completed_at = timezone.now()
                session.completed = True
                session.cycles_completed = cycles_completed
                session.save()  # duration_seconds calculated in save() method
                
                return JsonResponse({
                    'success': True,
                    'message': 'Session completed',
                    'duration_seconds': session.duration_seconds
                })
            except BreathingSession.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
        
        elif action == 'cancel':
            # Mark session as cancelled
            session_id = data.get('session_id')
            cycles_completed = data.get('cycles_completed', 0)
            
            if not session_id:
                return JsonResponse({'success': False, 'error': 'Session ID required'}, status=400)
            
            try:
                session = BreathingSession.objects.select_related('technique', 'technique__category').get(pk=session_id, user=request.user)
                session.completed_at = timezone.now()
                session.completed = False
                session.cycles_completed = cycles_completed
                session.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Session cancelled'
                })
            except BreathingSession.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
        
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
