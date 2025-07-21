from .ConnectionHandler import ConnectionHandler

class MessageConnectionHandler(ConnectionHandler):
    """
    消息专用连接处理器，支持向指定用户发送消息。
    """
    async def on_message(self, message: str, target_user_id: str = None) -> None:
        """
        收到消息时调用。如果指定了 target_user_id，则私聊，否则广播。
        :param message: 消息内容
        :param target_user_id: 目标用户ID（可选）
        """
        if target_user_id:
            await self.send_to_user(target_user_id, message)
        else:
            await self.broadcast(f"用户{self.user_id}说: {message}") 