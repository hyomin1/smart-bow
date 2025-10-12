from ultralytics import YOLO
import torch
import os

class ArrowModel:
    def __init__(self):
        onnx_path = "weights/arrow_best.onnx"
        pt_path = "weights/arrow_best.pt"
        
        if os.path.exists(onnx_path):
            print("🚀 ONNX 모델 사용 (최적화)")
            self.model = YOLO(onnx_path, task='detect')
        else:
            print("⚠️  일반 .pt 모델 사용")
            self.model = YOLO(pt_path)
            self.model.fuse()
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"화살모델 device: {self.device}")
        
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        
        if not os.path.exists(onnx_path):
            self.model.to(self.device)
        
        # 설정 캐싱
        self.imgsz = 640
        self.conf = 0.36
        self.iou = 0.6  # 0.5 → 0.6 (NMS 빠르게)
    
    def predict(self, frame):
        return self.model.predict(
            frame, 
            conf=self.conf, 
            iou=self.iou,
            verbose=False,
            max_det=1,
            agnostic_nms=True,
            device=self.device,
            stream=False,
        )[0]
    
    
        
        