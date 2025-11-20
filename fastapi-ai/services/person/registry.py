from .service import PersonService


class PersonRegistry:
    def __init__(self):
        self.services = {}

    def get(self, cam_id: str):
        if cam_id not in self.services:
            self.services[cam_id] = PersonService()
        return self.services[cam_id]

    def remove(self, cam_id: str):
        if cam_id in self.services:
            del self.services[cam_id]

    def clear_all(self):
        self.services.clear()

    def items(self):
        return self.services.items()


person_registry = PersonRegistry()
