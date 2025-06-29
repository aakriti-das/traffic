import cv2
import numpy as np
import os
from speed_estimation.detections.detect_vehicle import detect_vehicle
from .vehicle_tracker import track_vehicles
from .config import video_path

def process_video_stream(request):
    # Check if video file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return
    cap = cv2.VideoCapture(video_path)
    # cap = cv2.VideoCapture(0)  # 0 for webcam replace with IP stream if needed
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Video FPS: {fps}")
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        try:
            detections, frame = detect_vehicle(frame)
            annotated_frame, tracked_detections = track_vehicles(request, frame, detections, fps)

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue
                
            frame = buffer.tobytes()
            # Yield frame in byte format
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error processing frame: {e}")
            continue
    cap.release()

if __name__ == "__main__":
    process_video_stream() 