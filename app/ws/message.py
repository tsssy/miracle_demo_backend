from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.WebSocketsService.MessageConnectionHandler import MessageConnectionHandler

router = APIRouter()

@router.websocket("/ws/message")
async def websocket_message(websocket: WebSocket):
    """
    /ws/message 路由，使用 MessageConnectionHandler 作为消息专用 WebSocket 处理器。
    支持认证、私聊、定向消息等。
    """
    await websocket.accept()
    handler = MessageConnectionHandler(websocket)
    try:
        await handler.handle_connection()
    except WebSocketDisconnect:
        # 断开连接时的日志由 handler.on_disconnect 负责
        pass 