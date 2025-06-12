import os
import supervision as sv
import numpy as np
import cv2
from collections import deque
from speed_estimation.utils.speed import calculate_speed
from speed_estimation.config import speed_limit
from speed_estimation.detections.detect_license import detect_license_plate
from speed_estimation.db.db import save_record

# Initialize ByteTrack tracker and annotators once
tracker = sv.ByteTrack()
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

# Position history for speed calculation
vehicle_positions = {}  # tracker_id: deque of x-coordinates
MAX_HISTORY = 10

# Ensure the speeding_vehicles directory exists
SPEEDING_DIR = "speeding_vehicles"
os.makedirs(SPEEDING_DIR, exist_ok=True)

saved_tracker_ids = set()

def track_vehicles(frame: np.ndarray, detections: sv.Detections, fps) -> tuple[np.ndarray, sv.Detections]:
    print("FPS:", fps)
    # Update tracker with the latest detections
    tracked_detections = tracker.update_with_detections(detections)

    labels = []
    # print(f"Tracker IDs this frame: {tracked_detections.tracker_id}")
    num_detections = len(tracked_detections.xyxy)
    for i in range(num_detections):
        tracker_id = tracked_detections.tracker_id[i]

        # Compute center x-coordinate
        x1, y1, x2, y2 = tracked_detections.xyxy[i]
        center_x = (x1 + x2) / 2

        # Update position history
        if tracker_id not in vehicle_positions:
            vehicle_positions[tracker_id] = deque(maxlen=MAX_HISTORY)
        vehicle_positions[tracker_id].append(center_x)
        # print(f"History for vehicle {tracker_id}: {list(vehicle_positions[tracker_id])}")

        # Calculate speed only if there are at least 2 positions
        if len(vehicle_positions[tracker_id]) > 1:
            speed = calculate_speed(vehicle_positions[tracker_id], fps)
        else:
            speed = 0.0

        # Annotate label and log
        label = f"ID {tracker_id} {speed:.1f} km/h"
        labels.append(label)
        print(f"[TRACK] Vehicle ID {tracker_id} | Speed: {speed:.1f} km/h")

        if speed > speed_limit:
            if tracker_id not in saved_tracker_ids:
                print(f"[ALERT] Vehicle ID {tracker_id} is exceeding the speed limit!")
                x1i, y1i, x2i, y2i = map(int, [x1, y1, x2, y2])
                crop = frame[y1i:y2i, x1i:x2i]
                if crop.size > 0:
                    filename = f"{SPEEDING_DIR}/vehicle_{tracker_id}_{int(speed)}.jpg"
                    cv2.imwrite(filename, crop)
                    print(f"Saved speeding vehicle crop to {filename}")
                    cv2.imshow('Speeding Vehicle', crop)
                    cv2.waitKey(1)
                    record=save_record(speed, 1, filename)  # Pass the filename, not the crop array
                    license_detections = detect_license_plate(crop,record)
                    saved_tracker_ids.add(tracker_id)  # Mark as saved
    

    # Annotate frame
    annotated_frame = box_annotator.annotate(
        scene=frame.copy(), detections=tracked_detections
    )
    annotated_frame = label_annotator.annotate(
        scene=annotated_frame, detections=tracked_detections, labels=labels
    )

    return annotated_frame, tracked_detections
