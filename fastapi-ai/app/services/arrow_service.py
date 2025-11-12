import cv2
import numpy as np
import time
import os
import datetime
from collections import deque
from app.models.yolo_arrow import ArrowModel
from app.models.person_model import PersonModel
from app.services.target_service import TargetService


class ArrowService:
    def __init__(self, buffer_size=10, cooldown_sec=3.0):
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
        tip_y = y2
        return np.array([tip_x, tip_y], dtype=np.float32)

    def _isEmpty(self):
        return len(self.tracking_buffer) == 0

    def _is_y_change_too_small(self, tip, threshold=3):
        """오탐 되는 것들은 y좌표 변화량이 적음 -> 필터링"""
        if self._isEmpty():
            return False

        last_y = self.tracking_buffer[-1][1]
        y_diff = abs(tip[1] - last_y)
        # print(f"현재 tip y={tip[1]}, 버퍼 마지막 y={last_y}, 차이={y_diff}")
        if y_diff < threshold:

            # print("판정되지만 변화량 적음", tip)
            return True

        return False

    def _should_add_to_buffer(self, tip):
        if self._isEmpty():
            return True        

        is_small_change = self._is_y_change_too_small(tip)

        if is_small_change:
            return False

        return True
    def _is_false_positive(self, threshold_total=25, threshold_avg=3):
        if len(self.tracking_buffer) < 3:
            return True

        coords = [(d[0], d[1]) for d in self.tracking_buffer]
        total_dist = 0
        for i in range(1, len(coords)):
            dx = coords[i][0] - coords[i - 1][0]
            dy = coords[i][1] - coords[i - 1][1]
            total_dist += (dx**2 + dy**2) ** 0.5

        avg_dist = total_dist / len(coords)
        print(f"[total_move={total_dist:.1f}px, avg_move={avg_dist:.1f}px]")

        if total_dist < threshold_total or avg_dist < threshold_avg:
            print("정지 오탐 감지됨 — hit 무효 처리")
            return True

        return False

    def visualize_buffer(self, frame, base_dir="/home/gwandugjung/workspace/data"):
        """버퍼에 저장된 실제 화살 crop을 복원해서 그리기"""
        if self._isEmpty():
            return

        vis_frame = frame.copy()

        hit_point = self._find_hit_point()

        for i, data in enumerate(self.tracking_buffer):
            if len(data) == 9:  # crop 포함된 버전
                x, y, t, x1, y1, x2, y2, arrow_crop, confidence = data
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # 🔥 실제 화살 영상 복원 (bbox 안에 다시 붙이기)
                h, w = arrow_crop.shape[:2]
                vis_frame[y1:y1+h, x1:x1+w] = arrow_crop

                # bbox 색상
                alpha = (i + 1) / len(self.tracking_buffer)
                color = (0, int(255 * alpha), int(255 * (1 - alpha)))

                # bbox 테두리
                cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(vis_frame, str(i), (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                cv2.putText(vis_frame, f"{confidence:.2f}", (x1, y2 + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                cv2.circle(vis_frame, (int(x), int(y)), 4, color, -1)

        # 🎯 HIT 표시
        if hit_point is not None:
            hit_x, hit_y = int(hit_point[0]), int(hit_point[1])
            cv2.circle(vis_frame, (hit_x, hit_y), 15, (0, 0, 255), 3)
            cv2.circle(vis_frame, (hit_x, hit_y), 5, (0, 0, 255), -1)
            cv2.putText(vis_frame, "HIT", (hit_x + 20, hit_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            cv2.putText(vis_frame, f"({hit_x}, {hit_y})", (hit_x + 20, hit_y + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
        
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")
        save_dir = os.path.join(base_dir, date_str)
        os.makedirs(save_dir, exist_ok=True)

        save_path = os.path.join(save_dir, f"{time_str}.jpg")
        cv2.imwrite(save_path, vis_frame)


    def _find_hit_point(self):
        buffer_len = len(self.tracking_buffer)
        if buffer_len <= 2:
            return None

        y_coords = [data[1] for data in self.tracking_buffer]

        for i in range(1, len(y_coords) - 1):
            if y_coords[i + 1] < y_coords[i]:
                data = self.tracking_buffer[i]
                # print("화살 적중 변곡점 발견")
                return [float(data[0]), float(data[1])]

        last = self.tracking_buffer[-1]
        last_point = [float(last[0]), float(last[1])]

        if self.target_polygon is None:
            return last_point

        result = cv2.pointPolygonTest(self.target_polygon, last_point, False)

        #  1. 마지막 좌표가 과녁 내부이고 y가 870 이상이면 y를 910으로 수정
        # if result >= 0 and last_point[1] >= 870:
        #     return [float(last[0]), 925.0]

        # 2. 마지막 좌표가 과녁 내부
        if result >= 0:
            return last_point

        # 3. 마지막 좌표가 과녁 밖 - 버퍼에서 과녁 내부 좌표 찾기
        for data in self.tracking_buffer:
            point = [float(data[0]), float(data[1])]
            result = cv2.pointPolygonTest(self.target_polygon, point, False)
            if result >= 0:
                return point

        # 4. 버퍼에 과녁 내부 좌표가 하나도 없음 - 마지막 좌표 반환
        return [float(last[0]), float(last[1])]

    def detect(self, frame, with_hit=True):
        now = time.time()

        if now - self.last_hit_time < self.cooldown_sec:
            return {"type": "cooldown", "tip":None, "bbox":None}

        if self.target_polygon is None:
            self.update_target_polygon(frame)

           
        #start = time.time()
        results = self.model.predict(frame)
        #inference_time = time.time() - start
        #print(f"[YOLO 추론] {inference_time*1000:.1f}ms (FPS: {1/inference_time:.1f})")
        event = {"type": "arrow", "tip": None, "bbox": None}

        if results.boxes is not None and len(results.boxes) > 0:
            conf = results.boxes.conf.cpu().numpy()
            best_conf_idx = int(np.argmax(conf))
            xyxy = results.boxes.xyxy[best_conf_idx].cpu().numpy()
            x1, y1, x2, y2 = map(int, xyxy)
            tip = self.leading_tip_from_bbox(xyxy)

            

           
            arrow_crop = frame[y1:y2, x1:x2].copy()
            confidence = float(conf[best_conf_idx])
            self.tracking_buffer.append(
                (float(tip[0]), float(tip[1]), now, x1, y1, x2, y2, arrow_crop, confidence)
            )

            self.last_box = (x1, y1, x2, y2)
            event = {"type": "arrow", "tip": tip, "bbox": (x1, y1, x2, y2)}
            return event

        else:  # 감지 안된 경우
            self.last_box = None
            if self.tracking_buffer:
                last_time = self.tracking_buffer[-1][2]
                elapsed = now - last_time

                if elapsed > 1.0:  # 마지막 탐지 이후 1초동안 안들어오면 판단 하기
                    print(
                         f"버퍼 길이 {len(self.tracking_buffer)}, {self.tracking_buffer}"
                    )
                    if len(self.tracking_buffer) <= 2:
                        self.tracking_buffer.clear()
                        return event

                    if self._is_false_positive():
                        self.tracking_buffer.clear()
                        return event
                        
                    self.visualize_buffer(frame)

                    # hit
                    hit_point = self._find_hit_point()
                    # print("hit_point", hit_point)
                    if hit_point is not None:
                        self.last_hit_time = now
                        if self.target_polygon is not None:
                            inside = (
                                cv2.pointPolygonTest(
                                    self.target_polygon, hit_point, False
                                )
                                >= 0
                            )
                        else:
                            inside = False
                        event = {"type": "hit", "tip": hit_point, "bbox": None, "inside":inside}
                    else:
                        event = {
                            "type": "arrow",
                            "tip": None,
                            "bbox": None,
                        }

                    self.tracking_buffer.clear()
                    return event

            return event
