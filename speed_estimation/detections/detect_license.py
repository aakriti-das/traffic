from ultralytics import YOLO
import cv2
import os
from speed_estimation.config import license_detection_model_path
from .read_license import read_license_plate
from speed_estimation.db.db import update_record,match_license_plate

model = YOLO(license_detection_model_path)


def detect_license_plate(request,vehicle_crop,  prefix="licenseplate"):
    results = model(vehicle_crop)
    detections = []
    output = []
    for idx, result in enumerate(results):
        for box_num, box in enumerate(result.boxes):
            if box.conf > 0.5:  # Confidence threshold
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'confidence': box.conf.item()
                })
                # Draw bounding box on the vehicle_crop
                cv2.rectangle(vehicle_crop, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    vehicle_crop,
                    f"{box.conf.item():.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                # Save cropped license plate if save_dir is provided

                crop = vehicle_crop[y1:y2, x1:x2]
                if crop.size > 0:
                    license_text = read_license_plate(crop)
                    # Append bbox and text
                    output.append(((x1, y1, x2, y2), license_text, crop))
    return output

# Example usage:
# img = cv2.imread('nepali licenseplate.jpeg')
# detect_license_plate(img, save_dir="licenseplates", prefix="test")
# cv2.imshow('Input Image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows