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

# @csrf_exempt
# def get_stats(request):
#     if request.method == 'POST':
#         try:
#             logger.debug("Stats requested")
#             cam = get_camera()
#             if cam is None:
#                 return JsonResponse({'error': 'Camera not initialized'}, status=500)

#             # Get tracked vehicles
#             tracked_vehicles = cam.tracker_id_to_coordinates
#             vehicle_count = len(tracked_vehicles)
            
#             # Calculate max speed
#             speeds = []
#             for coords in tracked_vehicles.values():
#                 if len(coords) >= 2:  # Need at least 2 points to calculate speed
#                     speed = calculate_speed(coords, cam.fps)
#                     speeds.append(speed)
            
#             current_speed = max(speeds) if speeds else 0
            
#             stats = {
#                 'vehicle_count': vehicle_count,
#                 'current_speed': round(current_speed, 1)
#             }
#             logger.debug(f"Stats calculated: {stats}")
#             return JsonResponse(stats)
#         except Exception as e:
#             logger.error(f"Error in get_stats: {str(e)}")
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Method not allowed'}, status=405)
from django.http import JsonResponse

def dummy_get_stats(request):
    return JsonResponse({"message": "No longer supported."})
