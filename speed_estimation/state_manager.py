from collections import deque
from typing import Dict, List
import threading

class VehicleStateManager:
    def __init__(self):
        self.vehicle_positions: Dict[int, deque] = {}
        self.current_vehicles: Dict[int, dict] = {}
        self.lock = threading.Lock()
    
    def update_vehicle_position(self, tracker_id: int, position: tuple, speed: float, confidence: float = None):
        """Update vehicle position and speed data"""
        with self.lock:
            if tracker_id not in self.vehicle_positions:
                self.vehicle_positions[tracker_id] = deque(maxlen=10)
            
            self.vehicle_positions[tracker_id].append(position)
            
            self.current_vehicles[tracker_id] = {
                'speed': speed,
                'confidence': confidence,
                'position': position,
                'last_update': self._get_current_time()
            }
    
    def get_current_stats(self) -> dict:
        """Get current vehicle count and max speed"""
        with self.lock:
            # Clean up old vehicles (not seen for more than 5 seconds)
            current_time = self._get_current_time()
            active_vehicles = {
                vid: data for vid, data in self.current_vehicles.items()
                if current_time - data['last_update'] < 5.0
            }
            
            vehicle_count = len(active_vehicles)
            
            # Get max speed from active vehicles
            speeds = [data['speed'] for data in active_vehicles.values() if data['speed'] > 0]
            current_speed = max(speeds) if speeds else 0
            
            return {
                'vehicle_count': vehicle_count,
                'current_speed': round(current_speed, 1),
                'active_vehicles': len(active_vehicles)
            }
    
    def _get_current_time(self) -> float:
        """Get current time in seconds"""
        import time
        return time.time()

# Global instance
vehicle_state = VehicleStateManager()
