from ultralytics import YOLO
import torch
class PersonModel:
    def __init__(self):
        self.model = YOLO("/weights/yolov8n.pt")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print("사람모델 gpu",self.device)
        self.model.to(self.device)

    def predict(self, frame):
        
        return self.model(frame,conf=0.5, verbose=False, classes=[0])[0]