import asyncio, json
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from services.arrow.registry import arrow_registry

router = APIRouter()

connected_clients: dict[str, dict[WebSocket, dict]] = {}


async def broadcast(cam_id: str, event: dict):
    clients = connected_clients.get(cam_id, {})
    if not clients:
        return

    if event.get("type") != "hit":
        return

    arrow_service = arrow_registry.get(cam_id)

    if not arrow_service:
        return
    raw_x, raw_y = event["tip"]

    for ws, info in list(clients.items()):
        video_size = info.get("video_size")

        if video_size is None:
            continue

        render_tip = arrow_service.to_render_coords(raw_x, raw_y, video_size)

        payload = {"type": "hit", "tip": render_tip}

        try:
            await ws.send_json(payload)
        except Exception:
            if ws in clients:
                del clients[ws]


async def send_polygon(ws: WebSocket, cam_id: str, video_size=None):
    arrow_service = arrow_registry.get(cam_id)
    if arrow_service is None:
        return

    render_polygon = arrow_service.polygon_to_render(video_size)

    if render_polygon is None:

        return

    await ws.send_json(
        {
            "type": "polygon",
            "points": render_polygon,
        }
    )


@router.websocket("/hit/{cam_id}")
async def hit_ws(ws: WebSocket, cam_id: str):
    await ws.accept()

    if cam_id not in connected_clients:
        connected_clients[cam_id] = {}
    connected_clients[cam_id][ws] = {"video_size": None}

    print(f"[WS:{cam_id}] Client connected (total: {len(connected_clients[cam_id])})")

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
        if ws in connected_clients[cam_id]:
            del connected_clients[cam_id][ws]

        print(
            f"[WS:{cam_id}] Client disconnected (remaining: {len(connected_clients[cam_id])})"
        )
