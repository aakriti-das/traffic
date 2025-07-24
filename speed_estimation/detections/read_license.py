from ultralytics import YOLO
import os
import sys
sys.path.append(r"C:\Users\reala\TrafficSight\traffic")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traffisight.settings')
import django
django.setup()
import cv2
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torchvision import transforms
import pickle
from PIL import Image
from speed_estimation.config import PlateReaderModel
import os
import time
from sklearn.cluster import KMeans

# Create a directory for debug images
DEBUG_DIR = "debug_plates"
os.makedirs(DEBUG_DIR, exist_ok=True)

class_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'BA', 'BAGMATI', 'CHA', 'DHA', 'GA', 'GANDAKI', 'HA', 'JA', 
               'JHA', 'KA', 'KHA', 'KO', 'LU', 'LUMBINI', 'MA', 'MADESH', 'ME', 'NA', 'PA', 'PRA', 'PRADESH', 'RA', 'SU',
                 'VE', 'YA']

#Load your YOLO model
model = YOLO(PlateReaderModel)  # path to trained detector
# names = model.names  # class names
# print(f"Loaded model with classes: {names.values()}")

def preprocess_plate(image, target_size=640):
    # Ensure grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    # Resize with padding (fit)
    h, w = gray.shape[:2]
    scale = target_size / max(h, w)
    resized = cv2.resize(gray, (int(w * scale), int(h * scale)))
    pad_h = target_size - resized.shape[0]
    pad_w = target_size - resized.shape[1]
    top = pad_h // 2
    bottom = pad_h - top
    left = pad_w // 2
    right = pad_w - left
    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=0)
    return padded
def group_and_sort_chars(char_data):
    # char_data: list of dicts with "center_y" and "center_x"
    if not char_data:
        return [], []
    # Compute median y to split rows
    y_centers = [c["center_y"] for c in char_data]
    median_y = np.median(y_centers)
    top_row = [c for c in char_data if c["center_y"] < median_y]
    bottom_row = [c for c in char_data if c["center_y"] >= median_y]
    # Sort each row by x
    top_sorted = sorted(top_row, key=lambda c: c["center_x"])
    bottom_sorted = sorted(bottom_row, key=lambda c: c["center_x"])
    return top_sorted, bottom_sorted
# def group_and_sort_chars_by_top(char_data):
#     # char_data: list of dicts with "bbox" key
#     if not char_data:
#         return [], []
#     y1s = [c["bbox"][1] for c in char_data]  # y1 is the top of the box
#     median_y1 = np.median(y1s)
#     top_row = [c for c in char_data if c["bbox"][1] < median_y1]
#     bottom_row = [c for c in char_data if c["bbox"][1] >= median_y1]
#     # Sort each row by x (left to right)
#     top_sorted = sorted(top_row, key=lambda c: c["bbox"][0])
#     bottom_sorted = sorted(bottom_row, key=lambda c: c["bbox"][0])
#     return top_sorted, bottom_sorted

def is_single_line(char_data, y_thresh=30):
    y1s = [c["bbox"][1] for c in char_data]
    return max(y1s) - min(y1s) < y_thresh

def read_license_plate(image_input, conf_thres=0.2):
    # Accept both file path and numpy array
    if isinstance(image_input, str):
        image = cv2.imread(image_input)
        if image is None:
            raise ValueError(f"Could not read image from path: {image_input}")
    elif isinstance(image_input, np.ndarray):
        image = image_input
    else:
        raise TypeError("Input must be a file path or numpy array.")

    img = preprocess_plate(image)  # Always grayscale, 640x640, padded
    img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # YOLO expects 3 channels

    results = model.predict(source=img_bgr, conf=conf_thres, save=False)
    boxes = results[0].boxes
    if len(boxes) < 4:
        print("Not Valid License plate.")
        return ""
    char_data = []
    if not boxes:
        print("No characters detected.")
        return ""
    for box, conf, cls_id in zip(boxes.xyxy.cpu().numpy(), boxes.conf.cpu().numpy(), boxes.cls.cpu().numpy()):
        x1, y1, x2, y2 = map(int, box)
        char_data.append({
            "cls_id": int(cls_id),
            "bbox": (x1, y1, x2, y2),
            "center_x": (x1 + x2) / 2,
            "center_y": (y1 + y2) / 2,
            "confidence": conf
        })

    if not char_data:
        return ""

    # Single-line plate handling 
    if is_single_line(char_data):
        sorted_chars = sorted(char_data, key=lambda c: c["bbox"][0])
        full_text = "".join([class_names[c["cls_id"]] for c in sorted_chars])
        # Visualization (optional)
        vis_img = img_bgr.copy()
        for char in sorted_chars:
            x1, y1, x2, y2 = char["bbox"]
            label = class_names[char["cls_id"]]
            confidence = char["confidence"]
            cv2.rectangle(vis_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label_text = f"{label} ({confidence:.2f})"
            cv2.putText(vis_img, label_text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        debug_image_path = os.path.join(DEBUG_DIR, f"plate_{timestamp}_{full_text}.jpg")
        cv2.imwrite(debug_image_path, vis_img)
        print(f"Debug image saved to: {debug_image_path}")
        print("Full plate text:", full_text)
        return full_text

    # Multi-line plate handling 
    top_sorted, bottom_sorted = group_chars_by_kmeans(char_data, n_rows=2)
    top_sorted, bottom_sorted = enforce_plate_format(top_sorted, bottom_sorted, class_names)

    # Build strings from detected characters
    top_text_raw = "".join([class_names[c["cls_id"]] for c in top_sorted])
    bottom_text_raw = "".join([class_names[c["cls_id"]] for c in bottom_sorted])

    full_text = top_text_raw + bottom_text_raw

    # Visualization (optional)
    vis_img = img_bgr.copy()
    for char in top_sorted + bottom_sorted:
        x1, y1, x2, y2 = char["bbox"]
        label = class_names[char["cls_id"]]
        confidence = char["confidence"]
        cv2.rectangle(vis_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label_text = f"{label} ({confidence:.2f})"
        cv2.putText(vis_img, label_text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    debug_image_path = os.path.join(DEBUG_DIR, f"plate_{timestamp}_{full_text}.jpg")
    cv2.imwrite(debug_image_path, vis_img)
    print(f"Debug image saved to: {debug_image_path}")
    print("Top row:", [class_names[c["cls_id"]] for c in top_sorted])
    print("Bottom row:", [class_names[c["cls_id"]] for c in bottom_sorted])
    print("Full plate text:", full_text)
    return full_text

def enforce_plate_format(top_sorted, bottom_sorted, class_names):
    zone_codes = {"BA", "GA", "NA", "MA", "LU", "JA", "KO", "ME", "DHA", "SA","PRADESH", "BAGMATI", "LUMBINI", "GANDAKI", "MADESH", "SU"}
    category_codes={"PA","RA", "VE", "HA", "KA", "KHA", "JA", "JHA", "YA","CHA","MA"}
    # Helper to get label from char dict
    def get_label(char):
        return class_names[char["cls_id"]]

    # --- Move first digit from top to bottom row ---
    if top_sorted and get_label(top_sorted[0]).isdigit():
        bottom_sorted = [top_sorted[0]] + bottom_sorted
        top_sorted = top_sorted[1:]

    # --- Zone code logic ---
    if top_sorted:
        first_label = get_label(top_sorted[0])
        last_label = get_label(top_sorted[-1])
        # If first char is not digit
        if not first_label.isdigit():
            # If not a zone code, remove it
            if first_label not in zone_codes:
                top_sorted = top_sorted[1:]
            # If it is a zone code, check 2nd char
            elif len(top_sorted) > 1:
                second_label = get_label(top_sorted[1])
                if not second_label.isdigit() and second_label not in ["PRADESH","PRA"]:
                    top_sorted = [top_sorted[0]] + top_sorted[2:]  # Remove 2nd char
                if last_label in category_codes and len(top_sorted) > 4:
                    #Remove 2nd last char 
                    top_sorted = top_sorted[:-2] + top_sorted[-1:]  # Keep last char                    
    # If bottom row is now 5, remove the last char
    if len(bottom_sorted) == 5:
        bottom_sorted = bottom_sorted[:-1]

    return top_sorted, bottom_sorted

def group_chars_by_kmeans(char_data, n_rows=2):
    if not char_data:
        return [], []
    y_coords = np.array([c["center_y"] for c in char_data]).reshape(-1, 1)
    kmeans = KMeans(n_clusters=n_rows, random_state=0).fit(y_coords)
    labels = kmeans.labels_
    rows = [[] for _ in range(n_rows)]
    for idx, label in enumerate(labels):
        rows[label].append(char_data[idx])
    # Sort each row by x (left to right)
    sorted_rows = [sorted(row, key=lambda c: c["center_x"]) for row in rows]
    # Ensure top row is above bottom row
    if np.mean([c["center_y"] for c in sorted_rows[0]]) > np.mean([c["center_y"] for c in sorted_rows[1]]):
        sorted_rows = sorted_rows[::-1]
    return sorted_rows[0], sorted_rows[1]

# read_license_plate("test_images/licenseplate_20250722_164043.jpg")