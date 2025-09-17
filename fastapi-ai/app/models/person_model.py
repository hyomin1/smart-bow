from ultralytics import YOLO

class PersonModel:
    def __init__(self):
        self.model = YOLO("/weights/yolov8n.pt")

    def predict(self, frame):
        return self.model(frame,conf=0.5, verbose=False, classes=[0])[0]