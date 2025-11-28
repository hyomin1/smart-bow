from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from subscriber import start_subscriber_thread
from config import ARROW_INFER_CONFIG, PERSON_INFER_CONFIG, ALLOW_ORIGINS, LOG_DIR
from services.arrow.registry import arrow_registry
from services.person.registry import person_registry
from routers import webrtc, ws
from datetime import datetime


import time, threading, asyncio
import logging.config, yaml
import os

os.makedirs(LOG_DIR, exist_ok=True)

try:
    with open("logging.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

        today = datetime.now().strftime("%Y-%m-%d")

        config["handlers"]["file_handler"]["filename"] = f"{LOG_DIR}/{today}.log"
        logging.config.dictConfig(config)
except FileNotFoundError:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
except Exception as e:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("smartbow")


def on_arrow_event(cam_id, event):
    arrow_service = arrow_registry.get(cam_id)
    if arrow_service is None:
        logger.warning(f"화살 서비스를 찾을 수 없음 - 카메라 ID: {cam_id}")
        return

    arrow_service.add_event(event)


def on_person_event(cam_id, event):
    person_service = person_registry.get(cam_id)
    if person_service is None:
        logger.warning(f"사람 감지 서비스를 찾을 수 없음 - 카메라 ID: {cam_id}")
        return

    person_service.set_zoom_area(event["bbox"])


def idle_watcher():
    """화살 적중 감지 백그라운드 워커"""
    logger.info("화살 적중 감지 스레드 시작")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            for cam_id, arrow_service in list(arrow_registry.items()):
                try:
                    if arrow_service.is_idle():
                        hit = arrow_service.find_hit_point()
                        if hit is not None:

                            arrow_service.last_hit_time = time.time()

                            try:
                                arrow_service.visualize_buffer(hit)
                            except Exception as e:
                                logger.error(
                                    f"버퍼 시각화 실패 - 카메라: {cam_id}, 오류: {e}"
                                )

                            loop.run_until_complete(
                                ws.broadcast(cam_id, {"type": "hit", "tip": hit})
                            )

                        arrow_service.clear_buffer()
                except Exception as e:
                    logger.error(
                        f"화살 적중 처리 중 오류 발생 - 카메라: {cam_id}, 오류: {e}",
                        exc_info=True,
                    )

            time.sleep(0.1)
        except Exception as e:
            logger.critical(f"화살 감지 워커 오류: {e}", exc_info=True)
            time.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("SmartBow 서버 시작 중...")
    logger.info("=" * 60)

    logger.info(f"화살 추론 서비스 초기화 시작 (총 {len(ARROW_INFER_CONFIG)} 개)")
    for cam_key, config in ARROW_INFER_CONFIG.items():
        cam_id = config["id"]
        port = config["infer_port"]

        try:
            logger.info(f"  → 카메라 연결 시도: {cam_id} (포트: {port})")
            start_subscriber_thread(port, cam_id, on_arrow_event)
            logger.info(f"  ✓ 카메라 연결 성공: {cam_id}")
        except Exception as e:
            logger.error(f"  ✗ 카메라 연결 실패: {cam_id} - {e}")

    # logger.info(f"사람 감지 서비스 초기화 시작 (총 {len(PERSON_INFER_CONFIG)}개)")
    # for cam_key, config in PERSON_INFER_CONFIG.items():
    #     cam_id = config["id"]
    #     port = config["infer_port"]
    #     try:
    #         logger.info(f"  → 카메라 연결 시도: {cam_id} (포트: {port})")
    #         start_subscriber_thread(port, cam_id, on_person_event)
    #         logger.info(f"  ✓ 카메라 연결 성공: {cam_id}")
    #     except Exception as e:
    #         logger.error(f"  ✗ 카메라 연결 실패: {cam_id} - {e}")

    t = threading.Thread(target=idle_watcher, daemon=True)
    t.start()
    logger.info("백그라운드 워커 시작 완료")

    logger.info("=" * 60)
    logger.info("SmartBow 서버 시작 완료!")
    logger.info("=" * 60)

    yield

    logger.info("=" * 60)
    logger.info("SmartBow 서버 종료 중...")
    logger.info("=" * 60)


app = FastAPI(
    title="SmartBow",
    version="1.0.0",
    description="스마트 국궁 시스템 - WebRTC 시그널링 및 이벤트 서버",
    lifespan=lifespan,
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


@app.get("/")
def root():
    return {"status": "ok"}
