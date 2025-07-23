from app.core.database import Database
from app.utils.my_logger import MyLogger

logger = MyLogger("Chatroom")


class Chatroom:
    """
    聊天室类，管理聊天室内容
    """
    _chatroom_counter = 0
    _initialized = False
    
    @classmethod
    async def initialize_counter(cls):
        """
        从数据库初始化聊天室计数器，确保不会产生重复ID
        """
        if cls._initialized:
            return
            
        try:
            # 查找数据库中最大的_id（chatroom_id存储在_id字段中）
            chatrooms = await Database.find("chatrooms", sort=[("_id", -1)], limit=1)
            
            if chatrooms:
                max_id = chatrooms[0]["_id"]
                cls._chatroom_counter = max_id
                logger.info(f"Chatroom counter initialized from database: starting from {max_id}")
            else:
                cls._chatroom_counter = 0
                logger.info("No existing chatrooms found, starting counter from 0")
                
            cls._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize chatroom counter: {e}")
            # 如果初始化失败，使用时间戳作为起始点以避免冲突
            import time
            cls._chatroom_counter = int(time.time() * 1000)  # 毫秒时间戳
            cls._initialized = True
            logger.warning(f"Using timestamp as chatroom counter starting point: {cls._chatroom_counter}")
    
    def __init__(self, user1, user2, match_id):
        # 确保计数器已初始化
        if not Chatroom._initialized:
            raise RuntimeError("Chatroom counter not initialized. Call Chatroom.initialize_counter() first.")
            
        Chatroom._chatroom_counter += 1
        self.chatroom_id = Chatroom._chatroom_counter
        self.message_ids = []
        self.user1_id = user1.user_id
        self.user2_id = user2.user_id
        self.match_id = match_id  # 添加match_id属性
        
        self.user1 = user1
        self.user2 = user2
        
        logger.info(f"Created chatroom {self.chatroom_id} for users {self.user1_id} and {self.user2_id} with match_id {self.match_id}")

    async def save_to_database(self) -> bool:
        """
        保存聊天室到数据库，使用chatroom_id作为_id主键
        """
        try:
            chatroom_dict = {
                "_id": self.chatroom_id,  # 使用chatroom_id作为MongoDB的_id主键
                "user1_id": self.user1_id,
                "user2_id": self.user2_id,
                "message_ids": self.message_ids,
                "match_id": self.match_id  # 添加match_id到数据库字段
            }
            
            # 检查聊天室是否已存在（基于_id查询，O(log n)复杂度）
            existing_chatroom = await Database.find_one("chatrooms", {"_id": self.chatroom_id})
            if existing_chatroom:
                # 更新现有聊天室
                await Database.update_one(
                    "chatrooms",
                    {"_id": self.chatroom_id},
                    {"$set": {k: v for k, v in chatroom_dict.items() if k != "_id"}}  # 不更新_id字段
                )
            else:
                # 插入新聊天室
                await Database.insert_one("chatrooms", chatroom_dict)
            
            logger.info(f"Saved chatroom {self.chatroom_id} to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving chatroom {self.chatroom_id} to database: {e}")
            return False