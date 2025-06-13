from ultralytics import YOLO
import cv2
import os
from speed_estimation.config import license_detection_model_path
from .read_license import read_license_plate
from speed_estimation.db.db import update_record,match_license_plate

model = YOLO(license_detection_model_path)

save_dir ="licenseplates"  # Directory to save cropped license plates

def detect_license_plate(vehicle_crop,record,  prefix="licenseplate"):
    #apply license detection model on recieved image
    results = model(vehicle_crop)
    detections = []
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
                if save_dir is not None:
                    os.makedirs(save_dir, exist_ok=True)
                    crop = vehicle_crop[y1:y2, x1:x2]
                    if crop.size > 0:
                        filename = os.path.join(save_dir, f"{prefix}_{idx}_{box_num}.jpg")
                        cv2.imwrite(filename, crop)
                        # print(f"Saved license plate crop to {filename}")
                        cv2.imshow('Cropped License Plate', crop)  # Display the cropped license plate
                        cv2.waitKey(1)
                        record=update_record(record.id,None,crop)
                        license_text = read_license_plate(crop)
                        record=update_record(record.id,license_text,None)
                        print(f"Detected license text: {license_text}")
                        match_license_plate(record)
    return detections

# Example usage:
# img = cv2.imread('nepali licenseplate.jpeg')
# detect_license_plate(img, save_dir="licenseplates", prefix="test")
# cv2.imshow('Input Image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()