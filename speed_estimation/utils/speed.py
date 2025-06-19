# utils/speed.py

from collections import deque
import numpy as np

def calculate_speed(coordinates: deque, fps: int, pixel_to_meter: float = 0.01) -> float:
    if len(coordinates) < 2:
        return 0.0
    start = coordinates[0]
    end = coordinates[-1]
    distance = np.linalg.norm(np.array(end) - np.array(start))
    time = (len(coordinates) - 1) / fps
    if time == 0:
        return 0.0
    speed_mps = (distance) / time
    speed_kmh = speed_mps * 3.6
    print(f"DEBUG: distance={distance}, time={time}, speed_kmh={speed_kmh}")
    return speed_kmh
