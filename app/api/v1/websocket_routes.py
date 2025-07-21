from fastapi import APIRouter, WebSocket
from app.WebsocketServices.ConnectionHandler import ConnectionHandler
from app.WebsocketServices.MessageConnectionHandler import MessageConnectionHandler
from app.WebsocketServices.MatchSessionHandler import MatchSessionHandler

router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    class ChatHandler(ConnectionHandler):
        async def on_message(self, message):
            print(f"[WS-Chat] 收到消息: {message}")  # 测试日志
            await super().on_message(message)
    handler = ChatHandler(websocket)
    await handler.handle_connection()

@router.websocket("/ws/message")
async def websocket_message_endpoint(websocket: WebSocket):
    await websocket.accept()
    class MyMessageHandler(MessageConnectionHandler):
        async def on_message(self, message, target_user_id=None):
            print(f"[WS-Message] 收到消息: {message}, 目标用户: {target_user_id}")  # 测试日志
            await super().on_message(message, target_user_id)
    handler = MyMessageHandler(websocket)
    await handler.handle_connection()

@router.websocket("/ws/match")
async def websocket_match_endpoint(websocket: WebSocket):
    await websocket.accept()
    class MyMatchHandler(MatchSessionHandler):
        async def on_message(self, message):
            print(f"[WS-Match] 收到消息: {message}")  # 测试日志
            await super().on_message(message)
    handler = MyMatchHandler(websocket)
    await handler.handle_connection() 