import json
import logging
from fastapi import WebSocket
from .ConnectionHandler import ConnectionHandler


class MatchSessionHandler(ConnectionHandler):
    """
    匹配会话处理器，处理用户匹配相关的WebSocket连接
    """
    # 匹配队列和活跃匹配会话
    match_queue = []  # 等待匹配的用户ID列表
    active_matches = {}  # {match_id: [user_id1, user_id2]}
    match_sessions = {}  # {user_id: match_id}

    async def on_connect(self):
        """
        用户连接时，加入匹配系统
        """
        await super().on_connect()
        logging.info(f"User {self.user_id} joined match system")
        
        # 发送欢迎消息
        await self.websocket.send_text(json.dumps({
            "type": "match_system_connected",
            "message": "Connected to match system",
            "user_id": self.user_id
        }))

    async def on_message(self, message: dict):
        """
        处理匹配相关消息
        """
        message_type = message.get("type")
        
        if message_type == "start_matching":
            await self._start_matching()
        elif message_type == "stop_matching":
            await self._stop_matching()
        elif message_type == "match_message":
            await self._handle_match_message(message)
        elif message_type == "end_match":
            await self._end_match()
        else:
            await self.websocket.send_text(json.dumps({
                "error": f"Unknown message type: {message_type}"
            }))

    async def _start_matching(self):
        """
        开始匹配
        """
        if self.user_id in self.match_queue:
            await self.websocket.send_text(json.dumps({
                "type": "match_status",
                "status": "already_in_queue"
            }))
            return
            
        if self.user_id in self.match_sessions:
            await self.websocket.send_text(json.dumps({
                "type": "match_status", 
                "status": "already_in_match"
            }))
            return

        # 检查是否有等待的用户
        if self.match_queue:
            # 匹配成功
            partner_id = self.match_queue.pop(0)
            match_id = f"match_{self.user_id}_{partner_id}"
            
            # 创建匹配会话
            self.active_matches[match_id] = [self.user_id, partner_id]
            self.match_sessions[self.user_id] = match_id
            self.match_sessions[partner_id] = match_id
            
            # 通知双方匹配成功
            match_message = json.dumps({
                "type": "match_found",
                "match_id": match_id,
                "partner_id": partner_id if self.user_id != partner_id else self.user_id
            })
            
            await self.send_to_user(self.user_id, match_message)
            await self.send_to_user(partner_id, json.dumps({
                "type": "match_found",
                "match_id": match_id,
                "partner_id": self.user_id
            }))
            
        else:
            # 加入等待队列
            self.match_queue.append(self.user_id)
            await self.websocket.send_text(json.dumps({
                "type": "match_status",
                "status": "waiting_for_match"
            }))

    async def _stop_matching(self):
        """
        停止匹配
        """
        if self.user_id in self.match_queue:
            self.match_queue.remove(self.user_id)
            await self.websocket.send_text(json.dumps({
                "type": "match_status",
                "status": "stopped_matching"
            }))
        else:
            await self.websocket.send_text(json.dumps({
                "type": "match_status",
                "status": "not_in_queue"
            }))

    async def _handle_match_message(self, message: dict):
        """
        处理匹配会话中的消息
        """
        if self.user_id not in self.match_sessions:
            await self.websocket.send_text(json.dumps({
                "error": "Not in a match session"
            }))
            return
            
        match_id = self.match_sessions[self.user_id]
        if match_id not in self.active_matches:
            await self.websocket.send_text(json.dumps({
                "error": "Match session not found"
            }))
            return
            
        # 找到对方用户
        match_users = self.active_matches[match_id]
        partner_id = next((uid for uid in match_users if uid != self.user_id), None)
        
        if not partner_id:
            await self.websocket.send_text(json.dumps({
                "error": "Partner not found"
            }))
            return
            
        # 转发消息给对方
        content = message.get("content", "")
        forward_message = json.dumps({
            "type": "match_message",
            "from": self.user_id,
            "content": content,
            "match_id": match_id,
            "timestamp": message.get("timestamp")
        })
        
        success = await self.send_to_user(partner_id, forward_message)
        
        # 给发送者确认
        await self.websocket.send_text(json.dumps({
            "type": "message_status",
            "delivered": success,
            "content": content
        }))

    async def _end_match(self):
        """
        结束匹配会话
        """
        if self.user_id not in self.match_sessions:
            await self.websocket.send_text(json.dumps({
                "error": "Not in a match session"
            }))
            return
            
        match_id = self.match_sessions[self.user_id]
        if match_id in self.active_matches:
            match_users = self.active_matches[match_id]
            
            # 通知所有参与者匹配结束
            end_message = json.dumps({
                "type": "match_ended",
                "match_id": match_id,
                "ended_by": self.user_id
            })
            
            for user_id in match_users:
                await self.send_to_user(user_id, end_message)
                self.match_sessions.pop(user_id, None)
                
            # 清理匹配记录
            del self.active_matches[match_id]

    async def on_disconnect(self):
        """
        用户断开连接时的清理工作
        """
        await super().on_disconnect()
        
        # 从匹配队列中移除
        if self.user_id in self.match_queue:
            self.match_queue.remove(self.user_id)
            
        # 结束当前匹配会话
        if self.user_id in self.match_sessions:
            await self._end_match()
            
        logging.info(f"User {self.user_id} left match system")