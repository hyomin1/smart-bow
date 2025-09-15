import cv2
import numpy as np
from app.models.yolo_target import TargetModel
class TargetService:
    def __init__(self,cam_key):
        self.model = TargetModel()
        self.cam_key = cam_key

    def get_frame(self):
        cap = cv2.VideoCapture(self.cam_key)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return None
        return frame
    
    def order_points(self,pts):
        pts = np.array(pts)
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)

        top_left = pts[np.argmin(s)]
        bottom_right = pts[np.argmax(s)]
        top_right = pts[np.argmin(diff)]
        bottom_left = pts[np.argmax(diff)]

        return np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")

    def get_target_raw(self,frame):
        """보정 없는 버전: 과녁 원본 좌표(src_pts)만 반환"""
        result = self.model.predict(frame)
        corners = []
        if result.masks is not None:
            for mask in result.masks.xy:
                pts = np.array(mask, dtype=np.int32)
                epsilon = 0.04 * cv2.arcLength(pts, True)
                approx = cv2.approxPolyDP(pts, epsilon, True)
                corners = approx.reshape(-1, 2).tolist()
                break
        if len(corners) == 4:
            src_pts = self.order_points(corners)
            return src_pts.tolist()      
        return None 



