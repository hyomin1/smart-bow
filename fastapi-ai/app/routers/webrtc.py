from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription
from app.services.shooter_loop import shooter_loop, detect_tasks as shooter_detect_tasks
from app.services.video_service import  CameraVideoTrack
from app.services.registry import registry

import asyncio

router = APIRouter()
pcs = set() 

@router.post("/offer/{cam_id}")
async def offer(cam_id,request: Request):
    frame_manager = registry.get_camera(cam_id)
    if not frame_manager:
        return JSONResponse({"detail": "카메라를 찾을 수 없습니다."}, status_code=404)
    
    if cam_id.startswith("shooter") and cam_id not in shooter_detect_tasks:
        shooter_detect_tasks[cam_id] = asyncio.create_task(shooter_loop(cam_id, frame_manager))

    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    pc.addTrack(CameraVideoTrack(frame_manager, cam_id))
    

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return JSONResponse(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )
