from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websocket.manager import manager
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for the dashboard.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive and listen for any client messages (e.g., stats request)
            data = await websocket.receive_text()
            # We can handle client messages here if needed, for now just echo or log
            if data == "ping":
                await manager.send_personal_message("pong", websocket)
            else:
                logger.debug(f"Received message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
