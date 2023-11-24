import webbrowser

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from app.controllers.app_manager import router as am_router
from app.controllers.pages import router as pages_router
from app.controllers.websocket import router as ws_router

main_router = APIRouter(prefix="/api", tags=["API"])
main_router.include_router(am_router)
main_router.include_router(ws_router)

origins = [
    "http://localhost:8000",
]

app = FastAPI(title="Test API")

app.include_router(main_router)
app.include_router(pages_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

if __name__ == "__main__":
    webbrowser.open("http://localhost:8000/index")
    uvicorn.run(app, host="0.0.0.0", port=8000)
