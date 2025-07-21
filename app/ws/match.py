from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.WebSocketsService.MatchSessionHandler import MatchSessionHandler

router = APIRouter()

@router.websocket("/ws/match")
async def websocket_match(websocket: WebSocket):
    """
    /ws/match 路由，使用 MatchSessionHandler 作为匹配专用 WebSocket 处理器。
    支持认证、匹配消息、会话管理等。
    """
    await websocket.accept()
    handler = MatchSessionHandler(websocket)
    try:
        await handler.handle_connection()
    except WebSocketDisconnect:
        # 断开连接时的日志由 handler.on_disconnect 负责
        pass 