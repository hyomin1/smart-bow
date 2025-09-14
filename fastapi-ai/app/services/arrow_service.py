# import cv2
# import numpy as np
# import time
# from app.models.yolo_arrow import get_arrow_model

# class ArrowService:
#     def __init__(self, cooldown_sec: float = 3.0):
#         self.model = get_arrow_model()
#         self.cooldown_sec = cooldown_sec
#         self.last_hit_time = 0
        

#     def leading_tip_from_bbox(self, xyxy, H):
#         """bbox corner 중 아래쪽을 tip으로 선택"""
#         x1, y1, x2, y2 = xyxy
#         corners = np.array([[x1,y1],[x2,y1],[x1,y2],[x2,y2]], dtype=np.float32)
#         d_bottom = H - corners[:,1]
#         tip = corners[np.argmin(d_bottom)]
#         return tip

#     def detect(self, frame, target_info: dict):
#         """
#         화살 검출 + 보정 + 명중 판정
#         target_info = { "src_pts":, "dst_pts":, "M": }
#         """
#         if target_info is None:
#             return {"type": "error", "reason": "no_target"}

#         H, W = frame.shape[:2]
#         results = self.model(frame, conf=0.36, verbose=False)[0]

#         if results.boxes is None or len(results.boxes) == 0:
#             return {"type": "arrow", "tip": None, "corrected_tip": None}

#         xyxy = results.boxes.xyxy[0].cpu().numpy()
#         tip = self.leading_tip_from_bbox(xyxy, H)

        
#         corrected_tip = tip

#         # 과녁 안에 들어왔는지
#         inside = cv2.pointPolygonTest(
#              np.array(target_info, dtype=np.int32),
#             (float(corrected_tip[0]), float(corrected_tip[1])),
#             False
#         ) >= 0
   

#         # 기본 arrow 이벤트
#         event = {
#             "type": "arrow",
#             "tip": [float(tip[0]), float(tip[1])],
#             "corrected_tip": [float(corrected_tip[0]), float(corrected_tip[1])]
#         }

#         # 명중 이벤트
#         now = time.time()
#         if inside and (now - self.last_hit_time) >= self.cooldown_sec:
#             self.last_hit_time = now
#             event["type"] = "hit"

#         return event
