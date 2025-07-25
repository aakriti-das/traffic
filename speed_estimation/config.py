import numpy as np
import cv2
from speed_estimation.db.db import get_mac_address
vehicle_detection_model_path='models/Vehicle_Detector.pt'
license_detection_model_path='models/LP_Detector.pt'
PlateReaderModel='models/Character_Detection_model.pt'
MAC_ADDRESS = get_mac_address()

video_path="Test_Videos/aakriti.mp4"

src_points = np.float32([(2, 165), (267, 139), (899, 283), (212, 541)])
dst_points = np.float32([[0, 0],[10, 0],[10, 30], [0, 30]])
pixel_to_meter = 1.0368540119222602
# Compute the matrix once
perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)