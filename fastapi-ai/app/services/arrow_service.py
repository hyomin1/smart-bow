import cv2
import numpy as np
import time
from collections import deque
from app.models.yolo_arrow import ArrowModel 
from app.models.person_model import PersonModel
from app.services.target_service import TargetService   


class ArrowService:
    def __init__(self, buffer_size=30, cooldown_sec=3.0):
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

    def leading_tip_from_bbox(self, xyxy):
        """bbox 밑변의 중심을 tip으로 선택"""
        x1, y1, x2, y2 = map(int, xyxy)
      
        tip_x = (x1 + x2) // 2
        tip_y = (y1 + y2) // 2
        return np.array([tip_x, tip_y], dtype=np.float32)
    
    def detect(self, frame, with_hit=True):
        start_time = time.time()
       
        results = self.model.predict(frame)
        infer_time = time.time() - start_time
        print(f"[YOLO] 추론시간 {infer_time*1000:.1f}ms  ({1/infer_time:.1f} FPS)")
        now = time.time()

        event = {"type": "arrow", "tip": None, "bbox": None}
        if results.boxes is not None and len(results.boxes) > 0:
            conf = results.boxes.conf.cpu().numpy()
            best_conf_idx = int(np.argmax(conf))
            xyxy = results.boxes.xyxy[best_conf_idx].cpu().numpy()
         

            tip = self.leading_tip_from_bbox(xyxy)
            
            self.tracking_buffer.append((float(tip[0]), float(tip[1]), now))

            x1, y1, x2, y2 = map(int, xyxy)
            self.last_box = (x1,y1,x2,y2)
            event = {"type": "arrow", "tip": tip, "bbox": (x1, y1, x2, y2)}
            return event
        
        else: # 감지 안된 경우
            self.last_box = None
            if self.tracking_buffer:
                last_time = self.tracking_buffer[-1][2]
                elapsed = now - last_time

                if elapsed > 2.0: # 마지막 탐지 이후 일정 기간 안들어오면 판단 하기
                    print(f"버퍼 길이 {len(self.tracking_buffer)}, {self.tracking_buffer}")
                    # 판단 로직 추가
                    event = {"type": "arrow", "tip": None, "bbox": None}
                    self.tracking_buffer.clear()
                
                return event

   

        
    # def detect(self, frame, with_hit=True):
    #     """화살 검출 + 보정 + 명중 판정"""
    #     # 1. polygon 없으면 갱신

    #     if self.target_polygon is None:
    #         self.update_target_polygon(frame)
    #         if self.target_polygon is None:
    #             return {"type": "error", "reason": "no_target"}
            
        
    #     H, W = frame.shape[:2]
    #     results = self.model.predict(frame)
    #     now = time.time()

    #     event = {"type": "arrow", "tip": None, "bbox": None}
       
    #     if results.boxes is not None and len(results.boxes) > 0:
    #         xyxy = results.boxes.xyxy[0].cpu().numpy()
    #         x1, y1, x2, y2 = map(int, xyxy)
    #         tip = self.leading_tip_from_bbox(xyxy, H)
        
    #         self.last_box = (x1,y1,x2,y2)
          
    #         # polygon 내부 여부 확인
    #         corners = [(x1,y1),(x2,y1),(x1,y2),(x2,y2)]
            
    #         inside = any(cv2.pointPolygonTest(
    #                 self.target_polygon.astype(np.int32),
    #                 (float(x), float(y)),
    #                 False,
    #             ) >= 0
    #             for x, y in corners
    #         )

    #         if inside:
    #             if len(self.tracking_buffer) >= 2:
    #                 last_positions = [(x, y) for x, y, _ in list(self.tracking_buffer)[-3:]]
    #                 dists = [
    #                     np.hypot(last_positions[i+1][0] - last_positions[i][0],
    #                         last_positions[i+1][1] - last_positions[i][1])
    #                     for i in range(len(last_positions)-1)
    #                 ]
    #                 avg_dist = np.mean(dists)

    #                 polygon_bottom = int(np.max(self.target_polygon[:, 1]))

    #                 # 움직임이 거의 없는 경우 → 정지 화살로 판단
    #                 if avg_dist < 5 and tip[1] > polygon_bottom - 30:  
    #                     print("정지 화살 -> 버퍼 추가 안 함",self.tracking_buffer)
    #                     return event

    #                 # 동일 좌표 반복되면 정지 화살
    #             if self.tracking_buffer:
    #                 recent = list(self.tracking_buffer)[-5:]
    #                 same_count = sum(
    #                     abs(tip[0] - x) < 5 and abs(tip[1] - y) < 5
    #                     for x, y, _ in recent
    #                 )
    #                 if same_count >= len(recent) * 0.8:
    #                     print("반복 좌표 화살 -> 버퍼 추가 안 함",self.tracking_buffer)
    #                     return event
                
    #             self.tracking_buffer.append((tip[0], tip[1], now))

        
    #         event = {
    #             "type": "arrow",
    #             "tip": [float(tip[0]), float(tip[1])],
    #             "bbox": [x1, y1, x2, y2]
    #         }

    #         if not with_hit:
    #             return event
    #     else:
    #         self.last_box = None

    #     # hit 판정
    #     if (
    #         len(self.tracking_buffer) >= self.buffer_size
    #         or (2 <= len(self.tracking_buffer) and len(self.tracking_buffer) < self.buffer_size
    #             and now - self.tracking_buffer[-1][2] > 0.5)
    #     ):
    #         print('버퍼 확인',self.tracking_buffer)
     
    #         if  now - self.last_hit_time >= self.cooldown_sec:
            
    #             hit_tip = max(self.tracking_buffer, key=lambda p: p[1])  # y 가장 큰 값
    #             event["type"] = "hit"
    #             event["hit_tip"] = [float(hit_tip[0]), float(hit_tip[1])]
    #             self.last_hit_time = now
    #             self.tracking_buffer.clear()
    #             return event

    #         self.tracking_buffer.clear()
    #     else:
    #         if self.tracking_buffer:
    #             elapsed = now - self.tracking_buffer[-1][2]
    #             print("[DEBUG] HIT 조건 불충분:",
    #                 "len =", len(self.tracking_buffer),
    #                 "elapsed =", elapsed,
    #                 "buffer =", list(self.tracking_buffer))
                
    #             # inside 인데 1프레임만 잡힌 경우 1프레임으로 판정
    #             if len(self.tracking_buffer) == 1 and elapsed > 0.5:
    #                 # if now - self.last_hit_time >= self.cooldown_sec:
    #                 #     hit_tip = self.tracking_buffer[0]
    #                 #     event['type'] = 'hit'
    #                 #     event['hit_tip'] = [float(hit_tip[0]), float(hit_tip[1])]
    #                 #     self.last_hit_time = now
    #                 #     print("1 프레임 HIT 발생:")
    #                 #     self.tracking_buffer.clear()
    #                 #     return event
    #                 print("[DEBUG] 버퍼 초기화 (1프레임 오래됌)")
    #                 self.tracking_buffer.clear()
    #         else:
    #             elapsed = None



    #     return event




