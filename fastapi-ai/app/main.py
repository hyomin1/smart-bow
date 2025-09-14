from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import target

app = FastAPI(
    title="Smart Archery",
    version="0.1.0",
    description="스마트 국궁"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(target.router, prefix="/target", tags=["target"])
#app.include_router(ws.router, tags=["websocket"])  

@app.get("/")
async def root():
    return {"message": "Hello World"}




