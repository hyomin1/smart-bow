
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import subprocess

import asyncio  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 개발 단계에서는 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.websocket("/ws/coords")
async def coords_ws(ws:WebSocket):
    await ws.accept()
    x = 1
    y = 2
    while True:
        coords = {"x": x, "y": y}
        await ws.send_json(coords)
        x+=1
        y+=1
        await asyncio.sleep(1)



@app.get("/stream.ts")
def stream_video():
    cmd = [
    "ffmpeg", "-re", "-i", "output.mp4",
    "-an",
    "-c:v", "libx264",
    "-preset", "veryfast",     
    "-tune", "zerolatency",
    "-pix_fmt", "yuv420p",
    "-r", "30",
    "-g", "30",
    "-b:v", "5000k",          
    "-maxrate", "5000k",
    "-bufsize", "10000k",
    "-f", "mpegts",
    "pipe:1"
]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return StreamingResponse(proc.stdout, media_type="video/MP2T")