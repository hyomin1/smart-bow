import time, cv2, numpy as np
from collections import deque


class ArrowService:
    def __init__(self, buffer_size=10, idle_sec=2.0, cooldown_sec=8.0):
        self.tracking_buffer = deque(maxlen=buffer_size)
        self.idle_sec = idle_sec
        self.cooldown_sec = cooldown_sec
        self.last_event_time = None
        self.last_hit_time = 0.0
        self.target = None
        self.last_bbox = None

        self.video_rect = None
        self.frame_size = None

    def to_render_coords(self, x, y):
        if self.video_rect is None or self.frame_size is None:
            return None

        render_w, render_h = self.video_rect
        frame_w, frame_h = self.frame_size

        scale_x = render_w / frame_w
        scale_y = render_h / frame_h
        scale = min(scale_x, scale_y)

        pad_x = (render_w - frame_w * scale) / 2
        pad_y = (render_h - frame_h * scale) / 2

        rx = x * scale + pad_x
        ry = y * scale + pad_y

        return [float(rx), float(ry)]

    def polygon_to_render(self):
        if self.target is None or self.frame_size is None or self.video_rect is None:
            return None

        render_poly = []
        for x, y in self.target:
            p = self.to_render_coords(x, y)
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

            self.tracking_buffer.append(
                (
                    tip[0],
                    tip[1],
                    event["timestamp"],
                    x1,
                    y1,
                    x2,
                    y2,
                    None,
                    event["conf"],
                )
            )
            self.last_event_time = time.time()
        else:
            self.last_bbox = None

    def is_idle(self):
        if not self.tracking_buffer or self.last_event_time is None:
            return False
        now = time.time()
        if now - self.last_hit_time < self.cooldown_sec:
            return False

        return time.time() - self.last_event_time > self.idle_sec

    def clear_buffer(self):
        self.tracking_buffer.clear()

    def _find_hit_point(self):
        tips = [(round(x, 1), round(y, 1)) for (x, y, *_rest) in self.tracking_buffer]
        print(f"판정버퍼 len={len(self.tracking_buffer)}, tips={tips}")
        if len(self.tracking_buffer) < 3:
            self.clear_buffer()
            return None

        y_coords = [data[1] for data in self.tracking_buffer]

        # 오탐 정지 물체 필터링
        y_min, y_max = min(y_coords), max(y_coords)
        total_height = y_max - y_min

        if total_height < 30:
            self.clear_buffer()
            return None

        # 적중하면 변곡점이 나온다.
        for i in range(len(y_coords) - 1):
            if y_coords[i + 1] < y_coords[i]:
                x, y = self.tracking_buffer[i][0], self.tracking_buffer[i][1]
                raw_hit = [float(x), float(y)]
                return self.to_render_coords(x, y)

        # 변곡점 없는 경우 적중 X or 적중했지만 변곡점 감지 안되는 경우가 있다
        x, y = self.tracking_buffer[-1][0], self.tracking_buffer[-1][1]
        raw_hit = [float(x), float(y)]

        if self.target is None:
            return self.to_render_coords(x, y)

        inside = cv2.pointPolygonTest(self.target, raw_hit, False) >= 0

        if inside:
            return self.to_render_coords(x, y)

        for data in self.tracking_buffer:
            px, py = float(data[0]), float(data[1])
            if cv2.pointPolygonTest(self.target, [px, py], False) >= 0:
                return self.to_render_coords(px, py)

        return self.to_render_coords(x, y)
