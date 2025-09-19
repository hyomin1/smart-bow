from aiortc import VideoStreamTrack
from av import VideoFrame
from app.services.arrow_service import ArrowService

import numpy as np
import cv2, asyncio, time

arrow_service = ArrowService()


class CameraVideoTrack(VideoStreamTrack):
    def __init__(self, frame_manager):
        super().__init__()
        self.frame_manager = frame_manager
    
    def _reconnect(self):
        print("[WARN] 스트림 끊김 -> 재연결 시도중 ...")
        self.cap = cv2.VideoCapture(self.source)
        self.last_reconnect_time = time.time()

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        frame = self.frame_manager.get_frame()

        if frame is None:
            await asyncio.sleep(0.01)
            return await self.recv()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame
