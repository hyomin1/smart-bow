from app.services.shooter_service import ShooterService

class ShooterServiceRegistry:
    
    def __init__(self):
        self.services = {}

    def get(self, cam_id: str) -> ShooterService:
        if cam_id not in self.services:
            self.services[cam_id] = ShooterService()
        return self.services[cam_id]

    def remove(self, cam_id: str):
        if cam_id in self.services:
            del self.services[cam_id]

shooter_registry = ShooterServiceRegistry()
