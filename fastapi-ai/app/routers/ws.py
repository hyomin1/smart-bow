from fastapi import APIRouter, WebSocket
import cv2
from app.services.arrow_service import ArrowService
from app.services.target_service import get_target_info, get_target_raw
import app.config as config
import asyncio
router = APIRouter()

arrow_service = ArrowService()

async def capture_frames(queue,cap):
    """카메라 프레임을 계속 읽어서 queue에 넣기"""
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        await queue.put(frame)

async def run_inference(queue,ws,arrow_service,target_info):
    """큐에서 프레임을 꺼내 YOLO 추론 후 결과를 ws로 전송"""
    while True:
        frame = await queue.get()
        event = await asyncio.to_thread(arrow_service.detect,frame,target_info)
        await ws.send_json(event)
        queue.task_done()

@router.websocket("/ws/arrow-events")
async def coords_ws(ws: WebSocket):
    await ws.accept()
    cap = cv2.VideoCapture(config.VIDEO_SOURCE)  
    
    ok, frame = cap.read()
    target_info = get_target_raw(frame) if ok else None
    # 프론트에서 과녁 영역을 실제 좌표에서 보정을 해서 보여주므로 화살 검출 좌표도 보정을해야함, 과녁 영역 필요
    if target_info is None:
        await ws.send_json({"type": "error", "reason": "no_target"})
        await ws.close()
        return
   
    queue = asyncio.Queue(maxsize=10)
    await asyncio.gather(capture_frames(queue,cap),run_inference(queue,ws,arrow_service,target_info))
     

   
