import os
from dotenv import load_dotenv

load_dotenv()

VIDEO_SOURCE = os.getenv("VIDEO_SOURCE", "output.mp4")
