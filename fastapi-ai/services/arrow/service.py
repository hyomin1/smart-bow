import time, cv2, numpy as np, os, datetime
from collections import deque
from config import BASE_DIR


class ArrowService:
    def __init__(self, buffer_size=10, idle_sec=2.0, cooldown_sec=8.0):
        self.tracking_buffer = deque(maxlen=buffer_size)
        self.idle_sec = idle_sec
        self.cooldown_sec = cooldown_sec
        self.last_event_time = None
        self.last_hit_time = 0.0
        self.target = None
        self.last_bbox = None

        self.frame_size = None
        self.last_frame = None  # 화살 위치 디버그용 추후 서비스 안정화되면 제거

    def to_render_coords(self, x, y, video_size):
        if video_size is None or self.frame_size is None:
            return None

        render_w, render_h = video_size
        frame_w, frame_h = self.frame_size

        scale_x = render_w / frame_w
        scale_y = render_h / frame_h
        scale = min(scale_x, scale_y)

        pad_x = (render_w - frame_w * scale) / 2
        pad_y = (render_h - frame_h * scale) / 2

        rx = x * scale + pad_x
        ry = y * scale + pad_y

        return [float(rx), float(ry)]

    def polygon_to_render(self, video_size):
        if self.target is None or self.frame_size is None:
            return None

        render_poly = []
        for x, y in self.target:
            p = self.to_render_coords(x, y, video_size)
            if p:
                render_poly.append(p)

        return render_poly

    def add_event(self, event):

        if event.get("target") is not None:
            self.target = np.array(event["target"], dtype=np.int32)

        if event.get("frame_size") is not None:
            self.frame_size = tuple(event["frame_size"])

        if event["type"] == "arrow" and event["tip"] is not None:
            tip = event["tip"]

            if self.tracking_buffer:
                last = self.tracking_buffer[-1]
                last_x, last_y = last[0], last[1]
                if (abs(last_x - tip[0]) < 5) and (abs(last_y - tip[1]) < 5):
                    return

            x1, y1, x2, y2 = event["bbox"]
            self.last_bbox = (x1, y1, x2, y2)

            # 화살 위치 디버그용 추후 서비스 안정화되면 제거
            arrow_crop = None
            if self.last_frame is not None:
                try:
                    arrow_crop = self.last_frame[y1:y2, x1:x2].copy()
                except:
                    pass

            self.tracking_buffer.append(
                (
                    tip[0],
                    tip[1],
                    event["timestamp"],
                    x1,
                    y1,
                    x2,
                    y2,
                    arrow_crop,
                    event["conf"],
                )
            )
            self.last_event_time = time.time()
        else:
            self.last_bbox = None

    def visualize_buffer(self, hit_point):
        if not self.tracking_buffer or self.last_frame is None:
            return
        print("그린다")
        vis_frame = self.last_frame.copy()

        for i, data in enumerate(self.tracking_buffer):
            if len(data) == 9:  # crop 포함된 버전
                x, y, t, x1, y1, x2, y2, arrow_crop, confidence = data
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                if arrow_crop is not None:
                    h, w = arrow_crop.shape[:2]
                    try:
                        vis_frame[y1 : y1 + h, x1 : x1 + w] = arrow_crop
                    except:
                        pass

                # bbox 색상
                alpha = (i + 1) / len(self.tracking_buffer)
                color = (0, int(255 * alpha), int(255 * (1 - alpha)))

                # bbox 테두리
                cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    vis_frame,
                    str(i),
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                )

                cv2.putText(
                    vis_frame,
                    f"{confidence:.2f}",
                    (x1, y2 + 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 0),
                    2,
                )
                cv2.circle(vis_frame, (int(x), int(y)), 4, color, -1)

        if hit_point is not None:
            hit_x, hit_y = int(hit_point[0]), int(hit_point[1])
            cv2.circle(vis_frame, (hit_x, hit_y), 15, (0, 0, 255), 3)
            cv2.circle(vis_frame, (hit_x, hit_y), 5, (0, 0, 255), -1)
            cv2.putText(
                vis_frame,
                "HIT",
                (hit_x + 20, hit_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3,
            )
            cv2.putText(
                vis_frame,
                f"({hit_x}, {hit_y})",
                (hit_x + 20, hit_y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")
        save_dir = os.path.join(BASE_DIR, date_str)
        os.makedirs(save_dir, exist_ok=True)

        save_path = os.path.join(save_dir, f"{time_str}.jpg")
        cv2.imwrite(save_path, vis_frame)

    def is_idle(self):
        if not self.tracking_buffer or self.last_event_time is None:
            return False
        now = time.time()
        if now - self.last_hit_time < self.cooldown_sec:
            return False

        return time.time() - self.last_event_time > self.idle_sec

    def clear_buffer(self):
        self.tracking_buffer.clear()

    def _closest_point_on_polygon(self, point, polygon):

        px, py = point
        min_dist = float("inf")
        closest_point = None

        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]  # 다음 꼭짓점 (마지막은 첫번째로)

            # 선분 p1-p2에서 point까지 가장 가까운 점 찾기
            x1, y1 = float(p1[0]), float(p1[1])
            x2, y2 = float(p2[0]), float(p2[1])

            # 선분의 방향 벡터
            dx = x2 - x1
            dy = y2 - y1

            if dx == 0 and dy == 0:  # 같은 점이면 스킵
                continue

            # t = 선분 위의 위치 (0~1 사이)
            t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))

            # 선분 위의 가장 가까운 점
            closest_x = x1 + t * dx
            closest_y = y1 + t * dy

            # 거리 계산
            dist = np.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)

            if dist < min_dist:
                min_dist = dist
                closest_point = (closest_x, closest_y)

        return closest_point

    def find_hit_point(self):
        tips = [(round(x, 1), round(y, 1)) for (x, y, *_rest) in self.tracking_buffer]
        print(f"판정버퍼 len={len(self.tracking_buffer)}, tips={tips}")
        if len(self.tracking_buffer) < 2:
            self.clear_buffer()
            return None

        y_coords = [data[1] for data in self.tracking_buffer]

        # 오탐 정지 물체 필터링
        y_min, y_max = min(y_coords), max(y_coords)
        total_height = y_max - y_min

        if total_height < 15:
            self.clear_buffer()
            return None

        # 적중하면 변곡점이 나온다.
        for i in range(len(y_coords) - 1):
            if y_coords[i + 1] < y_coords[i]:
                x, y = self.tracking_buffer[i][0], self.tracking_buffer[i][1]
                raw_hit = [float(x), float(y)]

                if self.target is not None:
                    inside = cv2.pointPolygonTest(self.target, raw_hit, False) >= 0

                    if inside:
                        print(f"[HIT-변곡점] 과녁 안: {raw_hit}")
                        return raw_hit

                    for data in self.tracking_buffer:
                        px, py = float(data[0]), float(data[1])
                        if cv2.pointPolygonTest(self.target, [px, py], False) >= 0:
                            print(
                                f"[HIT-보정] 버퍼에서 과녁 안 좌표 발견: ({px}, {py})"
                            )
                            return [px, py]

                        closest_point = self._closest_point_on_polygon(
                            [x, y], self.target
                        )

                        if closest_point:
                            closest_x, closest_y = closest_point

                            M = cv2.moments(self.target)
                            if M["m00"] != 0:
                                cx = M["m10"] / M["m00"]
                                cy = M["m01"] / M["m00"]

                                dx = cx - closest_x
                                dy = cy - closest_y
                                length = np.sqrt(dx**2 + dy**2)

                                if length > 0:
                                    dx, dy = dx / length, dy / length
                                    closest_x += dx * 35
                                    closest_y += dy * 35
                            print(
                                f"[HIT-보정] 가장 가까운 테두리 안쪽: ({closest_x}, {closest_y})"
                            )
                            return [closest_x, closest_y]
                        else:
                            return [x, y]
                else:
                    return [x, y]

        # 변곡점 없는 경우 적중 X or 적중했지만 변곡점 감지 안되는 경우가 있다
        x, y = self.tracking_buffer[-1][0], self.tracking_buffer[-1][1]
        raw_hit = [float(x), float(y)]

        if self.target is None:
            print(f"[HIT] raw={raw_hit}")
            return raw_hit

        inside = cv2.pointPolygonTest(self.target, raw_hit, False) >= 0

        if inside:
            print(f"[HIT] 마지막 좌표 과녁 안")
            return raw_hit

        for data in self.tracking_buffer:
            px, py = float(data[0]), float(data[1])
            if cv2.pointPolygonTest(self.target, [px, py], False) >= 0:
                print(f"[HIT] 버퍼에서 과녁 안 좌표 발견: ({px}, {py})")
                return [px, py]
        print(f"[HIT] 과녁 밖 좌표 그대로 반환")
        return raw_hit
