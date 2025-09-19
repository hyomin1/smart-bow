from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription
from app.core import config

from app.services.video_service import  CameraVideoTrack
from app.services.registry import registry

router = APIRouter()
pcs = set() 

@router.post("/offer/{cam_id}")
async def offer(cam_id,request: Request):
    frame_manager = registry.get_camera(cam_id)
    if not frame_manager:
        return JSONResponse({"detail": "카메라를 찾을 수 없습니다."}, status_code=404)
    
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    pc.addTrack(CameraVideoTrack(frame_manager))

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return JSONResponse(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )
