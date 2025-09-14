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




# def get_target_info(frame, output_size=(800, 800)):
#     """
#     서버 내부용: src_pts, dst_pts, M 모두 반환
#     """
#     model = get_target_model()
#     results = model.predict(frame, verbose=False, conf=0.8)
#     r = results[0]

#     corners = []
#     if r.masks is not None:
#         for mask in r.masks.xy:
#             pts = np.array(mask, dtype=np.int32)
#             epsilon = 0.01 * cv2.arcLength(pts, True)
#             approx = cv2.approxPolyDP(pts, epsilon, True)
#             corners = approx.reshape(-1, 2).tolist()
#             break

#     if len(corners) == 4:
#         src_pts = order_points(corners)

#         w, h = output_size
#         dst_pts = np.array(
#             [[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype="float32"
#         )
#         M = cv2.getPerspectiveTransform(src_pts, dst_pts)

#         return {
#             "src_pts": src_pts,
#             "dst_pts": dst_pts,
#             "M": M,
#         }

#     return None


# def get_target_for_front(frame, output_size=(800, 800)):
#     """
#     프론트엔드용: dst_pts만 반환
#     """
#     info = get_target_info(frame, output_size)
#     if info is None:
#         return None
#     return info["dst_pts"].astype(int).tolist()
