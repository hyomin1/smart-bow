import cv2
import torch
from torch.amp import autocast
from app.models.shooter_model import ShooterModel

class ShooterService:
    def __init__(self):
        self.model = ShooterModel()
        self.last_frame = None  

    def detect(self, frame):
        self.last_frame = frame
        # h, w = frame.shape[:2]
        # infer_w, infer_h = 640, 360
        # resized = cv2.resize(frame, (infer_w, infer_h))

        # # GPU mixed precision context
        # if self.model.device == "cuda":
        #     with autocast("cuda"):
        #         results = self.model.predict(frame)
        # else:
        #     results = self.model.predict(frame)

        # pose_frame = results.plot()
        # self.last_frame = pose_frame
