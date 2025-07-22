from ultralytics import YOLO
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

# Create a directory for debug images
DEBUG_DIR = "debug_plates"
os.makedirs(DEBUG_DIR, exist_ok=True)

class_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
               'BA', 'BAGMATI', 'CHA', 'Char', 'GA', 'GANDAKI', 'HA', 'JA', 'JHA', 'KA',
               'KHA', 'KO', 'LU', 'LUMBINI', 'MA', 'MADESH', 'ME', 'NA', 'PA', 'PRA',
               'PRADESH', 'RA', 'SU', 'VE', 'YA', 'de', 'dha', 'gha', 'sha', 'tin']

#Load your YOLO model
model = YOLO(PlateReaderModel)  # path to trained detector

# Load classifier and class mapping (do this once)
# class CharClassifier(nn.Module):
#     def __init__(self, num_classes):
#         super(CharClassifier, self).__init__()
#         self.model = nn.Sequential(
#             nn.Conv2d(1, 32, 3, padding=1),
#             nn.ReLU(),
#             nn.MaxPool2d(2),
#             nn.Conv2d(32, 64, 3, padding=1),
#             nn.ReLU(),
#             nn.MaxPool2d(2),
#             nn.Flatten(),
#             nn.Linear(64 * 7 * 7, 128),
#             nn.ReLU(),
#             nn.Linear(128, num_classes)
#         )

#     def forward(self, x):
#         return self.model(x)

# def read_license_plate(image_input):
#     print("Inside read_license_plate function")
#     # Accept both file path and numpy array
#     if isinstance(image_input, str):
#         image = cv2.imread(image_input)
#         if image is None:
#             raise ValueError(f"Could not read image from path: {image_input}")
#     elif isinstance(image_input, np.ndarray):
#         image = image_input
#     else:
#         raise TypeError("Input must be a file path or numpy array.")
#     # image=preprocess_plate(image)
#     # Convert to RGB for further processing
#     if image.ndim == 2:
#         rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
#     elif image.shape[2] == 3:
#         rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     else:
#         raise ValueError("Unsupported image array shape for license plate input.")
#     #Run detection
#     results = model.predict(source=image, conf=0.3, iou=0.4)[0]  # returns one result

#     # Get bounding boxes (x1, y1, x2, y2)
#     boxes = results.boxes.xyxy.cpu().numpy()  # shape: (N, 4)
#     # print("boxes:",boxes)
#     # Sort boxes by x1 (left to right)
#     sorted_boxes = sorted(boxes, key=lambda b: (b[1], b[0]))   
#     # print("Sorted Boxes:",sorted_boxes)

#     with open("models/class_mapping.pkl", "rb") as f:
#         class_names = pickle.load(f)

#     classifier = CharClassifier(num_classes=len(class_names))
#     classifier.load_state_dict(torch.load("models/char_classifier1.pth", map_location=torch.device("cpu")))
#     classifier.eval()

#     transform = transforms.Compose([
#     transforms.Grayscale(),
#     transforms.Resize((28, 28)),
#     transforms.ToTensor(),
#     ])

#     # Crop and Classify Each Detected Character
#     char_crops = []
#     predicted_chars = []
#     for box in sorted_boxes:
#         x1, y1, x2, y2 = map(int, box)
#         crop = rgb_image[y1:y2, x1:x2]
#         # cv2.imshow("Char",crop)
#         # cv2.waitKey(1000)
#         char_crops.append(crop)

#         # Convert OpenCV image (numpy array) to PIL Image for transform
#         if crop.shape[0] == 0 or crop.shape[1] == 0:
#             print(f"Skipping empty crop with shape: {crop.shape}")
#             continue

#         try:
#             pil_crop = Image.fromarray(crop)
#         except Exception as e:
#             print(f"Failed to convert crop to PIL image: {e}")
#             continue

#         # Apply classifier
#         input_tensor = transform(pil_crop).unsqueeze(0)  # (1, 1, 28, 28)
#         with torch.no_grad():
#             outputs = classifier(input_tensor)
#             predicted_index = outputs.argmax(dim=1).item()
#             predicted_class = class_names[predicted_index]
#             print(f"Predicted class: {predicted_class}")
#         predicted_chars.append(predicted_class)
#     license_text = ''.join(predicted_chars)
#     print(f"Detected license text: {license_text}")
#     return license_text

def preprocess_plate(image_path, target_size=640):
    # img = cv2.imread(image_path)
    if image_path is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    gray = cv2.cvtColor(image_path, cv2.COLOR_BGR2GRAY)
    img_eq = cv2.equalizeHist(gray)
    img_filtered = cv2.bilateralFilter(img_eq, 11, 17, 17)
    img_final = cv2.cvtColor(img_filtered, cv2.COLOR_GRAY2BGR)
    img_final = cv2.resize(img_final, (target_size, target_size))

    return img_final

def group_and_sort_chars(char_data):
    y_centers = [char["center_y"] for char in char_data]
    median_y = np.median(y_centers)

    top_line = []
    bottom_line = []

    for char in char_data:
        if char["center_y"] < median_y:
            top_line.append(char)
        else:
            bottom_line.append(char)

    # Sort each line left-to-right
    top_sorted = sorted(top_line, key=lambda x: x["center_x"])
    bottom_sorted = sorted(bottom_line, key=lambda x: x["center_x"])

    return top_sorted, bottom_sorted

def correct_plate_sequence(text: str) -> str:
    # Rule 1: Fix repeated province names, a common OCR error.
    text = text.replace("PRADESHPRADESH", "PRADESH")
    text = text.replace("BAGMATIBAGMATI", "BAGMATI")
    
    # Add more rules here as you identify other common errors
    # For example, correcting "O" to "0" or "I" to "1" if needed.
    
    return text

def read_license_plate(image_path, conf_thres=0.3):
    img = preprocess_plate(image_path)
    
    results = model.predict(source=img, conf=conf_thres, save=False)
    boxes = results[0].boxes

    char_data = []
    if not boxes:
        print("No characters detected.")
        return ""
    for box, conf, cls_id in zip(boxes.xyxy.cpu().numpy(), boxes.conf.cpu().numpy(), boxes.cls.cpu().numpy()):
        x1, y1, x2, y2 = box
        char_data.append({
            "cls_id": int(cls_id),
            "bbox": box,
            "center_x": (x1 + x2) / 2,
            "center_y": (y1 + y2) / 2,
            "confidence": conf
        })

    if not char_data:
        return "" # No characters detected

    # Group and sort characters
    top_sorted, bottom_sorted = group_and_sort_chars(char_data)

    # Build strings from detected characters
    top_text_raw = "".join([class_names[c["cls_id"]] for c in top_sorted])
    bottom_text_raw = "".join([class_names[c["cls_id"]] for c in bottom_sorted])

    # Apply sequence correction rules
    top_text_corrected = correct_plate_sequence(top_text_raw)
    bottom_text_corrected = correct_plate_sequence(bottom_text_raw)
    
    full_text = top_text_corrected + bottom_text_corrected
    
    vis_img = img.copy()
    all_chars_sorted = top_sorted + bottom_sorted
    
    for char in all_chars_sorted:
        x1, y1, x2, y2 = map(int, char["bbox"])
        label = class_names[char["cls_id"]]
        confidence = char["confidence"]
        
        # Log each character's details
        print(f"  - Char: {label}, Conf: {confidence:.2f}, Pos: ({x1},{y1})")
        
        # Draw box, label, and confidence on the debug image
        cv2.rectangle(vis_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label_text = f"{label} ({confidence:.2f})"
        cv2.putText(vis_img, label_text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Save the visualized image for review
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    debug_image_path = os.path.join(DEBUG_DIR, f"plate_{timestamp}_{full_text}.jpg")
    cv2.imwrite(debug_image_path, vis_img)
    print(f"Debug image saved to: {debug_image_path}")

    return full_text

# read_license_plate("Detected_licenseplates/LicensePlate_20250629_134458.jpg")