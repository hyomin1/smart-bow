import asyncio
import cv2

from aiortc import VideoStreamTrack
from av import VideoFrame
from app.frame_manager import frame_queue
from app.services.arrow_service import ArrowService
from app.core import config  

arrow_service = ArrowService()

class ArrowVideoTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
      
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        if not frame_queue.empty():
            frame = frame_queue.get()
        else:
            await asyncio.sleep(0.01)
            return await self.recv()

        event = await asyncio.to_thread(arrow_service.detect, frame, with_hit=False)

        # 스트리밍용 화살 그리기
        if event and event.get("bbox"):
            x1, y1, x2, y2 = event["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # 스트리밍용 과녁 그리기
        # if arrow_service.target_polygon is not None:
        #     pts_poly = arrow_service.target_polygon.astype(int).reshape((-1, 1, 2))
        #     cv2.polylines(frame, [pts_poly], isClosed=True, color=(0, 0, 255), thickness=2)

        new_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        new_frame.pts = pts
        new_frame.time_base = time_base
        return new_frame
