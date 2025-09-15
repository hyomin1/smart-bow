import cv2
import numpy as np
import time
from collections import deque
from app.models.yolo_arrow import ArrowModel 
from app.services.target_service import TargetService   


class ArrowService:
    def __init__(self, cam_key, cooldown_sec: float = 2.5, buffer_size: int = 7):
       
        self.model = ArrowModel()

      
        self.cooldown_sec = cooldown_sec
        self.last_hit_time = 0

        # 상태 관리
        self.state = "idle"  # idle → tracking → hit_confirmed
        self.tracking_buffer = deque(maxlen=buffer_size)
        self.buffer_size = buffer_size

  
        self.target_service = TargetService(cam_key)
        self.cam_key = cam_key
        self.target_polygon = None   

    def update_target_polygon(self, frame):
        """필요할 때만 과녁 polygon 갱신"""
        target_pts = self.target_service.get_target_raw(frame)
        if target_pts is not None:
            self.target_polygon = np.array(target_pts, dtype=np.float32)

    def leading_tip_from_bbox(self, xyxy, H):
        """bbox corner 중 아래쪽을 tip으로 선택"""
        x1, y1, x2, y2 = xyxy
        corners = np.array([[x1, y1], [x2, y1], [x1, y2], [x2, y2]], dtype=np.float32)
        d_bottom = H - corners[:, 1]
        tip = corners[np.argmin(d_bottom)]
        return tip

    def detect(self, frame):
        """화살 검출 + 보정 + 명중 판정"""
        # 1. polygon 없으면 갱신
        if self.target_polygon is None:
            self.update_target_polygon(frame)
            if self.target_polygon is None:
                return {"type": "error", "reason": "no_target"}

        # 2. YOLO로 화살 검출
        H, W = frame.shape[:2]
        results = self.model.predict(frame)

        if results.boxes is None or len(results.boxes) == 0:
            # 화살 검출 안 됨
            if self.state == "tracking":
                if time.time() - self.tracking_buffer[-1][2] > 0.5:
                    self.state = "idle"
                    self.tracking_buffer.clear()
            return {"type": "arrow", "tip": None, "corrected_tip": None}

        # bbox → tip 추출
        xyxy = results.boxes.xyxy[0].cpu().numpy()
        tip = self.leading_tip_from_bbox(xyxy, H)
        corrected_tip = tip
        now = time.time()

        # polygon 내부 여부 확인
        inside = cv2.pointPolygonTest(
            self.target_polygon.astype(np.int32),
            (float(corrected_tip[0]), float(corrected_tip[1])),
            False,
        ) >= 0

        event = {
            "type": "arrow",
            "tip": [float(tip[0]), float(tip[1])],
            "corrected_tip": [float(corrected_tip[0]), float(corrected_tip[1])],
        }

        # 3. state machine (hit 판정)
        if self.state == "idle" and inside:
            self.state = "tracking"
            self.tracking_buffer.clear()
            self.tracking_buffer.append((tip[0], tip[1], now))

        elif self.state == "tracking":
            self.tracking_buffer.append((tip[0], tip[1], now))

            if len(self.tracking_buffer) >= self.buffer_size:
                inside_ratio = sum(
                    cv2.pointPolygonTest(
                        self.target_polygon.astype(np.int32),
                        (float(x), float(y)),
                        False,
                    ) >= 0
                    for x, y, _ in self.tracking_buffer
                ) / len(self.tracking_buffer)

                # 조건 만족 → hit 확정
                if inside_ratio >= 0.6 and (now - self.last_hit_time) >= self.cooldown_sec:
                    inside_points = [
                        (x, y) for x, y, _ in self.tracking_buffer
                        if cv2.pointPolygonTest(self.target_polygon, (x, y), False) >= 0
                    ]
                    if inside_points:
                        # polygon 안에서 가장 깊숙한 좌표 선택
                        hit_tip = max(
                            inside_points,
                            key=lambda p: cv2.pointPolygonTest(self.target_polygon, (p[0], p[1]), True)
                        )
                        self.last_hit_time = now
                        self.state = "hit_confirmed"

                        event["type"] = "hit"
                        event["hit_tip"] = [float(hit_tip[0]), float(hit_tip[1])]
                        return event

        elif self.state == "hit_confirmed":
            # 쿨다운 지나면 idle로 복귀
            if now - self.last_hit_time >= self.cooldown_sec:
                self.state = "idle"
                self.tracking_buffer.clear()

        return event
