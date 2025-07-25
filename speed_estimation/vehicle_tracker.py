import os
import supervision as sv
import numpy as np
import cv2
from collections import deque
from speed_estimation.utils.speed import calculate_speed
from speed_estimation.utils.nepaliframe import draw_nepali_text_on_frame
from speed_estimation.config import speed_limit,perspective_matrix
from speed_estimation.detections.detect_license import detect_license_plate
from speed_estimation.db.db import save_record,match_license_plate
from datetime import datetime 
from speed_estimation.state_manager import vehicle_state

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

save_dir ="Detected_licenseplates"  # Directory to save cropped license plates
os.makedirs(save_dir, exist_ok=True)
saved_tracker_ids = set()
plate_memory = {}

def track_vehicles(request,frame: np.ndarray, detections: sv.Detections, fps) -> tuple[np.ndarray, sv.Detections]:
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
        confidence = tracked_detections.confidence[i] if hasattr(tracked_detections, 'confidence') else None

        # Update global state manager
        vehicle_state.update_vehicle_position(tracker_id, transformed_center, speed, confidence)

        if confidence is not None:
            conf_text = f"{confidence:.2f}"
        else:
            conf_text = "N/A"
        # Annotate label and log
        if speed <=speed_limit:
            label = f"ID {tracker_id} {speed:.1f} km/h {conf_text}"
        else:
            label = f"ID {tracker_id} {speed:.1f} km/h Overspeeding {conf_text}"
        
        labels.append(label)
        print(f"[TRACK] Vehicle ID {tracker_id} | Speed: {speed:.1f} km/h")

        # if speed > 15:
        if speed > speed_limit:
            if tracker_id not in saved_tracker_ids:
                print(f"[ALERT] Vehicle ID {tracker_id} is exceeding the speed limit!")
                crop = frame[y1i:y2i, x1i:x2i]
                if crop is None or crop.size == 0:
                    print(f"[WARNING] Invalid crop for vehicle {tracker_id}, skipping.")
                    continue
                if crop.size > 0:
                    # saved_tracker_ids.add(tracker_id) #To be removed
                    filename = f"{SPEEDING_DIR}/Vehicle2_{tracker_id}_{int(speed)}.jpg"
                    cv2.imwrite(filename, crop)
                    print(f"Saved speeding vehicle crop to {filename}")

                    license_detections = detect_license_plate(request,crop)
                    # license_detections=None
                    if license_detections:
                        crop_height,crop_width=crop.shape[:2]
                        # Assume only one plate per vehicle
                        (lx1, ly1, lx2, ly2), plate_text ,license_photo = license_detections[0]
                        relative_bbox = (lx1, ly1, lx2, ly2)
                        plate_memory[tracker_id] = {
                        "relative_bbox": relative_bbox,
                        "plate_text": plate_text,
                        "crop_dims": (crop_width, crop_height)
                                   }
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  
                        platefilename = os.path.join(save_dir, f"LicensePlate_{timestamp}.jpg")
                        cv2.imwrite(platefilename, license_photo)
                        
                        saved_tracker_ids.add(tracker_id)  # Mark as saved
                        if len(plate_text) > 4:
                            record=save_record(request,speed, 1, filename,platefilename,plate_text)
                            print(f"Detected license text: {plate_text}")
                            match_license_plate(request,record)

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
    
            # Draw plate box -->Removed because it slows down the processing
            cv2.rectangle(frame,(gx1, gy1), (gx2, gy2), (0, 255, 255), 2)
            frame = draw_nepali_text_on_frame(frame, plate_text, (gx1, gy1 - 30))

    # Annotate frame
    annotated_frame = label_annotator.annotate(
        scene=frame, detections=tracked_detections, labels=labels
    )
    return annotated_frame, tracked_detections
