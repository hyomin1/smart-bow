from ultralytics import YOLO

model = YOLO("weights/arrow_best.pt")

print("변환 시작... 5~10분 걸립니다")

model.export(
    format="onnx",
    opset=12,       # ONNX 호환성 (11~17 가능)
    dynamic=True,   # ✅ 핵심 옵션 — 입력 크기 자유롭게
    simplify=True,  # 그래프 단순화
    half=False,     # GTX1650은 half 권장X (Tensor Core 없음)
    device=0
)

print("완료!")