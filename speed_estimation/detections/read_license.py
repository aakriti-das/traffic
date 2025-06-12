from ultralytics import YOLO
import cv2
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torchvision import transforms
import pickle
from PIL import Image

#Load your YOLO model
model = YOLO("models/licensePlatesegmentation.pt")  # path to trained detector

# Load classifier and class mapping (do this once)
class CharClassifier(nn.Module):
    def __init__(self, num_classes):
        super(CharClassifier, self).__init__()
        self.model = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.model(x)


def read_license_plate(image_input):
    print("Inside read_license_plate function")
    # Accept both file path and numpy array
    if isinstance(image_input, str):
        image = cv2.imread(image_input)
        if image is None:
            raise ValueError(f"Could not read image from path: {image_input}")
    elif isinstance(image_input, np.ndarray):
        image = image_input
    else:
        raise TypeError("Input must be a file path or numpy array.")

    # Convert to RGB for further processing
    if image.ndim == 2:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 3:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        raise ValueError("Unsupported image array shape for license plate input.")
    #Run detection
    results = model.predict(source=image, conf=0.3, iou=0.4)[0]  # returns one result

    # Get bounding boxes (x1, y1, x2, y2)
    boxes = results.boxes.xyxy.cpu().numpy()  # shape: (N, 4)
    # print("boxes:",boxes)
    # Sort boxes by x1 (left to right)
    sorted_boxes = sorted(boxes, key=lambda b: (b[1], b[0]))   
    # print("Sorted Boxes:",sorted_boxes)

    with open("models/class_mapping.pkl", "rb") as f:
        class_names = pickle.load(f)

    classifier = CharClassifier(num_classes=len(class_names))
    classifier.load_state_dict(torch.load("models/char_classifier1.pth", map_location=torch.device("cpu")))
    classifier.eval()

    transform = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    ])

    # Crop and Classify Each Detected Character
    char_crops = []
    predicted_chars = []
    for box in sorted_boxes:
        x1, y1, x2, y2 = map(int, box)
        crop = rgb_image[y1:y2, x1:x2]
        # cv2.imshow("Character Crop", crop)  # Display each crop for debugging
        # cv2.waitKey(1000)  
        char_crops.append(crop)

        # Convert OpenCV image (numpy array) to PIL Image for transform
        pil_crop = Image.fromarray(crop)

        # Apply classifier
        input_tensor = transform(pil_crop).unsqueeze(0)  # (1, 1, 28, 28)
        with torch.no_grad():
            outputs = classifier(input_tensor)
            predicted_index = outputs.argmax(dim=1).item()
            predicted_class = class_names[predicted_index]
            print(f"Predicted class: {predicted_class}")
        predicted_chars.append(predicted_class)
    license_text = ''.join(predicted_chars)
    print(f"Detected license text: {license_text}")
    return license_text

