import cv2
import asyncio
from fastapi import APIRouter, WebSocket
from app.services.arrow_service import ArrowService
from app.utils.transform import get_perspective_transform, transform_points
from app.core import config

router = APIRouter()


arrow_service = ArrowService(config.CAMERA_URLS["test"])
clients = []


@router.websocket("/ws/arrow")
async def arrow_ws(ws: WebSocket):
    await ws.accept()

    tw = int(ws.query_params.get("tw", 400))
    th = int(ws.query_params.get("th", 400))

    cap = cv2.VideoCapture(config.CAMERA_URLS["test"])
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.05)
                continue

            # 추론은 별도 스레드에서 실행
            event = await asyncio.to_thread(arrow_service.detect, frame)

            if event["type"] == "hit" and arrow_service.target_polygon is not None:
                M, dst_pts = get_perspective_transform(
                    arrow_service.target_polygon, tw, th
                )
                corrected_hit = transform_points([event["hit_tip"]], M)[0]
                event["corrected_hit"] = corrected_hit

                await ws.send_json(event)

            await asyncio.sleep(0.05)
    finally:
        cap.release()


