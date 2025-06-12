import cv2
import numpy as np
from speed_estimation.detections.detect_vehicle import detect_vehicle
from .vehicle_tracker import track_vehicles
from .config import video_path

def process_video_stream():
    cap = cv2.VideoCapture(video_path)
    # cap = cv2.VideoCapture(0)  # 0 for webcam; replace with IP stream if needed
    fps = cap.get(cv2.CAP_PROP_FPS)
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        detections, frame = detect_vehicle(frame)
        annotated_frame, tracked_detections = track_vehicles(frame, detections,fps)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        # Yield frame in byte format
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == "__main__":
    process_video_stream() 