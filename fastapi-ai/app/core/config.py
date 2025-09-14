import os
from dotenv import load_dotenv

load_dotenv()

#VIDEO_SOURCE = os.getenv("VIDEO_SOURCE", "output.mp4")

CAMERA_URLS = {
    "cam1": os.getenv("CAM1_URL"),
    "cam2": os.getenv("CAM2_URL"),
    "cam3": os.getenv("CAM3_URL"),
    "test": os.getenv("TEST")
}