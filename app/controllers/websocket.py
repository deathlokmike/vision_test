from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

from app.services.connection_manager import manager

router = APIRouter(prefix="/ws")


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
