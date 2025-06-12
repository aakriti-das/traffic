import ultralytics
from ultralytics import YOLO
from speed_estimation.config import vehicle_detection_model_path, VEHICLE_CLASSES

import supervision as sv
import numpy as np

model = YOLO(vehicle_detection_model_path)

def detect_vehicle(frame: np.ndarray) -> tuple[sv.Detections, np.ndarray]:
    results = model(frame)
    result = results[0]

    # Extract raw YOLO boxes
    yolo_boxes = result.boxes
    class_names = result.names

    detections = []

    xyxy = []
    confidences = []
    class_ids = []

    for box in yolo_boxes:
        cls_id = int(box.cls[0])
        class_name = class_names[cls_id]
        conf = box.conf.item()

        if class_name in VEHICLE_CLASSES and conf > 0.5:
            print(f"Detected vehicle: {class_name}")
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            xyxy.append([x1, y1, x2, y2])
            confidences.append(conf)
            class_ids.append(cls_id)

    # Build sv.Detections object (required for ByteTrack)
    if len(xyxy) == 0:
        detections = sv.Detections.empty()
    else:
        detections = sv.Detections(
        xyxy=np.array(xyxy, dtype=np.float32),
        confidence=np.array(confidences, dtype=np.float32),
        class_id=np.array(class_ids, dtype=int),
        )

    return detections, frame
