import cv2
import threading
import queue
import time
from app.core import config

frame_queue = queue.Queue(maxsize=10)

def receive_frames():
    cap = cv2.VideoCapture(config.CAMERA_URLS["test"], cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise RuntimeError("카메라 열기 실패")

    # 스트림에서 제공하는 FPS 
    stream_fps = cap.get(cv2.CAP_PROP_FPS)
    #print(f"[INFO] 카메라가 보고한 스트림 FPS: {stream_fps:.2f}")

    frame_count = 0
    start_time = time.time()
    interval = 10  

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_count += 1
        elapsed_time = time.time() - start_time

        # 10초마다 실제 처리 FPS 계산
        if elapsed_time >= interval:
            process_fps = frame_count / elapsed_time
            #print(f"[INFO] 최근 {interval}초간 평균 처리 FPS: {process_fps:.2f}")
            frame_count = 0
            start_time = time.time()

        if frame_queue.full():
            try:
                frame_queue.get_nowait()
            except queue.Empty:
                pass

        frame_queue.put(frame)

def start_receiver():
    thread = threading.Thread(target=receive_frames, daemon=True)
    thread.start()
