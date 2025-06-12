"""
Test script for speed estimation functionality.

To run this script:
1. Make sure you're in the root directory (where speed_estimation folder is located)
2. Run: python -m speed_estimation.test_speed_estimation
"""

import cv2
import os
import time
import numpy as np
from collections import defaultdict, deque

def test_speed_estimation():
    # Initialize video capture
    video_path = "Test_Videos/BalkumariPul.mp4"
    if not os.path.exists(video_path):
        print(f"Please place a test video at {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file")
        return

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print("Video properties:")
    print(f"- FPS: {fps}")
    print(f"- Resolution: {frame_width}x{frame_height}")
    print(f"- Total frames: {frame_count}")

    # Process video frames
    frame_idx = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Display frame
        cv2.imshow('Speed Estimation Test', frame)
        
        # Print processing stats every 30 frames
        frame_idx += 1
        if frame_idx % 30 == 0:
            elapsed_time = time.time() - start_time
            current_fps = frame_idx / elapsed_time
            print(f"Processing FPS: {current_fps:.2f}")

        # Break if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nProcessing complete:")
    print(f"- Processed {frame_idx} frames")

if __name__ == "__main__":
    test_speed_estimation() 