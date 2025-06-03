import cv2
import numpy as np
from datetime import datetime
import logging

class VideoProcessor:
    def __init__(self):
        """Initialize the VideoProcessor instance."""
        self.logger = logging.getLogger(__name__)
        self.frame_processors = []
        self.is_processing = False
        
    def add_processor(self, processor_func):
        """
        Add a frame processor function.
        
        Args:
            processor_func: Function that takes a frame and returns processed frame
        """
        self.frame_processors.append(processor_func)
        
    def process_frame(self, frame):
        """
        Process a single frame through all registered processors.
        
        Args:
            frame: Input frame to process
            
        Returns:
            processed_frame: Frame after all processing steps
        """
        if frame is None:
            return None
            
        processed_frame = frame.copy()
        
        try:
            for processor in self.frame_processors:
                processed_frame = processor(processed_frame)
                
                # Check if processor returned a valid frame
                if processed_frame is None:
                    self.logger.error(f"Processor {processor.__name__} returned None")
                    return frame  # Return original frame if processing fails
                    
        except Exception as e:
            self.logger.error(f"Error in frame processing: {str(e)}")
            return frame
            
        return processed_frame
        
    def add_timestamp(self, frame):
        """
        Add timestamp to the frame.
        
        Args:
            frame: Input frame
            
        Returns:
            frame: Frame with timestamp
        """
        if frame is None:
            return None
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 0), 2)
        return frame
        
    def add_frame_counter(self, frame, counter):
        """
        Add frame counter to the frame.
        
        Args:
            frame: Input frame
            counter: Frame counter value
            
        Returns:
            frame: Frame with counter
        """
        if frame is None:
            return None
            
        cv2.putText(frame, f"Frame: {counter}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)
        return frame
        
    def draw_detection_box(self, frame, bbox, label, color=(0, 255, 0)):
        """
        Draw bounding box and label on the frame.
        
        Args:
            frame: Input frame
            bbox: Tuple of (x, y, w, h) for bounding box
            label: Label text to display
            color: BGR color tuple for box and text
            
        Returns:
            frame: Frame with detection box
        """
        if frame is None or bbox is None:
            return frame
            
        x, y, w, h = bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, 2)
        return frame
        
    def resize_frame(self, frame, width=None, height=None):
        """
        Resize frame while maintaining aspect ratio.
        
        Args:
            frame: Input frame
            width: Desired width (None to calculate from height)
            height: Desired height (None to calculate from width)
            
        Returns:
            resized_frame: Resized frame
        """
        if frame is None:
            return None
            
        if width is None and height is None:
            return frame
            
        h, w = frame.shape[:2]
        if width is None:
            aspect = width / float(w)
            dim = (int(w * aspect), height)
        else:
            aspect = height / float(h)
            dim = (width, int(h * aspect))
            
        return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA) 