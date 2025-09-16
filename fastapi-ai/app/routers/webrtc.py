import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription

from app.services.video_track import ArrowVideoTrack

router = APIRouter()
pcs = set() 


@router.post("/offer")
async def offer(request: Request):
    
    params = await request.json()

    # 브라우저에서 온 offer
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    # WebRTC 연결 생성 
    pc = RTCPeerConnection()

    pcs.add(pc)

    pc.addTrack(ArrowVideoTrack())

    # 클라 → 서버 오퍼 등록
    await pc.setRemoteDescription(offer)

    # 서버 → 클라 답변 생성
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return JSONResponse(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )
