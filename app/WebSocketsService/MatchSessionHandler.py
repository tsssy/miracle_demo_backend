import json
import logging
from fastapi import WebSocket
from .ConnectionHandler import ConnectionHandler
from app.services.https.N8nWebhookManager import N8nWebhookManager
from app.services.https.MatchManager import MatchManager


class MatchSessionHandler(ConnectionHandler):
    """
    匹配会话处理器，使用N8nWebhookManager和MatchManager实现匹配功能
    """
    sessions = {}  # 类级别的字典，作为"会话管理器"，用于存储所有已认证的客户端

    def __init__(self, websocket: WebSocket):
        """
        构造函数。当一个新客户端连接时，创建一个新的 MatchSessionHandler 实例。
        """
        super().__init__(websocket)

    async def on_connect(self):
        """
        连接成功后的钩子，使用N8nWebhookManager获取匹配并创建Match
        """
        await super().on_connect()
        logging.info(f"User {self.user_id} connected to match system")
        
        try:
            # 获取N8nWebhookManager实例并请求匹配
            webhook_manager = N8nWebhookManager()
            user_id_int = int(self.user_id)
            
            # 请求1个匹配
            matches = await webhook_manager.request_matches(user_id_int, num_of_matches=1)
            
            if not matches:
                await self.websocket.send_text(json.dumps({
                    "type": "match_error",
                    "message": "No matches found"
                }))
                return
            
            # 获取第一个匹配
            match_data = matches[0]
            
            # 获取MatchManager实例
            match_manager = MatchManager()
            
            # 创建匹配
            match = await match_manager.create_match(
                user_id_1=match_data.get('self_user_id'),
                user_id_2=match_data.get('matched_user_id'),
                reason_1=match_data.get('reason_of_match_given_to_self_user'),
                reason_2=match_data.get('reason_of_match_given_to_matched_user'),
                match_score=match_data.get('match_score')
            )
            
            # 发送匹配信息给客户端
            match_info = {
                "type": "match_info",
                "match_id": match.match_id,
                "self_user_id": match_data.get('self_user_id'),
                "matched_user_id": match_data.get('matched_user_id'),
                "match_score": match_data.get('match_score'),
                "reason_of_match_given_to_self_user": match_data.get('reason_of_match_given_to_self_user'),
                "reason_of_match_given_to_matched_user": match_data.get('reason_of_match_given_to_matched_user')
            }
            
            await self.websocket.send_text(json.dumps(match_info))
            logging.info(f"Match created and sent to user {self.user_id}: match_id={match.match_id}")
            
        except Exception as e:
            logging.error(f"Error in on_connect for user {self.user_id}: {e}")
            await self.websocket.send_text(json.dumps({
                "type": "match_error",
                "message": f"Failed to create match: {str(e)}"
            }))

    async def on_disconnect(self):
        """
        断开连接时的钩子，进行清理工作
        """
        await super().on_disconnect()
        logging.info(f"User {self.user_id} disconnected from match system")

    @classmethod
    async def broadcast(cls, message: str, exclude_id: str = None):
        """
        广播消息给所有连接的客户端（可被子类复写）
        """
        if not cls.sessions:
            return

        disconnected = []
        for user_id, websocket in cls.sessions.items():
            if exclude_id and user_id == exclude_id:
                continue
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.append(user_id)
        
        # 清理断开的连接
        for user_id in disconnected:
            cls.sessions.pop(user_id, None)

    @classmethod
    async def send_to_user(cls, user_id: str, message: str) -> bool:
        """
        向指定用户ID发送私聊消息（可被子类复写）
        """
        if user_id not in cls.sessions:
            return False
        
        try:
            await cls.sessions[user_id].send_text(message)
            return True
        except Exception:
            cls.sessions.pop(user_id, None)
            return False

    async def _authenticate(self, auth_data: dict) -> bool:
        """
        认证逻辑，检查用户是否在UserManagement的user_list中
        """
        # 使用父类的认证逻辑
        return await super()._authenticate(auth_data)