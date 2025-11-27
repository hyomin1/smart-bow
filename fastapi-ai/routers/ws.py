from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from services.arrow.registry import arrow_registry

import logging

logger = logging.getLogger("smartbow.ws")

router = APIRouter()

connected_clients: dict[str, dict[WebSocket, dict]] = {}


async def broadcast(cam_id: str, event: dict):
    try:

        clients = connected_clients.get(cam_id, {})
        if not clients:
            return

        if event.get("type") != "hit":
            return

        arrow_service = arrow_registry.get(cam_id)

        if not arrow_service:
            logger.warning(f"브로드캐스트 실패: ArrowService 없음 - 카메라: {cam_id}")
            return
        raw_x, raw_y = event["tip"]

        disconnected = []

        for ws, info in list(clients.items()):
            video_size = info.get("video_size")

            if video_size is None:
                continue

            render_tip = arrow_service.to_render_coords(raw_x, raw_y, video_size)

            payload = {"type": "hit", "tip": render_tip}

            try:
                await ws.send_json(payload)
            except Exception:
                logger.error(f"클라이언트 전송 실패 - 카메라: {cam_id}, 오류: {e}")
                disconnected.append(ws)

        for ws in disconnected:
            if ws in clients:
                del clients[ws]

    except Exception as e:
        logger.error(f"브로드캐스트 오류 - 카메라: {cam_id}, 오류: {e}", exc_info=True)


async def send_polygon(ws: WebSocket, cam_id: str, video_size=None):
    try:

        arrow_service = arrow_registry.get(cam_id)
        if arrow_service is None:
            logger.warning(f"폴리곤 전송 실패: ArrowService 없음 - 카메라: {cam_id}")
            return

        render_polygon = arrow_service.polygon_to_render(video_size)

        if render_polygon is None:
            logger.debug(f"폴리곤 없음 - 카메라: {cam_id}")
            return

        await ws.send_json(
            {
                "type": "polygon",
                "points": render_polygon,
            }
        )
    except Exception as e:
        logger.error(f"폴리곤 전송 실패 - 카메라: {cam_id}, 오류: {e}", exc_info=True)


@router.websocket("/hit/{cam_id}")
async def hit_ws(ws: WebSocket, cam_id: str):
    await ws.accept()

    if cam_id not in connected_clients:
        connected_clients[cam_id] = {}
    connected_clients[cam_id][ws] = {"video_size": None}

    logger.info(
        f"WebSocket 연결 - 카메라: {cam_id} (총 {len(connected_clients[cam_id])}개)"
    )
    try:
        while True:
            msg = await ws.receive_json()
            msg_type = msg.get("type")

            if msg_type == "video_size":
                width = msg["width"]
                height = msg["height"]

                if ws in connected_clients[cam_id]:
                    connected_clients[cam_id][ws]["video_size"] = (width, height)

                await send_polygon(ws, cam_id, (width, height))
                continue

    except WebSocketDisconnect:
        if cam_id in connected_clients and ws in connected_clients[cam_id]:
            del connected_clients[cam_id][ws]

    except Exception as e:
        logger.error(f"WebSocket 오류 - 카메라: {cam_id}, 오류: {e}", exc_info=True)
        if cam_id in connected_clients and ws in connected_clients[cam_id]:
            del connected_clients[cam_id][ws]
