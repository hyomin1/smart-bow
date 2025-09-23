from app.services.arrow_service import ArrowService

class ArrowServiceRegistry:
    def __init__(self):
        self.services = {}

    def get(self, cam_id: str) -> ArrowService:
        if cam_id not in self.services:
            self.services[cam_id] = ArrowService()
        return self.services[cam_id]

    def remove(self, cam_id: str):
        if cam_id in self.services:
            del self.services[cam_id]

arrow_registry = ArrowServiceRegistry()
