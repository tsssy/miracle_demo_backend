from app.core.database import Database
from app.utils.my_logger import MyLogger

logger = MyLogger("Chatroom")


class Chatroom:
    """
    聊天室类，管理聊天室内容
    """
    _chatroom_counter = 0
    
    def __init__(self, user1, user2, match_id):
        Chatroom._chatroom_counter += 1
        self.chatroom_id = Chatroom._chatroom_counter
        self.message_ids = []
        self.user1_id = user1.user_id
        self.user2_id = user2.user_id
        
        self.user1 = user1
        self.user2 = user2
        
        logger.info(f"Created chatroom {self.chatroom_id} for users {self.user1_id} and {self.user2_id}")

    async def save_to_database(self) -> bool:
        """
        保存聊天室到数据库
        """
        try:
            chatroom_dict = {
                "chatroom_id": self.chatroom_id,
                "user1_id": self.user1_id,
                "user2_id": self.user2_id,
                "message_ids": self.message_ids
            }
            
            # Check if chatroom already exists
            existing_chatroom = await Database.find_one("chatrooms", {"chatroom_id": self.chatroom_id})
            if existing_chatroom:
                await Database.update_one(
                    "chatrooms",
                    {"chatroom_id": self.chatroom_id},
                    {"$set": chatroom_dict}
                )
            else:
                await Database.insert_one("chatrooms", chatroom_dict)
            
            logger.info(f"Saved chatroom {self.chatroom_id} to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving chatroom {self.chatroom_id} to database: {e}")
            return False