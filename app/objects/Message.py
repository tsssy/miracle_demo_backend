from datetime import datetime, timezone
from app.core.database import Database
from app.utils.my_logger import MyLogger

logger = MyLogger("Message")


class Message:
    """
    消息类，管理单条消息内容
    """
    _message_counter = 0
    _initialized = False
    
    @classmethod
    async def initialize_counter(cls):
        """
        从数据库初始化消息计数器，确保不会产生重复ID
        """
        if cls._initialized:
            return
            
        try:
            # 查找数据库中最大的_id（message_id存储在_id字段中）
            messages = await Database.find("messages", sort=[("_id", -1)], limit=1)
            
            if messages:
                max_id = messages[0]["_id"]
                cls._message_counter = max_id
                logger.info(f"Message counter initialized from database: starting from {max_id}")
            else:
                cls._message_counter = 0
                logger.info("No existing messages found, starting counter from 0")
                
            cls._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize message counter: {e}")
            # 如果初始化失败，使用时间戳作为起始点以避免冲突
            import time
            cls._message_counter = int(time.time() * 1000)  # 毫秒时间戳
            cls._initialized = True
            logger.warning(f"Using timestamp as message counter starting point: {cls._message_counter}")
    
    def __init__(self, sender_user, receiver_user, send_content, chatroom_id):
        # 确保计数器已初始化
        if not Message._initialized:
            raise RuntimeError("Message counter not initialized. Call Message.initialize_counter() first.")
            
        Message._message_counter += 1
        self.message_id = Message._message_counter
        self.message_content = send_content
        self.message_send_time_in_utc = datetime.now(timezone.utc)
        self.message_sender_id = sender_user.user_id
        self.message_receiver_id = receiver_user.user_id
        self.chatroom_id = chatroom_id  # 消息归属的聊天室ID
        
        self.message_sender = sender_user
        self.message_receiver = receiver_user
        
        # 验证消息归属：确保发送者和接收者都属于指定的chatroom
        self._validate_chatroom_membership()
        
        logger.info(f"Created message {self.message_id} from {self.message_sender_id} to {self.message_receiver_id} in chatroom {self.chatroom_id}")
    
    async def save_to_database(self) -> bool:
        """
        保存消息到数据库，使用message_id作为_id主键
        消息一旦创建不可更新，确保数据完整性
        """
        try:
            message_dict = {
                "_id": self.message_id,  # 使用message_id作为MongoDB的_id主键
                "message_content": self.message_content,
                "message_send_time_in_utc": self.message_send_time_in_utc,
                "message_sender_id": self.message_sender_id,
                "message_receiver_id": self.message_receiver_id,
                "chatroom_id": self.chatroom_id  # 保存消息所属的聊天室ID
            }
            
            # 检查消息是否已存在（基于_id查询，O(log n)复杂度）
            existing_message = await Database.find_one("messages", {"_id": self.message_id})
            
            if existing_message:
                # 消息已存在，不允许更新
                logger.warning(f"Message {self.message_id} already exists in database - skipping save (messages are immutable)")
                return True  # 返回True因为消息已经存在于数据库中
            else:
                # 插入新消息
                await Database.insert_one("messages", message_dict)
                logger.info(f"Saved new message {self.message_id} to database")
                return True
            
        except Exception as e:
            logger.error(f"Error saving message {self.message_id} to database: {e}")
            return False
    
    def _validate_chatroom_membership(self):
        """
        验证消息的发送者和接收者是否都属于指定的聊天室
        这是一个保险机制，确保消息不会被错误分配到其他聊天室
        """
        try:
            # 导入放在方法内部避免循环导入
            from app.services.https.ChatroomManager import ChatroomManager
            
            # 获取ChatroomManager实例
            chatroom_manager = ChatroomManager()
            
            # 检查指定的chatroom是否存在
            chatroom = chatroom_manager.chatrooms.get(self.chatroom_id)
            if not chatroom:
                raise ValueError(f"Chatroom {self.chatroom_id} does not exist")
            
            # 验证发送者和接收者是否都属于这个聊天室
            chatroom_users = {chatroom.user1_id, chatroom.user2_id}
            message_users = {self.message_sender_id, self.message_receiver_id}
            
            if message_users != chatroom_users:
                raise ValueError(
                    f"Message users {message_users} do not match chatroom {self.chatroom_id} users {chatroom_users}. "
                    f"This message cannot belong to this chatroom."
                )
            
            logger.info(f"Message {self.message_id} chatroom membership validated successfully")
            
        except Exception as e:
            logger.error(f"Chatroom membership validation failed for message {self.message_id}: {e}")
            raise ValueError(f"Invalid chatroom assignment: {e}")
    
    @staticmethod
    async def validate_message_chatroom_consistency() -> bool:
        """
        静态方法：验证数据库中所有消息的chatroom归属是否正确
        返回True如果所有消息都正确归属，False如果发现问题
        """
        try:
            logger.info("Starting message-chatroom consistency validation...")
            
            # 获取所有消息和聊天室
            messages = await Database.find("messages")
            chatrooms = await Database.find("chatrooms")
            
            # 建立chatroom_id到用户对的映射
            chatroom_users = {}
            for room in chatrooms:
                chatroom_id = room["chatroom_id"]
                users = {room["user1_id"], room["user2_id"]}
                chatroom_users[chatroom_id] = users
            
            # 检查每条消息
            validation_errors = []
            for msg in messages:
                message_id = msg["_id"]  # message_id现在存储在_id字段中
                chatroom_id = msg.get("chatroom_id")
                
                if not chatroom_id:
                    validation_errors.append(f"Message {message_id} has no chatroom_id")
                    continue
                
                if chatroom_id not in chatroom_users:
                    validation_errors.append(f"Message {message_id} references non-existent chatroom {chatroom_id}")
                    continue
                
                # 验证消息的用户是否属于该chatroom
                msg_users = {msg["message_sender_id"], msg["message_receiver_id"]}
                room_users = chatroom_users[chatroom_id]
                
                if msg_users != room_users:
                    validation_errors.append(
                        f"Message {message_id} users {msg_users} don't match chatroom {chatroom_id} users {room_users}"
                    )
            
            if validation_errors:
                logger.error(f"Found {len(validation_errors)} validation errors:")
                for error in validation_errors:
                    logger.error(f"  - {error}")
                return False
            else:
                logger.info(f"All {len(messages)} messages have correct chatroom assignments")
                return True
                
        except Exception as e:
            logger.error(f"Error during message-chatroom consistency validation: {e}")
            return False