import cv2
import os
import django
import sys

# Django setup
sys.path.append(r"C:\Users\reala\TrafficSight\traffic")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traffisight.settings')
django.setup()
import numpy as np
from speed_estimation.config import video_path, perspective_matrix

def get_pixel_distance(img, perspective_matrix):
    # Show the frame and let user click two points
    points = []
    # Resize the frame to 1000x1000 for easier clicking
    img = cv2.resize(img, (1000, 1000))
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Select 2 Points", img)

    cv2.imshow("Select 2 Points", img)
    cv2.setMouseCallback("Select 2 Points", click_event)

    print("Click two points in the window (e.g., lane markers, known distance).")
    while len(points) < 2:
        cv2.waitKey(1)
    cv2.destroyAllWindows()

    # Transform points using perspective matrix
    pts = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
    transformed_pts = cv2.perspectiveTransform(pts, perspective_matrix)
    p1, p2 = transformed_pts[0][0], transformed_pts[1][0]
    pixel_distance = np.linalg.norm(p2 - p1)
    print(f"Pixel distance (after perspective transform): {pixel_distance:.2f}")
    return pixel_distance

def save_pixel_to_meter_to_config(pixel_to_meter, config_path="speed_estimation/config.py"):
    pixel_to_meter_str = f"pixel_to_meter = {pixel_to_meter}\n"
    with open(config_path, "r") as f:
        lines = f.readlines()
    with open(config_path, "w") as f:
        replaced = False
        for line in lines:
            if line.strip().startswith("pixel_to_meter"):
                f.write(pixel_to_meter_str)
                replaced = True
            else:
                f.write(line)
        if not replaced:
            f.write(pixel_to_meter_str)

def main():
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read video frame.")
        return

    pixel_distance = get_pixel_distance(frame, perspective_matrix)
    real_distance = float(input("Enter the real-world distance between the points (meters): "))
    pixel_to_meter = real_distance / pixel_distance
    print(f"Estimated pixel_to_meter ratio: {pixel_to_meter:.6f}")
    print("Use this value in your speed calculation for better accuracy.")
    save_pixel_to_meter_to_config(pixel_to_meter)
    print("✅ pixel_to_meter saved to config.py")

main()