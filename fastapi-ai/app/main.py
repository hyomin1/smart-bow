from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import target, arrow, webrtc
from app.frame_manager import start_receiver
from app.core import config



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
    start_receiver()


@app.get("/")
async def root():
    return {"message": "Hello World"}




