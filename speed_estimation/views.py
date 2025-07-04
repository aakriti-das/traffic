# from django.shortcuts import render
# from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.clickjacking import xframe_options_exempt
# import json
# import cv2
# import numpy as np
# import logging
# # from .camera.video_camera import VideoCamera
# # from .utils.speed import calculate_speed

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Global video camera instance
# camera = None

# def index(request):
#     return render(request, 'base.html')

# # @xframe_options_exempt
# # def video_feed(request):
# #     try:
# #         logger.debug("Video feed requested")
# #         cam = get_camera()
# #         if cam is None:
# #             logger.error("Could not initialize camera")
# #             return HttpResponse("Error: Could not initialize camera", status=500)
        
# #         logger.debug("Creating streaming response")
# #         response = StreamingHttpResponse(
# #             gen(cam),
# #             content_type='multipart/x-mixed-replace; boundary=frame'
# #         )
# #         response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
# #         response['Pragma'] = 'no-cache'
# #         response['Expires'] = '0'
# #         response['X-Accel-Buffering'] = 'no'
# #         return response
# #     except Exception as e:
# #         logger.error(f"Error in video_feed: {str(e)}")
# #         return HttpResponse(f"Error: {str(e)}", status=500)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from speed_estimation.state_manager import vehicle_state
import json

@csrf_exempt
@require_http_methods(["POST"])
def get_stats(request):
    """Get real-time vehicle statistics"""
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
    """Dummy stats for testing when video processing is not running"""
    return JsonResponse({
        'vehicle_count': 5,
        'current_speed': 45,
        'status': 'dummy'
    })
