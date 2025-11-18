import asyncio, json
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from arrow_registry import arrow_registry

router = APIRouter()

connected_clients: dict[str, set[WebSocket]] = {}


async def broadcast(cam_id: str, event: dict):
    dead = []
    for ws in connected_clients.get(cam_id, set()):
        try:
            await ws.send_json(event)
        except:
            dead.append(ws)

    for ws in dead:
        connected_clients[cam_id].remove(ws)


async def send_polygon(ws: WebSocket, cam_id: str):
    arrow_service = arrow_registry.get(cam_id)
    if arrow_service is None:
        return

    render_polygon = arrow_service.polygon_to_render()

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
        connected_clients[cam_id] = set()
    connected_clients[cam_id].add(ws)

    print(f"[WS:{cam_id}] client connected")

    try:
        while True:
            msg = await ws.receive_json()
            msg_type = msg.get("type")

            if msg_type == "video_size":
                width = msg["width"]
                height = msg["height"]

                arrow_service = arrow_registry.get(cam_id)
                if arrow_service:
                    arrow_service.video_rect = (width, height)

                    await send_polygon(ws, cam_id)

                continue

    except WebSocketDisconnect:
        connected_clients[cam_id].remove(ws)
        print(f"[WS:{cam_id}] disconnect")
