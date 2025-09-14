from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.services.target_service import TargetService
from app.utils.transform import get_perspective_transform, transform_points
from app.core import config


from fastapi.responses import StreamingResponse
import cv2
import numpy as np

router = APIRouter()
# 밤에 카메라 끌땐 test로 평소엔 cam2로 작업
target_service = TargetService(config.CAMERA_URLS["test"])

@router.get("/target-corners")
def target_corners(tw=Query(),th=Query()):
    
    frame = target_service.get_frame()
    if frame is None:
        return JSONResponse(status_code=404, content={"message": "Frame not found"})
 
    src_pts = target_service.get_target_raw(frame)
    if not src_pts:
        return JSONResponse(status_code=404, content={"message": "Target not found"})
    
    M, dst_pts = get_perspective_transform(src_pts,tw,th)
    corners = transform_points(src_pts, M)
    return {"corners": corners}




# 새벽 작업용
@router.get("/test")
def target_overlay():
    def gen_frames():
        while True:
            frame = target_service.get_frame()
            if frame is None:
                continue

            src_pts = target_service.get_target_raw(frame)
            if src_pts and len(src_pts) >= 4:
                # ---- 원본에 검출된 폴리곤 표시 ----
                pts = np.array(src_pts, np.int32).reshape((-1, 1, 2))
                print(src_pts)
                cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=3)
                for (x, y) in src_pts:
                    cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)

                # ---- 보정된 프레임 생성 ----
                tw, th = 400, 534  # 국궁 과녁 비율 (2.0m : 2.67m)
                M, dst_pts = get_perspective_transform(src_pts, tw, th)
                warped = cv2.warpPerspective(frame, M, (tw, th))

                # ---- 원본과 보정 프레임을 나란히 붙임 ----
                frame = np.hstack([frame, cv2.resize(warped, (frame.shape[1], frame.shape[0]))])

            # --- JPEG 인코딩 ---
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )

    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace;boundary=frame")
