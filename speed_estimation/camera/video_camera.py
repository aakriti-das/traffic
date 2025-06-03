import cv2
import numpy as np
from datetime import datetime
import os

class VideoCamera:
    def __init__(self, source=0):
        """
        Initialize the VideoCamera instance.
        
        Args:
            source: Can be camera index (0, 1, etc.) or video file path
        """
        self.source = source
        self.cap = None
        self.frame_count = 0
        self.fps = 0
        self.frame_width = 0
        self.frame_height = 0
        self.is_running = False
        
    def start(self):
        """Start the video capture."""
        if self.is_running:
            return False
            
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video source: {self.source}")
            
        # Get video properties
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.is_running = True
        return True
        
    def stop(self):
        """Stop the video capture."""
        if self.cap and self.is_running:
            self.cap.release()
            self.is_running = False
            self.frame_count = 0
            
    def get_frame(self):
        """
        Get the next frame from the video source.
        
        Returns:
            tuple: (success, frame, frame_number)
        """
        if not self.is_running:
            return False, None, self.frame_count
            
        success, frame = self.cap.read()
        if success:
            self.frame_count += 1
        return success, frame, self.frame_count
        
    def get_video_info(self):
        """
        Get information about the video source.
        
        Returns:
            dict: Video properties including fps, dimensions, and frame count
        """
        return {
            'fps': self.fps,
            'width': self.frame_width,
            'height': self.frame_height,
            'frame_count': self.frame_count,
            'is_running': self.is_running
        }
        
    def save_frame(self, frame, output_dir='captured_frames'):
        """
        Save a frame to disk.
        
        Args:
            frame: The frame to save
            output_dir: Directory to save the frame
        
        Returns:
            str: Path to the saved frame
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'frame_{timestamp}.jpg'
        filepath = os.path.join(output_dir, filename)
        
        cv2.imwrite(filepath, frame)
        return filepath
        
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        
    def __del__(self):
        """Destructor to ensure camera release."""
        self.stop()
