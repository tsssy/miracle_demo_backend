from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.WebSocketsService.ConnectionHandler import ConnectionHandler

router = APIRouter()

@router.websocket("/ws/base")
async def websocket_base(websocket: WebSocket):
    """
    /ws/base 路由，使用 ConnectionHandler 作为基础 WebSocket 处理器。
    每个连接独立实例，支持认证、消息处理、广播等。
    """
    await websocket.accept()
    handler = ConnectionHandler(websocket)
    try:
        await handler.handle_connection()
    except WebSocketDisconnect:
        # 断开连接时的日志由 handler.on_disconnect 负责
        pass 