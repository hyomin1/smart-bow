from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.target_service import get_target_for_front, get_target_raw

import cv2
import app.config as config

router = APIRouter()


@router.get("/target-corners")
def target_corners():
    cap = cv2.VideoCapture(config.VIDEO_SOURCE)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return JSONResponse(status_code=404, content={"message": "Frame not found"})
    corners = get_target_raw(frame)
    return {"corners": corners}
