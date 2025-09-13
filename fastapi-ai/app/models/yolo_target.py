from ultralytics import YOLO
model = YOLO("models/target_best.pt")

def get_target_model():
    return model
