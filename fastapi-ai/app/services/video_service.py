from aiortc import VideoStreamTrack
from av import VideoFrame
from app.services.arrow_registry import arrow_registry
from app.services.shooter_registry import shooter_registry
import numpy as np
import cv2, asyncio, time


class CameraVideoTrack(VideoStreamTrack):
    def __init__(self, frame_manager, cam_id):
        super().__init__()
        self.frame_manager = frame_manager
        self.cam_id = cam_id
    
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
        
        frame = frame.copy()

        if self.cam_id.startswith('target'):
            arrow_service = arrow_registry.get(self.cam_id)
            if arrow_service.last_box is not None:
                x1, y1, x2, y2 = arrow_service.last_box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        elif self.cam_id.startswith('shooter'):
            shooter_service = shooter_registry.get(self.cam_id)
            if shooter_service.last_frame is not None:
                frame = shooter_service.last_frame
          

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame
