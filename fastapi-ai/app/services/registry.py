from app.services.frame_service import FrameManager

class FrameMangerRegistry:
    def __init__(self):
        self.managers = {}
    
    def add_camera(self,name,source):
        if name not in self.managers:
            self.managers[name] = FrameManager(source,name)
        return self.managers[name]
    
    def get_camera(self,name):
        return self.managers.get(name)
    
    def stop_all(self):
        for manager in self.managers.values():
            manager.stop()
        self.managers.clear()

registry = FrameMangerRegistry()
    