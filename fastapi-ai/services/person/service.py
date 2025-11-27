import time


class PersonService:

    def __init__(self, timeout=3.0):
        self.zoom_box = None
        self.zoom_timestamp = None
        self.timeout = timeout

    def set_zoom_area(self, bbox):
        self.zoom_box = bbox
        self.zoom_timestamp = time.time()

    def get_zoom_area(self):
        if self.zoom_box is None or self.zoom_timestamp is None:
            return None

        if time.time() - self.zoom_timestamp > self.timeout:
            self.clear_zoom()
            return None

        return self.zoom_box

    def is_zooming(self):
        return self.get_zoom_area() is not None

    def clear_zoom(self):
        self.zoom_box = None
        self.zoom_timestamp = None
