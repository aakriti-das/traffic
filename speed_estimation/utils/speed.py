# utils/speed.py

from collections import deque
import numpy as np

def calculate_speed(coordinates: deque, fps: int, pixel_to_meter: float = 0.01) -> float:
    if len(coordinates) < 2:
        return 0.0
    distance = abs(coordinates[-1] - coordinates[0])
    time = (len(coordinates) - 1) / fps
    if time == 0:
        return 0.0
    speed_mps = (distance * pixel_to_meter) / time
    speed_kmh = speed_mps * 3.6
    print(f"DEBUG: distance={distance}, time={time}, speed_kmh={speed_kmh}")
    return speed_kmh
