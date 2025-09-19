import os
from dotenv import load_dotenv

load_dotenv()


CAMERA_URLS = {
    #"target1": os.getenv("CAM1_URL"),
    "target2": os.getenv("CAM2_URL"),
    #"target3": os.getenv("CAM3_URL"),
    "shooter1": os.getenv("SHOOTER1_URL"),
    # "shooter2" : os.getenv("SHOOTER2_URL"),
    #"test": os.getenv("TEST")
}

ALLOW_ORIGINS=os.getenv("ALLOW_ORIGINS").split(",")