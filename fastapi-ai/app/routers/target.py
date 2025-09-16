from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.services.target_service import TargetService
from app.utils.transform import get_perspective_transform, transform_points
from app.core import config
from app.frame_manager import frame_queue

from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import time


router = APIRouter()
target_service = TargetService()

@router.get("/target-corners")
def target_corners(tw: int = Query(...), th: int = Query(...)):
    frame = None
    src_pts = None

  
    for _ in range(50):
        if not frame_queue.empty():
            frame = frame_queue.get()
            src_pts = target_service.get_target_raw(frame)

            if src_pts:
              
                M, dst_pts = get_perspective_transform(src_pts, tw, th)
                corners = transform_points(src_pts, M)
                return {"corners": corners}

        time.sleep(0.1)  

  
    return {"corners": []}




# 새벽 작업용
@router.get("/test")
def target_overlay():
    def gen_frames():
        while True:
            if frame_queue.empty():
                continue

            frame = frame_queue.get()
            src_pts = target_service.get_target_raw(frame)

            if src_pts and len(src_pts) >= 4:
                pts = np.array(src_pts, np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=3)
                for (x, y) in src_pts:
                    cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)

                tw, th = 400, 534  # 국궁 과녁 비율 (2.0m : 2.67m)
                M, dst_pts = get_perspective_transform(src_pts, tw, th)
                warped = cv2.warpPerspective(frame, M, (tw, th))

                frame = np.hstack([
                    frame, cv2.resize(warped, (frame.shape[1], frame.shape[0]))
                ])

            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )

    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace;boundary=frame")
