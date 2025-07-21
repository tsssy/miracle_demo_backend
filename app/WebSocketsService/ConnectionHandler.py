import json
import logging
from fastapi import WebSocket
from app.services.https.UserManagement import UserManagement


class ConnectionHandler:
    """
    连接管理器，管理所有WebSocket连接
    """
    sessions = {}  # 类级别，存储所有已认证的客户端 {user_id: websocket}

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.user_id = None

    async def handle_connection(self):
        """
        处理连接的生命周期：认证 -> 连接 -> 消息循环 -> 断开
        """
        try:
            # 等待认证消息
            auth_message = await self.websocket.receive_text()
            try:
                auth_data = json.loads(auth_message)
            except json.JSONDecodeError:
                await self.websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
                await self.websocket.close()
                return

            # 认证
            if not await self._authenticate(auth_data):
                await self.websocket.send_text(json.dumps({"error": "Authentication failed"}))
                await self.websocket.close()
                return

            # 认证成功，注册会话
            self.sessions[self.user_id] = self.websocket
            await self.websocket.send_text(json.dumps({"status": "authenticated", "user_id": self.user_id}))
            
            # 调用连接钩子
            await self.on_connect()

            # 消息循环
            while True:
                message = await self.websocket.receive_text()
                try:
                    message_data = json.loads(message)
                    await self.on_message(message_data)
                except json.JSONDecodeError:
                    await self.websocket.send_text(json.dumps({"error": "Invalid JSON format"}))

        except Exception as e:
            logging.error(f"Connection error for user {self.user_id}: {e}")
        finally:
            # 清理会话
            if self.user_id and self.user_id in self.sessions:
                del self.sessions[self.user_id]
            await self.on_disconnect()

    @classmethod
    async def broadcast(cls, message: str, exclude_id: str = None):
        """
        广播消息给所有连接的客户端
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
        发送消息给指定用户
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
        认证逻辑，检查用户是否在UserManagement缓存中存在
        """
        print(f"🔍 [DEBUG] Starting authentication process...")
        print(f"🔍 [DEBUG] Received auth_data: {auth_data}")
        
        if "user_id" not in auth_data:
            print(f"❌ [DEBUG] No user_id found in auth_data")
            logging.warning("Authentication failed: no user_id provided")
            return False
        
        user_id_input = auth_data["user_id"]
        print(f"🔍 [DEBUG] Extracted user_id_input: '{user_id_input}' (type: {type(user_id_input)})")
        
        # 获取UserManagement实例并检查用户是否存在
        try:
            print(f"🔍 [DEBUG] Getting UserManagement instance...")
            user_manager = UserManagement()
            print(f"🔍 [DEBUG] UserManagement instance created: {user_manager}")
            
            # 检查UserManagement是否已初始化
            print(f"🔍 [DEBUG] UserManagement._initialized: {UserManagement._initialized}")
            print(f"🔍 [DEBUG] UserManagement user_list length: {len(user_manager.user_list)}")
            print(f"🔍 [DEBUG] UserManagement user_list keys (first 5): {list(user_manager.user_list.keys())[:5]}")
            
            # 转换用户ID为int类型进行查找（因为缓存中的键是int）
            try:
                user_id_for_lookup = int(user_id_input)
                print(f"🔍 [DEBUG] Successfully converted '{user_id_input}' to int: {user_id_for_lookup}")
            except (ValueError, TypeError) as e:
                print(f"❌ [DEBUG] Failed to convert '{user_id_input}' to int: {e}")
                logging.warning(f"Authentication failed: user_id '{user_id_input}' cannot be converted to int")
                return False
            
            print(f"🔍 [DEBUG] Looking up user with ID: {user_id_for_lookup} (type: {type(user_id_for_lookup)})")
            user_instance = user_manager.get_user_instance(user_id_for_lookup)
            print(f"🔍 [DEBUG] get_user_instance returned: {user_instance}")
            
            if user_instance is None:
                print(f"❌ [DEBUG] User not found in cache")
                print(f"🔍 [DEBUG] Available user IDs in cache: {sorted(list(user_manager.user_list.keys()))}")
                logging.warning(f"Authentication failed: user_id '{user_id_input}' not found in UserManagement cache")
                return False
            
            # 保存用户ID为字符串格式（用于WebSocket会话管理）
            self.user_id = str(user_id_input)
            print(f"✅ [DEBUG] Authentication successful! User: {user_instance.telegram_user_name}")
            logging.info(f"Authentication successful for user_id: {user_id_input} (looked up as {user_id_for_lookup})")
            return True
            
        except Exception as e:
            print(f"❌ [DEBUG] Exception during authentication: {e}")
            print(f"❌ [DEBUG] Exception type: {type(e)}")
            import traceback
            print(f"❌ [DEBUG] Traceback: {traceback.format_exc()}")
            logging.error(f"Authentication error for user_id '{user_id_input}': {e}")
            return False

    async def on_connect(self):
        """
        连接成功后的钩子，子类可以重写
        """
        logging.info(f"User {self.user_id} connected")

    async def on_message(self, message):
        """
        收到消息时的钩子，子类应该重写
        """
        # 默认行为：广播给所有用户
        await self.broadcast(json.dumps({
            "type": "message",
            "from": self.user_id,
            "content": message
        }), exclude_id=self.user_id)

    async def on_disconnect(self):
        """
        断开连接时的钩子，子类可以重写
        """
        logging.info(f"User {self.user_id} disconnected")