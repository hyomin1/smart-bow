import cv2, threading, time, platform

class FrameManager:
    def __init__(self, source, name,reconnect_interval=10.0):
        self.source = source
        self.name = name
        self.cap = None
        self.latest_frame = None
        self.running = True
        self.reconnect_interval = reconnect_interval
        self.last_reconnect_time = 0
        self._open_capture()
        self.thread = threading.Thread(target=self._reader,daemon=True)
        self.thread.start()

    def _open_capture(self):
        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(self.source)
     
        self.last_reconnect_time = time.time()
        print(f"[INFO] {self.name}: 카메라 연결 시도")
    
    def _reader(self):
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
            else:
                print(f"[WARN] {self.name}: 프레임 읽기 실패")
                time.sleep(0.1)
    def get_frame(self):
        return self.latest_frame
    
    def stop(self):
        self.running = False
        self.cap.release()