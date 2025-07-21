import json
import logging
from fastapi import WebSocket
from .ConnectionHandler import ConnectionHandler
from app.services.https.ChatroomManager import ChatroomManager
from app.utils.my_logger import MyLogger

logger = MyLogger("MessageConnectionHandler")


class MessageConnectionHandler(ConnectionHandler):
    """
    消息连接处理器，专门处理私聊消息
    """

    async def on_message(self, message: dict):
        """
        处理消息，支持私聊、广播和私信流程
        """
        message_type = message.get("type", "broadcast")
        
        if message_type == "private_chat_init":
            # 新的私信流程初始化
            await self.handle_private_chat_init(message)
            
        elif message_type == "private":
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

    async def handle_private_chat_init(self, message: dict):
        """
        处理私信流程初始化
        步骤1: 获取或创建聊天室
        步骤2: 获取聊天历史记录
        """
        try:
            # 获取参数
            target_user_id = message.get("target_user_id")
            match_id = message.get("match_id")
            
            if not target_user_id or not match_id:
                await self.websocket.send_text(json.dumps({
                    "type": "private_chat_error",
                    "error": "target_user_id and match_id are required"
                }))
                return
            
            logger.info(f"私信流程开始 - 用户 {self.user_id} 发起与用户 {target_user_id} 的私信 (match_id: {match_id})")
            
            # 步骤1: 获取或创建聊天室
            await self.websocket.send_text(json.dumps({
                "type": "private_chat_progress",
                "step": 1,
                "message": f"正在获取或创建聊天室... (match_id: {match_id})"
            }))
            
            chatroom_manager = ChatroomManager()
            chatroom_id = await chatroom_manager.get_or_create_chatroom(
                self.user_id, target_user_id, match_id
            )
            
            if not chatroom_id:
                await self.websocket.send_text(json.dumps({
                    "type": "private_chat_error",
                    "step": 1,
                    "error": "Failed to get or create chatroom"
                }))
                return
            
            # 步骤1完成通知
            await self.websocket.send_text(json.dumps({
                "type": "private_chat_progress",
                "step": 1,
                "status": "completed",
                "chatroom_id": chatroom_id,
                "message": f"聊天室已准备就绪 (chatroom_id: {chatroom_id})"
            }))
            
            # 步骤2: 获取聊天历史记录
            await self.websocket.send_text(json.dumps({
                "type": "private_chat_progress",
                "step": 2,
                "message": f"正在获取聊天历史记录... (chatroom_id: {chatroom_id})"
            }))
            
            chat_history = chatroom_manager.get_chatroom_history(chatroom_id, self.user_id)
            
            # 步骤2完成通知
            await self.websocket.send_text(json.dumps({
                "type": "private_chat_progress",
                "step": 2,
                "status": "completed",
                "chat_history": chat_history,
                "message": f"获取到 {len(chat_history)} 条聊天记录"
            }))
            
            # 私信流程完成
            await self.websocket.send_text(json.dumps({
                "type": "private_chat_init_complete",
                "chatroom_id": chatroom_id,
                "target_user_id": target_user_id,
                "match_id": match_id,
                "chat_history": chat_history,
                "message": "私信流程初始化完成，可以开始聊天"
            }))
            
            logger.info(f"私信流程完成 - 聊天室 {chatroom_id}, 历史记录 {len(chat_history)} 条")
            
        except Exception as e:
            logger.error(f"私信流程失败: {e}")
            await self.websocket.send_text(json.dumps({
                "type": "private_chat_error",
                "error": f"Private chat initialization failed: {str(e)}"
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