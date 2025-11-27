from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription

from services.webrtc.frame_subscriber import camera_frame_sub
from services.webrtc.video_track import CameraVideoTrack
from services.arrow.registry import arrow_registry
from services.person.registry import person_registry

from config import CAMERA_PORTS
import asyncio

router = APIRouter()
pcs = set()


subscribers = {}


@router.post("/offer/{cam_id}")
async def offer(cam_id: str, request: Request):
    if cam_id not in CAMERA_PORTS:
        return JSONResponse({"detail": f"Unknown camera id: {cam_id}"}, status_code=404)

    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    # 연결 상태 모니터링
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"[{cam_id}] Connection state: {pc.connectionState}")
        if pc.connectionState in ["failed", "closed"]:
            pcs.discard(pc)
            if cam_id in subscribers and video_track in subscribers[cam_id]["tracks"]:
                subscribers[cam_id]["tracks"].discard(video_track)
                print(
                    f"[{cam_id}] Track removed, remaining: {len(subscribers[cam_id]['tracks'])}"
                )

                if not subscribers[cam_id]["tracks"]:
                    subscribers[cam_id]["task"].cancel()
                    del subscribers[cam_id]
                    print(f"[{cam_id}] Subscriber task cancelled")

    arrow_service = arrow_registry.get(cam_id)
    person_service = person_registry.get(cam_id)
    video_track = CameraVideoTrack(arrow_service, person_service)
    pc.addTrack(video_track)

    port = CAMERA_PORTS[cam_id]

    if cam_id not in subscribers:
        tracks = {video_track}
        task = asyncio.create_task(camera_frame_sub(tracks, [port]))
        subscribers[cam_id] = {"task": task, "tracks": tracks}
        print(f"[ZMQ] NEW subscriber for {cam_id}")
    else:
        subscribers[cam_id]["tracks"].add(video_track)
        print(
            f"[ZMQ] Added track to existing subscriber for {cam_id}, total tracks: {len(subscribers[cam_id]['tracks'])}"
        )

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
    }


@router.on_event("shutdown")
async def on_shutdown():
    """앱 종료 시 정리"""
    # 모든 구독자 취소
    for cam_id, sub_info in subscribers.items():
        sub_info["task"].cancel()
    subscribers.clear()

    # 모든 PeerConnection 종료
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros, return_exceptions=True)
    pcs.clear()
    print("[WEBRTC] Cleanup completed")
