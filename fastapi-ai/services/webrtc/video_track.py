import asyncio, cv2, time
from aiortc import VideoStreamTrack
from av import VideoFrame


class CameraVideoTrack(VideoStreamTrack):
    def __init__(self, arrow_service, person_service):
        super().__init__()
        self.queue = asyncio.Queue(maxsize=2)
        self.arrow_service = arrow_service
        self.person_service = person_service
        self.last_frame_time = 0
        self.fps_limit = 20

    async def push(self, frame):
        if self.queue.full():
            try:
                self.queue.get_nowait()
            except:
                pass
        await self.queue.put(frame)

    async def recv(self):
        frame = await self.queue.get()

        now = time.time()
        elapsed = now - self.last_frame_time
        target_delay = 1.0 / self.fps_limit

        if elapsed < target_delay:
            await asyncio.sleep(target_delay - elapsed)

        self.last_frame_time = time.time()

        frame = frame.copy()
        self.arrow_service.last_frame = (
            frame.copy()
        )  # 화살 위치 디버그용 추후 서비스 안정화되면 제거

        zoom_bbox = self.person_service.get_zoom_area()
        if zoom_bbox:
            x1, y1, x2, y2 = map(int, zoom_bbox)

            h, w = frame.shape[:2]

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            zoom_scale = 2.0

            crop_w = int(w / zoom_scale)
            crop_h = int(h / zoom_scale)

            crop_x1 = max(0, center_x - crop_w // 2)
            crop_y1 = max(0, center_y - crop_h // 2)
            crop_x2 = min(w, crop_x1 + crop_w)
            crop_y2 = min(h, crop_y1 + crop_h)

            cropped = frame[crop_y1:crop_y2, crop_x1:crop_x2]

            frame = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LANCZOS4)

        if self.arrow_service.last_bbox:
            x1, y1, x2, y2 = map(int, self.arrow_service.last_bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        av_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        av_frame.pts, av_frame.time_base = await self.next_timestamp()
        return av_frame
