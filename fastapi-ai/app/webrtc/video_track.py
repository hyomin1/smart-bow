import asyncio, cv2, numpy as np
from aiortc import VideoStreamTrack
from av import VideoFrame


class CameraVideoTrack(VideoStreamTrack):
    def __init__(self, arrow_service):
        super().__init__()
        self.queue = asyncio.Queue(maxsize=2)
        self.arrow_service = arrow_service

    async def push(self, frame):
        if self.queue.full():
            try:
                self.queue.get_nowait()
            except:
                pass
        await self.queue.put(frame)

    async def recv(self):
        frame = await self.queue.get()

        frame = frame.copy()

        if self.arrow_service.last_bbox:
            x1, y1, x2, y2 = map(int, self.arrow_service.last_bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        av_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        av_frame.pts, av_frame.time_base = await self.next_timestamp()
        return av_frame
