from app.objects.Message import Message
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
        
        self.messages = []
        self.user1 = user1
        self.user2 = user2
        
        # Load messages from database if they exist
        self._load_messages_from_db()
        
        logger.info(f"Created chatroom {self.chatroom_id} for users {self.user1_id} and {self.user2_id}")
    
    def _load_messages_from_db(self):
        """Load existing messages for this chatroom from database"""
        try:
            # This would be called async in real implementation
            # For now, we'll populate messages as empty list
            pass
        except Exception as e:
            logger.error(f"Error loading messages for chatroom {self.chatroom_id}: {e}")

    async def send_message(self, sender_user_id, message_content, target_user_id):
        """
        发送消息并保存到数据库
        """
        try:
            # Validate sender is part of this chatroom
            if sender_user_id not in [self.user1_id, self.user2_id]:
                logger.error(f"User {sender_user_id} not authorized to send messages in chatroom {self.chatroom_id}")
                return False
            
            # Determine sender and receiver objects
            if sender_user_id == self.user1_id:
                sender_user = self.user1
                receiver_user = self.user2
            else:
                sender_user = self.user2
                receiver_user = self.user1
            
            # Create message
            message = Message(sender_user, receiver_user, message_content)
            
            # Save message to database
            success = await message.save_to_database()
            if success:
                # Add to local storage
                self.messages.append(message)
                self.message_ids.append(message.message_id)
                logger.info(f"Message {message.message_id} sent in chatroom {self.chatroom_id}")
                return True
            else:
                logger.error(f"Failed to save message to database")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message in chatroom {self.chatroom_id}: {e}")
            return False

    def get_messages(self):
        """
        获取消息列表: [(message, datetime, sender_id, sender_name)]
        """
        try:
            message_tuples = []
            for message in self.messages:
                message_tuples.append((
                    message.message_content,
                    message.message_send_time_in_utc,
                    message.message_sender_id,
                    message.message_sender.telegram_user_name
                ))
            
            logger.info(f"Retrieved {len(message_tuples)} messages for chatroom {self.chatroom_id}")
            return message_tuples
            
        except Exception as e:
            logger.error(f"Error getting messages for chatroom {self.chatroom_id}: {e}")
            return []

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