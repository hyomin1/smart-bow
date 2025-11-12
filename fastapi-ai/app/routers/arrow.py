import asyncio, cv2
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from app.models.person_model import PersonModel
from app.utils.transform import get_perspective_transform, transform_points
from app.services.registry import registry
from app.services.arrow_registry import arrow_registry
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

router = APIRouter()
person_model = PersonModel()

# cam_id별 연결된 클라이언트 세션 저장
connected_clients: dict[str, set[WebSocket]] = {}
# cam_id별 detect loop task
detect_tasks: dict[str, asyncio.Task] = {}


async def broadcast(cam_id: str, event: dict):
    """cam_id에 연결된 모든 세션에 이벤트 전송"""
    dead = []
    for ws in connected_clients.get(cam_id, set()):
        try:
            # if event["type"] == "hit" and arrow_service.target_polygon is not None:
            #     M, _ = get_perspective_transform(arrow_service.target_polygon, tw, th)
            #     corrected_hit = transform_points([event["tip"]], M)[0]
            #     event_to_send["tip"] = corrected_hit
            #     print(f"[broadcast] 원근 변환 적용: {corrected_hit}")
            await ws.send_json(event)
        except Exception:
            dead.append(ws)

    # 끊긴 세션 제거
    for item in dead:
        connected_clients[cam_id].remove(item)


async def detect_loop(cam_id: str, frame_manager):
    """cam_id별 화살/사람 탐지 루프"""
    arrow_service = arrow_registry.get(cam_id)
    loop = asyncio.get_running_loop()

    last_frame_id = None
    polygon_sent = False
    try:
        while True:
            frame = frame_manager.get_frame()
            if frame is None:
                await asyncio.sleep(0.016)
                continue
            frame_id = id(frame)
            if frame_id == last_frame_id:
                await asyncio.sleep(0)
                continue

            # 화살 탐지
            event = await loop.run_in_executor(
                executor, arrow_service.detect, frame, True
            )

            if not polygon_sent and arrow_service.target_polygon is not None:
                h, w = frame.shape[:2]
                polygon_data = arrow_service.target_polygon.tolist()
                await broadcast(
                    cam_id,
                    {
                        "type": "polygon",
                        "points": polygon_data,
                        "frame_size": [w, h],
                    },
                )
                polygon_sent = True  # 다시 안 보내도록 설정
                print(f"[{cam_id}] polygon 전송 완료 ({w}x{h})")

            if not event:
                continue
            if event["type"] == "arrow" and event["tip"] is None:
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

    except Exception as e:
        print(f"[{cam_id}] detect loop 에러: {e}")


@router.websocket("/hit/{cam_id}")
async def arrow_ws(ws: WebSocket, cam_id: str):
    await ws.accept()

    frame_manager = registry.get_camera(cam_id)
    if not frame_manager:
        await ws.send_json({"error": f"Camera {cam_id} not found"})
        await ws.close()
        return

    # cam_id별 세션 관리
    if cam_id not in connected_clients:
        connected_clients[cam_id] = set()
    connected_clients[cam_id].add(ws)

    frame = frame_manager.get_frame()
    arrow_service = arrow_registry.get(cam_id)

    if frame is not None and arrow_service and arrow_service.target_polygon is not None:
        h, w = frame.shape[:2]
        polygon_data = arrow_service.target_polygon.tolist()
        await ws.send_json(
            {
                "type": "polygon",
                "points": polygon_data,
                "frame_size": [w, h],
            }
        )
        print(f"[{cam_id}] polygon 전송 완료 ({len(polygon_data)} pts, frame {w}x{h})")

    # detect loop이 없으면 새로 시작
    if cam_id not in detect_tasks:
        detect_tasks[cam_id] = asyncio.create_task(detect_loop(cam_id, frame_manager))

    try:
        # 연결이 살아있는 동안 유지
        while True:
            await asyncio.sleep(3600)
    except WebSocketDisconnect:
        connected_clients[cam_id].remove(ws)
        print(f"[{cam_id}] 클라이언트 연결 끊김")
    finally:
        print(f"[{cam_id}] 세션 종료")
