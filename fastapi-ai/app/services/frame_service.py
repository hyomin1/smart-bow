import cv2, threading, time, platform

class FrameManager:
    def __init__(self, source, name,reconnect_interval=10.0):
        self.source = source
        self.name = name
        self.cap = None
        self.latest_frame = None
        self.frame_count = 0
        self.running = True
        self.reconnect_interval = reconnect_interval
        self.last_reconnect_time = 0
        self._open_capture()
        self.thread = threading.Thread(target=self._reader,daemon=True)
        self.thread.start()

    def _open_capture(self):
        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(self.source,cv2.CAP_FFMPEG)
     
        self.last_reconnect_time = time.time()
        print(f"[INFO] {self.name}: 카메라 연결 시도")
    
    def _reader(self):
        prev_time = time.time()
        frame_count = 0
        while self.running:
            if not self.cap or not self.cap.isOpened():
                now = time.time()
                if now - self.last_reconnect_time > self.reconnect_interval:
                    print(f"[WARN] {self.name}: 스트림 끊김 -> 재연결 시도")
                    self._open_capture()
                time.sleep(1)
                continue
        
            ret, frame = self.cap.read()
            if ret:
                self.latest_frame = frame
                self.frame_count += 1
              

                now = time.time()
                if now - prev_time >= 1.0:
                    prev_time = now
            else:
                print(f"[WARN] {self.name}: 프레임 읽기 실패")
                time.sleep(0.1)
    def get_frame(self):
        if self.latest_frame is None:
            return None
    
        frame = self.latest_frame
        if self.name == "target3":
            h, w = frame.shape[:2]
            x_cut_left = 310
            x_cut_right = 300
            frame = frame[:, x_cut_left:w - x_cut_right]
        
        elif self.name == "shooter1":
            h, w = frame.shape[:2]
            y_cut_top = 350
            y_cut_bottom = 200
            x_cut_left = 420
            x_cut_right = 500
            frame = frame[y_cut_top:h - y_cut_bottom, x_cut_left:w - x_cut_right]

        return frame
    
    def stop(self):
        self.running = False
        self.cap.release()

