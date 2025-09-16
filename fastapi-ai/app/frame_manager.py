import cv2
import threading
import queue
from app.core import config


frame_queue = queue.Queue(maxsize=10)

def receive_frames():
    cap = cv2.VideoCapture(config.CAMERA_URLS["cam2"], cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise RuntimeError("카메라 열기 실패")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        if frame_queue.full():
            try:
                frame_queue.get_nowait() 
            except queue.Empty:
                pass

        frame_queue.put(frame)

def start_receiver():
    thread = threading.Thread(target=receive_frames, daemon=True)
    thread.start()
