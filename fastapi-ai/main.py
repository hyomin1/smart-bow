from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from subscriber import start_subscriber_thread
from config import ARROW_INFER_CONFIG, ALLOW_ORIGINS
from services.arrow.registry import arrow_registry
from routers import webrtc, ws


import time, threading, asyncio

app = FastAPI(
    title="SmartBow",
    version="1.0.0",
    description="Smart Archery System — WebRTC Signaling + Event Server",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(webrtc.router, prefix="/webrtc", tags=["webrtc"])
app.include_router(ws.router, prefix="/ws", tags=["ws"])


def on_event(cam_id, event):
    arrow_service = arrow_registry.get(cam_id)
    if arrow_service is None:
        return

    arrow_service.add_event(event)


def idle_watcher():
    print("[IDLE] watcher thread started")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        for cam_id, arrow_service in arrow_registry.items():
            try:
                if arrow_service.is_idle():
                    hit = arrow_service.find_hit_point()
                    if hit is not None:
                        print(f"[HIT] cam={cam_id}, point={hit}")
                        arrow_service.last_hit_time = time.time()

                        loop.run_until_complete(
                            ws.broadcast(cam_id, {"type": "hit", "tip": hit})
                        )

                    arrow_service.clear_buffer()
            except Exception as e:
                print(f"[IDLE] Error in watcher for {cam_id}:", e)

        time.sleep(0.1)


@app.on_event("startup")
def startup_event():
    for cam_key, config in ARROW_INFER_CONFIG.items():
        cam_id = config["id"]
        port = config["infer_port"]

        start_subscriber_thread(port, cam_id, on_event)
    t = threading.Thread(target=idle_watcher, daemon=True)
    t.start()


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/buffer/{cam_id}")
def get_buffer(cam_id: str):
    """버퍼 조회 테스트용"""
    arrow_service = arrow_registry.get(cam_id)
    if arrow_service is None:
        return
    return list(arrow_service.tracking_buffer)
