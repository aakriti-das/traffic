import os
import supervision as sv
import numpy as np
import cv2
from collections import deque
from speed_estimation.utils.speed import calculate_speed
from speed_estimation.utils.nepaliframe import draw_nepali_text_on_frame
from speed_estimation.config import speed_limit,perspective_matrix
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
plate_memory = {}

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
        center_y = (y1 + y2) / 2
        center = np.array([[ [center_x, center_y] ]], dtype='float32')

        # Apply perspective transform
        transformed_center = cv2.perspectiveTransform(center, perspective_matrix)[0][0]

        # Update position history
        if tracker_id not in vehicle_positions:
            vehicle_positions[tracker_id] = deque(maxlen=MAX_HISTORY)
        vehicle_positions[tracker_id].append(transformed_center)
        # print(f"History for vehicle {tracker_id}: {list(vehicle_positions[tracker_id])}")

        # Calculate speed only if there are at least 2 positions
        if len(vehicle_positions[tracker_id]) > 1:
            speed = calculate_speed(vehicle_positions[tracker_id], fps)
        else:
            speed = 0.0
        
        x1i, y1i, x2i, y2i = map(int, [x1, y1, x2, y2])
        # Annotate label and log
        if speed <=speed_limit:
            label = f"ID {tracker_id} {speed:.1f} km/h"
        else:
            label = f"ID {tracker_id} {speed:.1f} km/h Overspeeding"
        
        labels.append(label)
        print(f"[TRACK] Vehicle ID {tracker_id} | Speed: {speed:.1f} km/h")

        if speed > speed_limit:
            if tracker_id not in saved_tracker_ids:
                print(f"[ALERT] Vehicle ID {tracker_id} is exceeding the speed limit!")
                crop = frame[y1i:y2i, x1i:x2i]
                if crop is None or crop.size == 0:
                    print(f"[WARNING] Invalid crop for vehicle {tracker_id}, skipping.")
                    continue
                if crop.size > 0:
                    filename = f"{SPEEDING_DIR}/vehicle_{tracker_id}_{int(speed)}.jpg"
                    cv2.imwrite(filename, crop)
                    print(f"Saved speeding vehicle crop to {filename}")
                    #cv2.imshow('Speeding Vehicle', crop)
                    #cv2.waitKey(1)
                    record=save_record(speed, 1, filename)  # Pass the filename, not the crop array
                    license_detections = detect_license_plate(crop,record)
                    if license_detections:
                        crop_height,crop_width=crop.shape[:2]
                        # Assume only one plate per vehicle
                        (lx1, ly1, lx2, ly2), plate_text = license_detections[0]
                        relative_bbox = (lx1, ly1, lx2, ly2)
                        plate_memory[tracker_id] = {
                        "relative_bbox": relative_bbox,
                        "plate_text": plate_text,
                        "crop_dims": (crop_width, crop_height)
                    }
                    saved_tracker_ids.add(tracker_id)  # Mark as saved
                # --- Re-draw saved license plate box on current frame ---
        if tracker_id in plate_memory:
            rel = plate_memory[tracker_id]["relative_bbox"]
            lx1, ly1, lx2, ly2 = rel
            # Project relative bbox to current vehicle bbox
            # global_bbox = [x1i + lx1, y1i + ly1, x1i + lx2, y1i + ly2]
            vehicle_crop_width=x2i-x1i
            vehicle_crop_height=y2i-y1i
            crop_width, crop_height = plate_memory[tracker_id]["crop_dims"]

            # Scale the license plate box from crop to global vehicle box dimensions
            scale_x=vehicle_crop_width/crop_width
            scale_y=vehicle_crop_height/crop_height

            # Scale and translate the relative coordinates to full frame
            gx1 = int(x1i + lx1 * scale_x)
            gy1 = int(y1i + ly1 * scale_y)
            gx2 = int(x1i + lx2 * scale_x)
            gy2 = int(y1i + ly2 * scale_y)

            plate_text = plate_memory[tracker_id]["plate_text"]
    
            # Draw plate box
            cv2.rectangle(frame,(gx1, gy1), (gx2, gy2), (0, 255, 0), 2)
            frame = draw_nepali_text_on_frame(frame, plate_text, (gx1, gy1 - 10))
            # cv2.putText(frame, plate_text, (global_bbox[0], global_bbox[1] - 10),
            # cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Annotate frame
    annotated_frame = box_annotator.annotate(
        scene=frame.copy(), detections=tracked_detections
    )
    annotated_frame = label_annotator.annotate(
        scene=annotated_frame, detections=tracked_detections, labels=labels
    )

    return annotated_frame, tracked_detections
