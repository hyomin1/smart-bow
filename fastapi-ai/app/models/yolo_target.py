from ultralytics import YOLO


class TargetModel:
    def __init__(self):
        self.model = YOLO("weights/target_best.pt")

    def predict(self,frame):
        return self.model(frame, conf=0.8, verbose=False)[0]