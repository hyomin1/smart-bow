from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import time

from app.routers import target, ws  
from app.models.yolo_arrow import get_arrow_model
import app.config as config
from app.services.arrow_service import ArrowService
from app.services.target_service import get_target_info
from app.models.yolo_arrow import get_arrow_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(target.router, prefix="/target", tags=["target"])
app.include_router(ws.router, tags=["websocket"])  

@app.get("/")
async def root():
    return {"message": "Hello World"}

# ===== 화살 검출 서비스 준비 =====
arrow_model = get_arrow_model()

def gen_frames():
    cap = cv2.VideoCapture(config.VIDEO_SOURCE)

    # 최초 1회 과녁 검출 (보정은 프론트에서 하므로 target_info만 유지)
    ok, frame = cap.read()
    target_info = get_target_info(frame) if ok else None

    while True:
        success, frame = cap.read()
        if not success:
            break

        result = arrow_model.predict(frame,verbose=False,conf=0.36)

        for box in result[0].boxes:
                    # 좌표
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    
            # 박스 확장 (예: 10픽셀씩 키우기)
            pad = 10
            x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
            x2, y2 = x2 + pad, y2 + pad

                    # 박스 그리기 (두께 4)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

                    # confidence 표시
            conf = float(box.conf[0]) if box.conf is not None else 0
            label = f"{conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        # JPEG 인코딩
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

@app.get("/monitor")
async def monitor():
    """
    카메라 스트리밍 + 화살 tip/명중 오버레이 확인용
    """
    return StreamingResponse(gen_frames(),
                             media_type="multipart/x-mixed-replace; boundary=frame")
