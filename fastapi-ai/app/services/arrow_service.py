import cv2
import numpy as np
import time
from collections import deque
from app.models.yolo_arrow import ArrowModel 
from app.services.target_service import TargetService   


class ArrowService:
    def __init__(self, buffer_size=7):
        self.model = ArrowModel()
        self.tracking_buffer = deque(maxlen=buffer_size)
        self.buffer_size = buffer_size

        self.target_service = TargetService()
        self.target_polygon = None   

    def update_target_polygon(self, frame):
        """필요할 때만 과녁 polygon 갱신"""
        target_pts = self.target_service.get_target_raw(frame)
        if target_pts is not None:
            self.target_polygon = np.array(target_pts, dtype=np.float32)

    # def leading_tip_from_bbox(self, xyxy, H):
    #     """bbox corner 중 아래쪽을 tip으로 선택"""
    #     x1, y1, x2, y2 = xyxy
    #     corners = np.array(
    #         [[x1, y1], [x2, y1], [x1, y2], [x2, y2]],
    #         dtype=np.float32
    #     )
    #     d_bottom = H - corners[:, 1]
    #     tip = corners[np.argmin(d_bottom)]
    #     return tip
    def leading_tip_from_bbox(self, xyxy, H):
        """bbox 밑변의 우측 끝을 tip으로 선택"""
        x1, y1, x2, y2 = map(int, xyxy)
        tip = np.array([x2, y2], dtype=np.float32)
        return tip

    def detect(self, frame, with_hit=True):
        """화살 검출 + 보정 + 명중 판정"""
        # 1. polygon 없으면 갱신
        if self.target_polygon is None:
            self.update_target_polygon(frame)
            if self.target_polygon is None:
                return {"type": "error", "reason": "no_target"}

        H, W = frame.shape[:2]
        results = self.model.predict(frame)
        now = time.time()

        event = {"type": "arrow", "tip": None, "bbox": None}

        #TODO: 욜로 기본 모델에서 person 클래스로 사람 검출되면 그냥 return

       
        if results.boxes is not None and len(results.boxes) > 0:
            xyxy = results.boxes.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, xyxy)
            tip = self.leading_tip_from_bbox(xyxy, H)

            # polygon 내부 여부 확인
            inside = cv2.pointPolygonTest(
                self.target_polygon.astype(np.int32),
                (float(tip[0]), float(tip[1])),
                False,
            ) >= 0

            if inside:
                self.tracking_buffer.append((tip[0], tip[1], now))

            event = {
                "type": "arrow",
                "tip": [float(tip[0]), float(tip[1])],
                "bbox": [x1, y1, x2, y2]
            }

            # 스트리밍 모드  끝
            if not with_hit:
                return event

        # hit 판정
        if (
            len(self.tracking_buffer) >= self.buffer_size
            or (0 < len(self.tracking_buffer) < self.buffer_size
                and now - self.tracking_buffer[-1][2] > 0.5)
        ):
            inside_points = [
                (x, y) for x, y, _ in self.tracking_buffer
                if cv2.pointPolygonTest(self.target_polygon, (x, y), False) >= 0
            ]
            #TODO: 속도 기반해서 그냥 바닥에 꽂히는 경우도 체크
            # if inside_points: and self.is_valid_hit():
            if inside_points:
                hit_tip = max(inside_points, key=lambda p: p[1])  # y 가장 큰 값
                event["type"] = "hit"
                event["hit_tip"] = [float(hit_tip[0]), float(hit_tip[1])]
            self.tracking_buffer.clear()

        return event


# def is_valid_hit(self):
#     if len(self.tracking_buffer) < 3:
#         return False
    
#     speeds = []
#     for i in range(1, len(self.tracking_buffer)):
#         x1, y1, t1 = self.tracking_buffer[i-1]
#         x2, y2, t2 = self.tracking_buffer[i]
#         dt = max(t2 - t1, 1e-3)
#         v = np.linalg.norm([x2 - x1, y2 - y1]) / dt
#         speeds.append(v)

#     
#     if not speeds:
#         return False

#     
#     pre_avg = np.mean(speeds[:len(speeds)//2])
#     post_avg = np.mean(speeds[len(speeds)//2:])

#    
#     return post_avg < pre_avg * 0.5
