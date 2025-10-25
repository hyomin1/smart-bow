from ultralytics import YOLO

model = YOLO("weights/arrow_best.pt")

print("변환 시작... 5~10분 걸립니다")

model.export(
    format="engine",
    opset=18,  # ONNX 호환성 (11~17 가능)
    dynamic=False,  # ✅ 핵심 옵션 — 입력 크기 자유롭게
    simplify=True,  # 그래프 단순화
    half=False,
    device=0,
    workspace=4,
)

print("완료!")
