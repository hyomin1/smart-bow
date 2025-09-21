from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import target, arrow, webrtc
from app.services.registry import registry
from app.core import config

import os

app = FastAPI(
    title="Smart Archery",
    version="0.1.0",
    description="스마트 국궁"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(target.router, prefix="/target", tags=["target"])
app.include_router(arrow.router, tags=["arrow"])
app.include_router(webrtc.router, prefix="/webrtc", tags=["webrtc"])


@app.on_event("startup")
async def startup_event():
    for name, url in config.CAMERA_URLS.items():
        registry.add_camera(name,url)

@app.on_event("shutdown")
async def shutdown_event():
    registry.stop_all()

@app.get("/api")
async def root():
    return {"message": "Hello World"}
