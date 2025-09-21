import asyncio
from fastapi import APIRouter, WebSocket
from app.services.arrow_service import arrow_service
from app.models.person_model import PersonModel
from app.utils.transform import get_perspective_transform, transform_points
from app.services.registry import registry
from starlette.websockets import WebSocketDisconnect

router = APIRouter()

person_model = PersonModel()

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
            
            if event['type'] == 'hit':
                person_results = await asyncio.to_thread(person_model.predict, frame)
                if len(person_results.boxes) > 0:
                    await ws.send_json({"type": "person"})
                    print("사람 감지됨, 화살 탐지 중단")
                    await asyncio.sleep(30)  # 30초 중단
                    continue

            if event["type"] == "hit" and arrow_service.target_polygon is not None:
                M, dst_pts = get_perspective_transform(
                    arrow_service.target_polygon, tw, th
                )
                corrected_hit = transform_points([event["hit_tip"]], M)[0]
                event["corrected_hit"] = corrected_hit
                print("hit 전송")
                await ws.send_json(event)

            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        print("클라이언트 연결 끊김")
    except Exception as e:
        print(f"Websocket 에러: {e}")
    finally:
        print("세션 종료")
