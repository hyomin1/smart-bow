import os
from dotenv import load_dotenv

load_dotenv()

TARGET1_INFER_PORT = 5561
TARGET2_INFER_PORT = 5562
TARGET3_INFER_PORT = 5563
TARGET_TEST_INFER_PORT = 5564

SHOOTER1_INFER_PORT = 5565
SHOOTER2_INFER_PORT = 5566

ARROW_INFER_CONFIG = {
    "target1": {"id": "target1", "infer_port": TARGET1_INFER_PORT},
    "target2": {"id": "target2", "infer_port": TARGET2_INFER_PORT},
    "target3": {"id": "target3", "infer_port": TARGET3_INFER_PORT},
    "target-test": {"id": "target-test", "infer_port": TARGET_TEST_INFER_PORT},
    # "shooter1": {"id": "shooter1", "infer_port": SHOOTER1_INFER_PORT},
    # "shooter2": {"id": "shooter2", "infer_port": SHOOTER2_INFER_PORT},
}
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS").split(",")
