import asyncio
from fastapi import APIRouter, WebSocket
from app.services.arrow_service import ArrowService
from app.models.person_model import PersonModel
from app.utils.transform import get_perspective_transform, transform_points
from app.frame_manager import frame_queue  
from starlette.websockets import WebSocketDisconnect

router = APIRouter()

arrow_service = ArrowService()
person_model = PersonModel()

@router.websocket("/ws/arrow")
async def arrow_ws(ws: WebSocket):
    await ws.accept()

    tw = int(ws.query_params.get("tw", 400))
    th = int(ws.query_params.get("th", 400))

    try:
        while True:
            if not frame_queue.empty():
                frame = frame_queue.get()

                person_results = await asyncio.to_thread(person_model.predict,frame)
                if len(person_results.boxes) > 0:
                    await ws.send_json({"type": "person"})
                    print('사람 감지됨, 화살 탐지 중단')
                    await asyncio.sleep(30)
                    continue

                # 추론은 별도 스레드에서 실행
                event = await asyncio.to_thread(
                    arrow_service.detect, frame, with_hit=True
                )
                if event is None:
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
        print(" 클라이언트 연결 끊김")
    except Exception as e:
        print(f"Websocket 에러: {e}" )
    finally:
        print("세션 종료")
