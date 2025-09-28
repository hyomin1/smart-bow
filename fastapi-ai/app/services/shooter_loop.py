import asyncio
from app.services.shooter_registry import shooter_registry

detect_tasks: dict[str, asyncio.Task] = {}

async def shooter_loop(cam_id, frame_manager):
    shooter_service = shooter_registry.get(cam_id)
    try:
        while True:
            frame = frame_manager.get_frame()
            if frame is None:
                await asyncio.sleep(0.05)
                continue

            # 별도 스레드에서 추론 실행
            await asyncio.to_thread(shooter_service.detect, frame)

            await asyncio.sleep(0.05)
    except Exception as e:
        print(f"[{cam_id}] shooter loop 에러: {e}")
