from datetime import datetime, timezone
from app.core.database import Database
from app.utils.my_logger import MyLogger

logger = MyLogger("Message")


class Message:
    """
    消息类，管理单条消息内容
    """
    _message_counter = 0
    
    def __init__(self, sender_user, receiver_user, send_content):
        Message._message_counter += 1
        self.message_id = Message._message_counter
        self.message_content = send_content
        self.message_send_time_in_utc = datetime.now(timezone.utc)
        self.message_sender_id = sender_user.user_id
        self.message_receiver_id = receiver_user.user_id
        
        self.message_sender = sender_user
        self.message_receiver = receiver_user
        
        logger.info(f"Created message {self.message_id} from {self.message_sender_id} to {self.message_receiver_id}")
    
    async def save_to_database(self) -> bool:
        """
        保存消息到数据库
        """
        try:
            message_dict = {
                "message_id": self.message_id,
                "message_content": self.message_content,
                "message_send_time_in_utc": self.message_send_time_in_utc,
                "message_sender_id": self.message_sender_id,
                "message_receiver_id": self.message_receiver_id
            }
            
            existing_message = await Database.find_one("messages", {"message_id": self.message_id})
            
            if existing_message:
                await Database.update_one(
                    "messages",
                    {"message_id": self.message_id},
                    {"$set": message_dict}
                )
            else:
                await Database.insert_one("messages", message_dict)
            
            logger.info(f"Saved message {self.message_id} to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving message {self.message_id} to database: {e}")
            return False