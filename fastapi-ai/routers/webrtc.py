from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription

from services.webrtc.frame_subscriber import camera_frame_sub
from services.webrtc.video_track import CameraVideoTrack
from services.arrow.registry import arrow_registry
from services.person.registry import person_registry

from config import CAMERA_PORTS
import asyncio, logging

logger = logging.getLogger("smartbow.webrtc")

router = APIRouter()
pcs = set()
subscribers = {}


@router.post("/offer/{cam_id}")
async def offer(cam_id: str, request: Request):
    try:
        if cam_id not in CAMERA_PORTS:
            logger.warning(f"알 수 없는 카메라 ID 요청: {cam_id}")
            return JSONResponse(
                {"detail": f"Unknown camera id: {cam_id}"}, status_code=404
            )

        try:
            params = await request.json()
            offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        except KeyError as e:
            logger.error(f"잘못된 요청 형식 - 카메라: {cam_id}, 누락된 필드: {e}")
            return JSONResponse(
                {"detail": f"Missing required field: {e}"}, status_code=400
            )
        except Exception as e:
            logger.error(f"요청 파싱 실패 - 카메라: {cam_id}, 오류: {e}")
            return JSONResponse({"detail": "Invalid request format"}, status_code=400)

        pc = RTCPeerConnection()
        pcs.add(pc)

        arrow_service = arrow_registry.get(cam_id)
        person_service = person_registry.get(cam_id)
        video_track = CameraVideoTrack(arrow_service, person_service)

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            state = pc.connectionState
            logger.info(f"연결 상태 변경 - 카메라: {cam_id}, 상태: {state}")

            if state in ["failed", "closed"]:
                pcs.discard(pc)
                logger.info(
                    f"PeerConnection 제거 - 카메라: {cam_id} (남은 연결: {len(pcs)}개)"
                )

                if (
                    cam_id in subscribers
                    and video_track in subscribers[cam_id]["tracks"]
                ):
                    subscribers[cam_id]["tracks"].discard(video_track)
                    logger.info(
                        f"[{cam_id}] 트랙 제거, 남은 트랙: {len(subscribers[cam_id]['tracks'])}"
                    )

                    if not subscribers[cam_id]["tracks"]:
                        try:
                            subscribers[cam_id]["task"].cancel()
                            del subscribers[cam_id]
                            logger.info(f"구독자 작업 취소 완료 - 카메라: {cam_id}")
                        except Exception as e:
                            logger.error(
                                f"구독자 정리 실패 - 카메라: {cam_id}, 오류: {e}"
                            )

        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            logger.debug(
                f"ICE 연결 상태 - 카메라: {cam_id}, 상태: {pc.iceConnectionState}"
            )

        try:
            pc.addTrack(video_track)
            logger.debug(f"비디오 트랙 추가 완료 - 카메라: {cam_id}")
        except Exception as e:
            logger.error(f"트랙 추가 실패 - 카메라: {cam_id}, 오류: {e}")
            raise

        port = CAMERA_PORTS[cam_id]

        if cam_id not in subscribers:
            tracks = {video_track}
            try:
                task = asyncio.create_task(camera_frame_sub(tracks, [port]))
                subscribers[cam_id] = {"task": task, "tracks": tracks}
                logger.info(f"새 구독자 생성 - 카메라: {cam_id}, 포트: {port}")
            except Exception as e:
                logger.error(f"구독자 생성 실패 - 카메라: {cam_id}, 오류: {e}")
                pcs.discard(pc)
                raise
        else:
            subscribers[cam_id]["tracks"].add(video_track)
            logger.info(
                f"구독자에 트랙 추가 완료 - 카메라: {cam_id}, 총 트랙: {len(subscribers[cam_id]['tracks'])}"
            )

        try:
            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            logger.info(f"WebRTC 협상 완료 - 카메라: {cam_id}")
        except Exception as e:
            logger.error(
                f"WebRTC 협상 실패 - 카메라: {cam_id}, 오류: {e}", exc_info=True
            )
            pcs.discard(pc)
            if cam_id in subscribers and video_track in subscribers[cam_id]["tracks"]:
                subscribers[cam_id]["tracks"].discard(video_track)
            raise
        return {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type,
        }
    except JSONResponse as e:
        raise
    except Exception as e:
        logger.error(f"예상치 못한 오류 - 카메라: {cam_id}, 오류: {e}", exc_info=True)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


@router.on_event("shutdown")
async def on_shutdown():
    """앱 종료 시 정리"""
    logger.info("=" * 60)
    logger.info("WebRTC 서비스 종료 시작")
    logger.info("=" * 60)

    if subscribers:
        logger.info(f"구독자 정리 중... (총 {len(subscribers)}개)")
        for cam_id, sub_info in list(subscribers.items()):
            try:
                sub_info["task"].cancel()
                logger.info(f"  ✓ 구독자 취소 완료 - 카메라: {cam_id}")
            except Exception as e:
                logger.error(f"  ✗ 구독자 취소 실패 - 카메라: {cam_id}, 오류: {e}")
        subscribers.clear()
    else:
        logger.info("정리할 구독자 없음")

    if pcs:
        logger.info(f"PeerConnection 종료 중... (총 {len(pcs)}개)")
        try:
            coros = [pc.close() for pc in pcs]
            await asyncio.gather(*coros, return_exceptions=True)
            pcs.clear()
            logger.info("  ✓ 모든 PeerConnection 종료 완료")
        except Exception as e:
            logger.error(f"  ✗ PeerConnection 종료 중 오류: {e}")
    else:
        logger.info("종료할 PeerConnection 없음")

    logger.info("=" * 60)
    logger.info("WebRTC 서비스 종료 완료")
    logger.info("=" * 60)
