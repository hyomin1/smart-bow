import cv2
import numpy as np
import time
from collections import deque
from app.models.yolo_arrow import ArrowModel 
from app.models.person_model import PersonModel
from app.services.target_service import TargetService   


class ArrowService:
    def __init__(self, buffer_size=7, cooldown_sec=3.0):
        self.model = ArrowModel()
        self.person_model = PersonModel()
        self.tracking_buffer = deque(maxlen=buffer_size)
        self.buffer_size = buffer_size

        self.target_service = TargetService()
        self.target_polygon = None

        self.last_hit_time = 0
        self.cooldown_sec = cooldown_sec

        self.last_box = None   

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
    
    def is_valid_hit(self):
        if len(self.tracking_buffer) < 3:
            return True
    
        speeds = []
        for i in range(1, len(self.tracking_buffer)):
            x1, y1, t1 = self.tracking_buffer[i-1]
            x2, y2, t2 = self.tracking_buffer[i]
            dt = max(t2 - t1, 1e-3)
            v = np.linalg.norm([x2 - x1, y2 - y1]) / dt
            speeds.append(v)

        if not speeds:
            return False

        pre_avg = np.mean(speeds[:len(speeds)//2])
        post_avg = np.mean(speeds[len(speeds)//2:])

        return post_avg < pre_avg * 0.5

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
       
        if results.boxes is not None and len(results.boxes) > 0:
            xyxy = results.boxes.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, xyxy)
            tip = self.leading_tip_from_bbox(xyxy, H)
        
            self.last_box = (x1,y1,x2,y2)
          
            # polygon 내부 여부 확인
            corners = [(x1,y1),(x2,y1),(x1,y2),(x2,y2)]
            inside = any(cv2.pointPolygonTest(
                    self.target_polygon.astype(np.int32),
                    (float(x), float(y)),
                    False,
                ) >= 0
                for x, y in corners
            )

            if inside:
                if len(self.tracking_buffer) >= 2:
                    last_positions = [(x, y) for x, y, _ in list(self.tracking_buffer)[-3:]]
                    dists = [
                        np.hypot(last_positions[i+1][0] - last_positions[i][0],
                            last_positions[i+1][1] - last_positions[i][1])
                        for i in range(len(last_positions)-1)
                    ]
                    avg_dist = np.mean(dists)

                    # 움직임이 거의 없는 경우 → 정지 화살로 판단
                    if avg_dist < 5:  
                        print("정지 화살 -> 버퍼 추가 안 함",self.tracking_buffer)
                        return event

                    # 동일 좌표 반복되면 정지 화살
                if self.tracking_buffer:
                    recent = list(self.tracking_buffer)[-5:]
                    same_count = sum(
                        abs(tip[0] - x) < 5 and abs(tip[1] - y) < 5
                        for x, y, _ in recent
                    )
                    if same_count >= len(recent) * 0.8:
                        print("반복 좌표 화살 -> 버퍼 추가 안 함",self.tracking_buffer)
                        return event

                self.tracking_buffer.append((tip[0], tip[1], now))

        
            event = {
                "type": "arrow",
                "tip": [float(tip[0]), float(tip[1])],
                "bbox": [x1, y1, x2, y2]
            }

            if not with_hit:
                return event
        else:
            self.last_box = None

        # hit 판정
        if (
            len(self.tracking_buffer) >= self.buffer_size
            or (2 <= len(self.tracking_buffer) and len(self.tracking_buffer) < self.buffer_size
                and now - self.tracking_buffer[-1][2] > 0.5)
        ):
            print('버퍼 확인',self.tracking_buffer)
     
            if  now - self.last_hit_time >= self.cooldown_sec:
            
                hit_tip = max(self.tracking_buffer, key=lambda p: p[1])  # y 가장 큰 값
                event["type"] = "hit"
                event["hit_tip"] = [float(hit_tip[0]), float(hit_tip[1])]
                self.last_hit_time = now
                self.tracking_buffer.clear()
                return event

            self.tracking_buffer.clear()
        return event


arrow_service = ArrowService()

