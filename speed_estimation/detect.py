from ultralytics import YOLO
import cv2
import numpy as np
import torch
import supervision as sv
from pathlib import Path
import logging

class VehicleDetector:
    def __init__(self, model_path="models/yolov8m.pt"):
        """
        Initialize the vehicle detector with YOLOv8.
        
        Args:
            model_path: Path to the YOLOv8 model weights
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize YOLO model
        try:
            self.model = YOLO(model_path)
            self.logger.info(f"Loaded YOLOv8 model from {model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load YOLO model: {str(e)}")
            raise
            
        # Set up detection classes (vehicle-related classes from COCO)
        self.target_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        
        # Define colors for different vehicle types (BGR format)
        self.colors = {
            'car': (0, 255, 0),      # Green
            'motorcycle': (255, 0, 0), # Blue
            'bus': (0, 0, 255),       # Red
            'truck': (255, 255, 0)    # Cyan
        }
        
        # Initialize annotator with custom box formatting
        self.box_annotator = sv.BoxAnnotator(
            thickness=3,
            text_thickness=2,
            text_scale=1,
            text_padding=5
        )

    def draw_boxes(self, frame, detections, results):
        """
        Draw custom bounding boxes with detailed information.
        
        Args:
            frame: Input frame
            detections: Supervision detections object
            results: YOLOv8 results object
            
        Returns:
            frame: Annotated frame
        """
        if frame is None or detections is None:
            return frame

        annotated_frame = frame.copy()
        
        for idx, (bbox, class_id, conf) in enumerate(zip(detections.xyxy, detections.class_id, detections.confidence)):
            # Get class name and color
            class_name = results.names[class_id]
            color = self.colors.get(class_name, (0, 255, 0))
            
            # Convert bbox to integer coordinates
            x1, y1, x2, y2 = map(int, bbox)
            
            # Draw filled rectangle for text background
            text = f"{class_name} {conf:.2f}"
            (text_width, text_height), _ = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )
            cv2.rectangle(annotated_frame, (x1, y1 - text_height - 10), 
                         (x1 + text_width + 10, y1), color, -1)
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)
            
            # Draw class name and confidence
            cv2.putText(annotated_frame, text, (x1 + 5, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Draw corner markers
            marker_length = 20
            # Top-left
            cv2.line(annotated_frame, (x1, y1), (x1 + marker_length, y1), color, 4)
            cv2.line(annotated_frame, (x1, y1), (x1, y1 + marker_length), color, 4)
            # Top-right
            cv2.line(annotated_frame, (x2, y1), (x2 - marker_length, y1), color, 4)
            cv2.line(annotated_frame, (x2, y1), (x2, y1 + marker_length), color, 4)
            # Bottom-left
            cv2.line(annotated_frame, (x1, y2), (x1 + marker_length, y2), color, 4)
            cv2.line(annotated_frame, (x1, y2), (x1, y2 - marker_length), color, 4)
            # Bottom-right
            cv2.line(annotated_frame, (x2, y2), (x2 - marker_length, y2), color, 4)
            cv2.line(annotated_frame, (x2, y2), (x2, y2 - marker_length), color, 4)

        return annotated_frame

    def detect(self, frame):
        """
        Perform vehicle detection on a frame.
        
        Args:
            frame: Input frame
            
        Returns:
            tuple: (annotated_frame, detections)
        """
        if frame is None:
            return None, None
            
        try:
            # Run YOLOv8 inference
            results = self.model(frame, verbose=False)[0]
            
            # Convert detections to supervision format
            detections = sv.Detections.from_yolov8(results)
            
            # Filter for vehicle classes
            mask = np.array([class_id in self.target_classes for class_id in detections.class_id])
            detections = detections[mask]
            
            # Draw custom bounding boxes
            annotated_frame = self.draw_boxes(frame, detections, results)
            
            return annotated_frame, detections
            
        except Exception as e:
            self.logger.error(f"Error during detection: {str(e)}")
            return frame, None
            
    def get_vehicle_count(self, detections):
        """
        Get the count of detected vehicles by type.
        
        Args:
            detections: Detections object from detect method
            
        Returns:
            dict: Count of each vehicle type
        """
        if detections is None:
            return {}
            
        counts = {}
        for class_id in detections.class_id:
            class_name = self.model.names[class_id]
            counts[class_name] = counts.get(class_name, 0) + 1
            
        return counts
        
    def download_model(self):
        """Download the YOLOv8 model if not present."""
        model_dir = Path("models")
        model_path = model_dir / "yolov8m.pt"
        
        if not model_dir.exists():
            model_dir.mkdir(parents=True)
            
        if not model_path.exists():
            try:
                torch.hub.download_url_to_file(
                    "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt",
                    str(model_path)
                )
                self.logger.info("Downloaded YOLOv8m model successfully")
            except Exception as e:
                self.logger.error(f"Failed to download model: {str(e)}")
                raise
