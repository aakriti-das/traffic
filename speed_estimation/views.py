from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from speed_estimation.state_manager import vehicle_state
import json

@csrf_exempt
@require_http_methods(["POST"])
def get_stats(request):
    try:
        # Get current stats from state manager
        stats = vehicle_state.get_current_stats()
        
        return JsonResponse({
            'vehicle_count': stats['vehicle_count'],
            'current_speed': stats['current_speed'],
            'active_vehicles': stats['active_vehicles'],
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'vehicle_count': 0,
            'current_speed': 0,
            'status': 'error'
        }, status=500)

# Keep the dummy function for testing
def dummy_get_stats(request):
    return JsonResponse({
        'vehicle_count': 5,
        'current_speed': 45,
        'status': 'dummy'
    })
