import asyncio
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from app.models.person_model import PersonModel
from app.utils.transform import get_perspective_transform, transform_points
from app.services.registry import registry
from app.services.arrow_registry import arrow_registry


router = APIRouter()
person_model = PersonModel()

# cam_id별 연결된 클라이언트 세션 저장 (ws, tw, th)
connected_clients: dict[str, set[tuple[WebSocket, int, int]]] = {}
# cam_id별 detect loop task
detect_tasks: dict[str, asyncio.Task] = {}


async def broadcast(cam_id: str, event: dict):
    """cam_id에 연결된 모든 세션에 이벤트 전송"""

    dead = []
    arrow_service = arrow_registry.get(cam_id)
    for ws, tw, th in connected_clients.get(cam_id, set()):
        try:
            event_to_send = dict(event)  # 원본 복사
            if event["type"] == "hit" and arrow_service.target_polygon is not None:
                M, _ = get_perspective_transform(arrow_service.target_polygon, tw, th)
                corrected_hit = transform_points([event["hit_tip"]], M)[0]
                event_to_send["corrected_hit"] = corrected_hit
            await ws.send_json(event_to_send)
        except Exception:
            dead.append((ws, tw, th))

    # 끊긴 세션 제거
    for item in dead:
        connected_clients[cam_id].remove(item)


async def detect_loop(cam_id: str, frame_manager):
    """cam_id별 화살/사람 탐지 루프"""
    arrow_service = arrow_registry.get(cam_id)
    try:
        while True:
            frame = frame_manager.get_frame()
            if frame is None:
                await asyncio.sleep(0.05)
                continue

            # 화살 탐지
            event = await asyncio.to_thread(arrow_service.detect, frame, with_hit=True)
            if event is None:
                await asyncio.sleep(0.05)
                continue

            if event["type"] == "hit":
                person_results = await asyncio.to_thread(person_model.predict, frame)
                if len(person_results.boxes) > 0:
                    await broadcast(cam_id, {"type": "person"})
                    print(f"[{cam_id}] 사람 감지됨, 화살 탐지 중단")
                    await asyncio.sleep(30)
                    continue

            # hit 이벤트 전송
            await broadcast(cam_id, event)
            if event["type"] == "hit":
                print(f"[{cam_id}] hit 전송")

            await asyncio.sleep(0.05)
    except Exception as e:
        print(f"[{cam_id}] detect loop 에러: {e}")


@router.websocket("/hit/{cam_id}")
async def arrow_ws(ws: WebSocket, cam_id: str):
    await ws.accept()

    tw = int(ws.query_params.get("tw", 400))
    th = int(ws.query_params.get("th", 400))

    frame_manager = registry.get_camera(cam_id)
    if not frame_manager:
        await ws.send_json({"error": f"Camera {cam_id} not found"})
        await ws.close()
        return

    # cam_id별 세션 관리
    if cam_id not in connected_clients:
        connected_clients[cam_id] = set()
    connected_clients[cam_id].add((ws, tw, th))

    # detect loop이 없으면 새로 시작
    if cam_id not in detect_tasks:
        detect_tasks[cam_id] = asyncio.create_task(detect_loop(cam_id, frame_manager))

    try:
        # 연결이 살아있는 동안 유지
        while True:
            await asyncio.sleep(3600)
    except WebSocketDisconnect:
        connected_clients[cam_id].remove((ws, tw, th))
        print(f"[{cam_id}] 클라이언트 연결 끊김")
    finally:
        print(f"[{cam_id}] 세션 종료")
