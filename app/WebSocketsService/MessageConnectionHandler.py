import json
import logging
from fastapi import WebSocket
from .ConnectionHandler import ConnectionHandler


class MessageConnectionHandler(ConnectionHandler):
    """
    消息连接处理器，专门处理私聊消息
    """

    async def on_message(self, message: dict):
        """
        处理消息，支持私聊和广播
        """
        message_type = message.get("type", "broadcast")
        
        if message_type == "private":
            # 私聊消息
            target_user_id = message.get("target_user_id")
            content = message.get("content", "")
            
            if not target_user_id:
                await self.websocket.send_text(json.dumps({
                    "error": "target_user_id is required for private messages"
                }))
                return
            
            # 发送私聊消息
            success = await self.send_to_user(target_user_id, json.dumps({
                "type": "private_message",
                "from": self.user_id,
                "content": content,
                "timestamp": message.get("timestamp")
            }))
            
            # 给发送者确认
            await self.websocket.send_text(json.dumps({
                "type": "message_status",
                "target_user_id": target_user_id,
                "delivered": success,
                "content": content
            }))
            
        elif message_type == "broadcast":
            # 广播消息
            content = message.get("content", "")
            await self.broadcast(json.dumps({
                "type": "broadcast_message",
                "from": self.user_id,
                "content": content,
                "timestamp": message.get("timestamp")
            }), exclude_id=self.user_id)
            
        else:
            await self.websocket.send_text(json.dumps({
                "error": f"Unknown message type: {message_type}"
            }))

    async def on_connect(self):
        """
        用户连接时通知
        """
        await super().on_connect()
        # 通知其他用户有新用户加入
        await self.broadcast(json.dumps({
            "type": "user_joined",
            "user_id": self.user_id
        }), exclude_id=self.user_id)

    async def on_disconnect(self):
        """
        用户断开连接时通知
        """
        await super().on_disconnect()
        # 通知其他用户有用户离开
        await self.broadcast(json.dumps({
            "type": "user_left", 
            "user_id": self.user_id
        }), exclude_id=self.user_id)