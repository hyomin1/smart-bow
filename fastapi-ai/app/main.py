from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import webrtc

from app.core import config

import asyncio
import platform


app = FastAPI(
    title="SmartBow",
    version="1.0.0",
    description="Smart Archery System — WebRTC Signaling + Event Server",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebRTC 라우터
app.include_router(webrtc.router, prefix="/webrtc", tags=["webrtc"])


# FastAPI 시작 시 필요한 작업


@app.get("/api")
async def root():
    return {"message": "SmartBow FastAPI OK"}
