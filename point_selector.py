import cv2
from speed_estimation.config import video_path

points = []

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
        points.append((x, y))
        print(f"Point {len(points)}: ({x}, {y})")
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Select 4 Points", frame)

# Load a frame from the video
cap = cv2.VideoCapture(video_path)

ret, frame = cap.read()
cap.release()

if not ret:
    print("❌ Failed to read video frame.")
    exit()

cv2.imshow("Select 4 Points", frame)
cv2.setMouseCallback("Select 4 Points", click_event)

print("🖱 Click on 4 road points in order (clockwise or counter-clockwise). Press 'q' to quit.")

while True:
    key = cv2.waitKey(0)
    if key == ord('q') or len(points) == 4:
        break

cv2.destroyAllWindows()

if len(points) == 4:
    print("\n✅ Selected src_points:")
    print("src_points =", points)
else:
    print("⚠️ You didn't select 4 points.")
