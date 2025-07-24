import numpy as np
import cv2
from speed_estimation.db.db import get_mac_address,get_speed_limit
vehicle_detection_model_path='models/Vehicle_Detector.pt'
license_detection_model_path='models/LP_Detector.pt'
PlateReaderModel='models/Character_Detection_model.pt'
speed_limit=get_speed_limit()   
# speed_limit=0
MAC_ADDRESS = get_mac_address()

video_path="Test_Videos/aakriti.mp4"

src_points = np.float32([(8, 153), (238, 114), (590, 180), (105, 356)])
dst_points = np.float32([[0, 0],[10, 0],[10, 30], [0, 30]])
pixel_to_meter = 1.1492493841110938
# Compute the matrix once
perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)