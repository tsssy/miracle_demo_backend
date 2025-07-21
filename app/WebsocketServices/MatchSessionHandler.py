import asyncio
from typing import Optional, Dict, Any
import websockets

class MatchSessionHandler:
    """
    匹配会话专用 WebSocket 连接处理器，负责单个客户端连接的生命周期管理。
    """
    # 类级别的 sessions 字典，管理所有已认证的客户端
    sessions: Dict[str, websockets.WebSocketServerProtocol] = {}

    def __init__(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """
        构造函数，初始化单个客户端连接。
        :param websocket: 当前客户端的 WebSocket 连接对象
        """
        self.websocket = websocket  # 当前连接对象
        self.user_id: Optional[str] = None  # 认证前为 None

    async def handle_connection(self) -> None:
        """
        连接生命周期主引擎：认证、注册、消息循环、断开处理。
        """
        try:
            # 1. 认证
            auth_data = await self.websocket.recv()
            if not await self._authenticate(auth_data):
                await self.websocket.send("认证失败，连接关闭")
                await self.websocket.close()
                return
            # 2. 注册会话
            MatchSessionHandler.sessions[self.user_id] = self.websocket
            await self.on_connect()
            # 3. 消息循环
            while True:
                message = await self.websocket.recv()
                await self.on_message(message)
        except websockets.ConnectionClosed:
            pass
        finally:
            # 4. 断开连接
            if self.user_id in MatchSessionHandler.sessions:
                del MatchSessionHandler.sessions[self.user_id]
            await self.on_disconnect()

    @classmethod
    async def broadcast(cls, message: str, exclude_id: Optional[str] = None) -> None:
        """
        向所有已认证客户端广播消息，可排除某个用户。
        :param message: 要广播的消息
        :param exclude_id: 可选，排除的用户ID
        """
        for uid, ws in cls.sessions.items():
            if exclude_id is not None and uid == exclude_id:
                continue
            try:
                await ws.send(message)
            except Exception:
                pass

    @classmethod
    async def send_to_user(cls, user_id: str, message: str) -> bool:
        """
        向指定用户发送私聊消息。
        :param user_id: 目标用户ID
        :param message: 消息内容
        :return: 是否发送成功
        """
        ws = cls.sessions.get(user_id)
        if ws:
            try:
                await ws.send(message)
                return True
            except Exception:
                return False
        return False

    async def _authenticate(self, auth_data: Any) -> bool:
        """
        认证逻辑，可被子类复写。默认假设 auth_data 是 JSON 字符串，包含 user_id。
        :param auth_data: 客户端发来的认证数据
        :return: 是否认证成功
        """
        import json
        try:
            data = json.loads(auth_data)
            user_id = data.get("user_id")
            if user_id:
                self.user_id = user_id
                return True
        except Exception:
            pass
        return False

    async def on_connect(self) -> None:
        """
        连接建立并认证后调用。可被子类复写。
        """
        # 可在子类中实现欢迎消息、广播等
        pass

    async def on_message(self, message: Any) -> None:
        """
        收到消息时调用。可被子类复写。
        """
        # 默认行为：广播消息
        await self.broadcast(f"用户{self.user_id}说: {message}")

    async def on_disconnect(self) -> None:
        """
        连接断开时调用。可被子类复写。
        """
        # 可在子类中实现离线通知、清理等
        pass 