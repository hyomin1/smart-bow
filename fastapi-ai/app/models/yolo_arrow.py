from ultralytics import YOLO
import torch
model = YOLO("models/arrow_best.pt")

def get_arrow_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(device)
    return model
