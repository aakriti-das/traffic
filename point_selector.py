import cv2
import os
import django
import sys
import ast

# Django setup
sys.path.append(r"C:\Users\reala\TrafficSight\traffic")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traffisight.settings')
django.setup()

from speed_estimation.config import video_path

points = []

def click_event(event, x, y, flags, param):
    global frame, points
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
        points.append((x, y))
        print(f"Point {len(points)}: ({x}, {y})")
        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
        redraw_frame()

        # Automatically quit when 4 points selected
        if len(points) == 4:
            cv2.destroyAllWindows()

def redraw_frame():
    """Redraw the frame with text and points."""
    display_frame = frame.copy()
    
    # Draw instruction text
    cv2.putText(display_frame,
                "Click 4 road points (clockwise/counter). Press 'q' to quit.",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2, cv2.LINE_AA)

    # Draw selected points
    for p in points:
        cv2.circle(display_frame, p, 5, (0, 255, 0), -1)

    # Resize for display (e.g., width=640, keep aspect ratio)
    display_width = 1000
    h, w = display_frame.shape[:2]
    scale = display_width / w
    display_resized = cv2.resize(display_frame, (display_width, int(h * scale)))

    cv2.imshow("Select 4 Points", display_resized)

# Load a frame from the video
cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
cap.release()

if not ret:
    print("❌ Failed to read video frame.")
    exit()

print("🖱 Click on 4 road points in order (clockwise or counter-clockwise). Press 'q' to quit.")
redraw_frame()

cv2.setMouseCallback("Select 4 Points", click_event)

while True:
    key = cv2.waitKey(0)
    if key == ord('q') or len(points) == 4:
        break

cv2.destroyAllWindows()

def save_src_points_to_config(src_points, config_path="speed_estimation/config.py"):
    # Format points for numpy
    src_points_str = f"src_points = np.float32({src_points})\n"
    # Read config.py
    with open(config_path, "r") as f:
        lines = f.readlines()
    # Replace or add src_points line
    with open(config_path, "w") as f:
        replaced = False
        for line in lines:
            if line.strip().startswith("src_points"):
                f.write(src_points_str)
                replaced = True
            else:
                f.write(line)
        if not replaced:
            f.write(src_points_str)

if len(points) == 4:
    print("\n✅ Selected src_points:")
    print("src_points =", points)
    save_src_points_to_config(points)
    print("✅ src_points saved to config.py")
else:
    print("⚠️ You didn't select 4 points.")
