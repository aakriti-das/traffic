import numpy as np
import cv2
from speed_estimation.db.db import get_mac_address,get_speed_limit
vehicle_detection_model_path='models/Vehicle_Detector.pt'
license_detection_model_path='models/LP_Detector.pt'
PlateReaderModel='models/PlateReaderModel.pt'
license_plate_segmentation_model_path='models/license_plate_segmentation_model.pt'
classifier_model_path='models/classifier_model.pth'
# speed_limit=get_speed_limit()   
speed_limit=5
# Common vehicle class names in COCO
VEHICLE_CLASSES = ['vehicle','car', 'truck', 'bus', 'motorbike', 'motorcycle']
MAC_ADDRESS = get_mac_address()

video_path="Test_Videos/aakriti.mp4"

# src_points = np.float32([
#     [610, 175],   # top-left
#     [945, 165],   # top-right
#     [1320, 700],  # bottom-right
#     [230, 610]    # bottom-left
# ])

src_points = np.float32([[(46, 489), (464, 494), (1383, 714), (20, 778)]])
dst_points = np.float32([
    [0, 0],
    [10, 0],
    [10, 30],
    [0, 30]
])

# Compute the matrix once
perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)