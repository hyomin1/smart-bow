from ultralytics import YOLO
import torch
class ShooterModel:
    def __init__(self):
        self.model = YOLO("yolov8n-pose.pt")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print("사수 모델 gpu",self.device)
        self.model.to(self.device)
  
    
    def predict(self,frame):
        return self.model(frame, conf=0.5, verbose=False)[0]