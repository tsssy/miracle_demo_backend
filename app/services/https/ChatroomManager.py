from app.config import settings
from app.objects.Chatroom import Chatroom
from app.services.https.MatchManager import MatchManager
from app.services.https.UserManagement import UserManagement
from app.core.database import Database
from app.utils.my_logger import MyLogger
from typing import Optional, List, Tuple

logger = MyLogger("ChatroomManager")


class ChatroomManager:
    """
    聊天室管理器，全局唯一，管理所有聊天室
    """
    _instance = None
    database_url = settings.MONGODB_URL

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.chatrooms = {}  # {chatroom_id: Chatroom}
            logger.info("ChatroomManager singleton instance created")
        return cls._instance

    async def construct(self) -> bool:
        """
        Initialize ChatroomManager by loading data from database
        """
        try:
            # Load existing chatrooms from database
            chatrooms_data = await Database.find("chatrooms")
            loaded_count = 0
            
            for chatroom_data in chatrooms_data:
                try:
                    chatroom_id = chatroom_data["chatroom_id"]
                    user1_id = chatroom_data["user1_id"]
                    user2_id = chatroom_data["user2_id"]
                    
                    # Get user instances
                    user_manager = UserManagement()
                    user1 = user_manager.get_user_instance(user1_id)
                    user2 = user_manager.get_user_instance(user2_id)
                    
                    if user1 and user2:
                        # Create chatroom instance with existing ID
                        chatroom = Chatroom(user1, user2, None)
                        chatroom.chatroom_id = chatroom_id
                        chatroom.message_ids = chatroom_data.get("message_ids", [])
                        
                        self.chatrooms[chatroom_id] = chatroom
                        loaded_count += 1
                    else:
                        logger.warning(f"Cannot load chatroom {chatroom_id}: users {user1_id} or {user2_id} not found")
                        
                except Exception as e:
                    logger.error(f"Error loading chatroom from database: {e}")
                    continue
            
            logger.info(f"Loaded {loaded_count} chatrooms from database")
            return True
            
        except Exception as e:
            logger.error(f"Error constructing ChatroomManager: {e}")
            return False

    async def get_or_create_chatroom(self, user_id_1: int, user_id_2: int, match_id: int) -> int:
        """
        Get existing chatroom or create new one for the match
        Returns chatroom_id
        """
        try:
            logger.info(f"STEP 1.1: Getting match {match_id} from MatchManager")
            # Get match from MatchManager
            match_manager = MatchManager()
            match = match_manager.get_match(match_id)
            
            if not match:
                logger.error(f"STEP 1.1 FAILED: Match {match_id} not found")
                return None
            
            logger.info(f"STEP 1.2: Checking if match {match_id} already has chatroom_id")
            # Check if match already has a chatroom_id
            if match.chatroom_id:
                logger.info(f"STEP 1.2 SUCCESS: Match {match_id} already has chatroom {match.chatroom_id}")
                return match.chatroom_id
            
            logger.info(f"STEP 1.3: Getting user instances for users {user_id_1} and {user_id_2}")
            # Get user instances
            user_manager = UserManagement()
            user1 = user_manager.get_user_instance(user_id_1)
            user2 = user_manager.get_user_instance(user_id_2)
            
            if not user1 or not user2:
                logger.error(f"STEP 1.3 FAILED: Users {user_id_1} or {user_id_2} not found")
                return None
            
            logger.info(f"STEP 1.4: Creating new chatroom for users {user_id_1} and {user_id_2}")
            # Create new chatroom
            chatroom = Chatroom(user1, user2, match_id)
            
            logger.info(f"STEP 1.5: Storing chatroom {chatroom.chatroom_id} in memory")
            # Store in memory
            self.chatrooms[chatroom.chatroom_id] = chatroom
            
            logger.info(f"STEP 1.6: Updating match {match_id} with chatroom_id {chatroom.chatroom_id}")
            # Update match with chatroom_id
            match.chatroom_id = chatroom.chatroom_id
            
            logger.info(f"STEP 1.7: Saving chatroom {chatroom.chatroom_id} to database")
            # Save chatroom to database
            await chatroom.save_to_database()
            
            logger.info(f"STEP 1.8: Saving updated match {match_id} to database")
            # Save match to database with updated chatroom_id
            await match.save_to_database()
            
            logger.info(f"STEP 1 SUCCESS: Created chatroom {chatroom.chatroom_id} for match {match_id}")
            return chatroom.chatroom_id
            
        except Exception as e:
            logger.error(f"STEP 1 FAILED: Error getting or creating chatroom for match {match_id}: {e}")
            return None

    def get_chatroom_history(self, chatroom_id: int, user_id: int) -> List[Tuple[str, str, int, str]]:
        """
        Get chat history for a chatroom, replacing user's own name with "I"
        Returns list of (message, datetime, sender_id, sender_name)
        """
        try:
            logger.info(f"STEP 2.1: Getting chatroom {chatroom_id} from memory")
            chatroom = self.chatrooms.get(chatroom_id)
            if not chatroom:
                logger.error(f"STEP 2.1 FAILED: Chatroom {chatroom_id} not found in memory")
                return []
            
            logger.info(f"STEP 2.2: Getting messages from chatroom {chatroom_id}")
            # Get messages from chatroom
            messages = chatroom.get_messages()
            logger.info(f"STEP 2.2: Found {len(messages)} messages in chatroom")
            
            logger.info(f"STEP 2.3: Transforming messages for user {user_id}")
            # Transform messages for the requesting user
            chat_history = []
            for message_content, datetime_utc, sender_id, sender_name in messages:
                # Replace sender name with "I" if it's the requesting user
                display_name = "I" if sender_id == user_id else sender_name
                
                chat_history.append((
                    message_content,
                    datetime_utc.isoformat() if hasattr(datetime_utc, 'isoformat') else str(datetime_utc),
                    sender_id,
                    display_name
                ))
            
            logger.info(f"STEP 2.3 SUCCESS: Retrieved {len(chat_history)} messages for chatroom {chatroom_id}, user {user_id}")
            return chat_history
            
        except Exception as e:
            logger.error(f"STEP 2 FAILED: Error getting chat history for chatroom {chatroom_id}: {e}")
            return []

    async def save_chatroom_history(self, chatroom_id: Optional[int] = None) -> bool:
        """
        Save chatroom and its messages to database
        If chatroom_id is None, save all chatrooms
        """
        try:
            if chatroom_id is not None:
                # Save specific chatroom
                chatroom = self.chatrooms.get(chatroom_id)
                if chatroom:
                    success = await chatroom.save_to_database()
                    
                    # Also save all messages in the chatroom
                    message_save_count = 0
                    for message in chatroom.messages:
                        if await message.save_to_database():
                            message_save_count += 1
                    
                    logger.info(f"Saved chatroom {chatroom_id} and {message_save_count} messages")
                    return success
                else:
                    logger.error(f"Chatroom {chatroom_id} not found")
                    return False
            else:
                # Save all chatrooms
                success_count = 0
                total_chatrooms = len(self.chatrooms)
                
                for chatroom in self.chatrooms.values():
                    if await chatroom.save_to_database():
                        success_count += 1
                        
                        # Save all messages in the chatroom
                        for message in chatroom.messages:
                            await message.save_to_database()
                
                logger.info(f"Saved {success_count}/{total_chatrooms} chatrooms to database")
                return success_count == total_chatrooms
                
        except Exception as e:
            logger.error(f"Error saving chatroom history: {e}")
            return False