import cv2
import numpy as np
import time
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

    def visualize_buffer(self, frame, save_path="buffer_visualization.jpg"):
        if self._isEmpty():
            return

        vis_frame = frame.copy()

        # 적중 지점 미리 찾기
        hit_point = self._find_hit_point()

        for i, data in enumerate(self.tracking_buffer):
            if len(data) == 7:  # bbox 정보 있음
                x, y, t, x1, y1, x2, y2 = data
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # 적중 지점이면 빨간색으로 강조
                is_hit_point = False
                if hit_point is not None:
                    if abs(x - hit_point[0]) < 1 and abs(y - hit_point[1]) < 1:
                        is_hit_point = True

                if is_hit_point:
                    color = (0, 0, 255)  # 빨간색
                    thickness = 4
                else:
                    alpha = (i + 1) / len(self.tracking_buffer)
                    color = (0, int(255 * alpha), int(255 * (1 - alpha)))
                    thickness = 2

                # bbox 그리기
                cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(
                    vis_frame,
                    str(i),
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                )

                # tip 위치에 작은 원 표시
                cv2.circle(vis_frame, (int(x), int(y)), 3, color, -1)

            else:  # 기존 데이터 (x, y, t)
                x, y, t = data
                cv2.circle(vis_frame, (int(x), int(y)), 5, (0, 255, 0), -1)

        # 적중 지점에 큰 원과 텍스트 표시
        if hit_point is not None:
            hit_x, hit_y = int(hit_point[0]), int(hit_point[1])
            cv2.circle(vis_frame, (hit_x, hit_y), 15, (0, 0, 255), 3)  # 큰 원
            cv2.circle(vis_frame, (hit_x, hit_y), 5, (0, 0, 255), -1)  # 중심점
            cv2.putText(
                vis_frame,
                "HIT",
                (hit_x + 20, hit_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3,
            )

            # 좌표 표시
            cv2.putText(
                vis_frame,
                f"({hit_x}, {hit_y})",
                (hit_x + 20, hit_y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

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
        if result >= 0 and last_point[1] >= 870:
            return [float(last[0]), 925.0]

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

        if self.target_polygon is None:
            self.update_target_polygon(frame)

        results = self.model.predict(frame)
        now = time.time()

        event = {"type": "arrow", "tip": None, "bbox": None}
        if results.boxes is not None and len(results.boxes) > 0:
            conf = results.boxes.conf.cpu().numpy()
            best_conf_idx = int(np.argmax(conf))
            xyxy = results.boxes.xyxy[best_conf_idx].cpu().numpy()
            x1, y1, x2, y2 = map(int, xyxy)
            tip = self.leading_tip_from_bbox(xyxy)

            should_add = self._should_add_to_buffer(tip)

            if should_add:
                self.tracking_buffer.append(
                    (float(tip[0]), float(tip[1]), now, x1, y1, x2, y2)
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
                    # print(
                    #     f"버퍼 길이 {len(self.tracking_buffer)}, {self.tracking_buffer}"
                    # )
                    if len(self.tracking_buffer) <= 2:
                        self.tracking_buffer.clear()
                        return event
                    self.visualize_buffer(frame, f"buffer_vis_{int(now)}.jpg")

                    # hit
                    hit_point = self._find_hit_point()
                    # print("hit_point", hit_point)
                    if hit_point is not None:
                        event = {"type": "hit", "tip": hit_point, "bbox": None}
                    else:
                        event = {
                            "type": "arrow",
                            "tip": None,
                            "bbox": None,
                        }

                    self.tracking_buffer.clear()
                    return event

            return event
