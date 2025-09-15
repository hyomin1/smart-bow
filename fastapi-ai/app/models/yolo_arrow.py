from ultralytics import YOLO
import torch

class ArrowModel:
    def __init__(self):
        self.model = YOLO("weights/arrow_best.pt")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
    
    def predict(self,frame):
        return self.model(frame,conf=0.36,verbose=False)[0]

    