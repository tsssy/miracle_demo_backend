from app.config import settings
from app.objects.Chatroom import Chatroom
from app.objects.Message import Message
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
            # Initialize counters from database first
            logger.info("ChatroomManager construct: Initializing counters...")
            from app.objects.Message import Message
            from app.objects.Chatroom import Chatroom
            await Message.initialize_counter()
            await Chatroom.initialize_counter()
            
            # Load existing chatrooms from database
            logger.info("ChatroomManager construct: Querying chatrooms from database...")
            chatrooms_data = await Database.find("chatrooms")
            logger.info(f"ChatroomManager construct: Found {len(chatrooms_data)} chatrooms in database")
            loaded_count = 0
            
            for chatroom_data in chatrooms_data:
                try:
                    chatroom_id = chatroom_data["_id"]  # chatroom_id现在存储在_id字段中
                    user1_id = chatroom_data["user1_id"]
                    user2_id = chatroom_data["user2_id"]
                    match_id = chatroom_data.get("match_id")  # 获取match_id，如果不存在则为None
                    
                    logger.info(f"ChatroomManager construct: Processing chatroom {chatroom_id} (users: {user1_id}, {user2_id}, match_id: {match_id})")
                    
                    # 统一转换为int类型
                    chatroom_id = int(chatroom_id)
                    user1_id = int(user1_id)
                    user2_id = int(user2_id)
                    if match_id is not None:
                        match_id = int(match_id)
                    
                    # Get user instances
                    user_manager = UserManagement()
                    user1 = user_manager.get_user_instance(user1_id)
                    user2 = user_manager.get_user_instance(user2_id)
                    
                    if user1 and user2:
                        # Create chatroom instance with existing ID
                        chatroom = Chatroom(user1, user2, match_id)
                        chatroom.chatroom_id = chatroom_id
                        chatroom.message_ids = chatroom_data.get("message_ids", [])
                        
                        self.chatrooms[chatroom_id] = chatroom
                        loaded_count += 1
                        logger.info(f"ChatroomManager construct: Successfully loaded chatroom {chatroom_id} with {len(chatroom.message_ids)} message_ids and match_id {match_id}")
                    else:
                        logger.warning(f"ChatroomManager construct: Cannot load chatroom {chatroom_id}: users {user1_id} (found: {user1 is not None}) or {user2_id} (found: {user2 is not None}) not found")
                        
                except Exception as e:
                    logger.error(f"ChatroomManager construct: Error loading chatroom from database: {e}")
                    continue
            
            logger.info(f"ChatroomManager construct: Loaded {loaded_count} chatrooms from database")
            logger.info(f"ChatroomManager construct: Final chatrooms in memory: {list(self.chatrooms.keys())}")
            return True
            
        except Exception as e:
            logger.error(f"ChatroomManager construct: Error constructing ChatroomManager: {e}")
            return False

    async def get_or_create_chatroom(self, user_id_1, user_id_2, match_id) -> int:
        """
        Get existing chatroom or create new one for the match
        Returns chatroom_id
        """
        try:
            # 统一转换为int类型
            user_id_1 = int(user_id_1)
            user_id_2 = int(user_id_2)
            match_id = int(match_id)
            
            # Debug: 打印ChatroomManager初始状态
            logger.info(f"STEP 0: ChatroomManager current state - {len(self.chatrooms)} chatrooms in memory")
            logger.info(f"STEP 0: Available chatroom IDs: {list(self.chatrooms.keys())}")
            
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
                logger.info(f"STEP 1.2 DEBUG: match.chatroom_id = {match.chatroom_id} (type: {type(match.chatroom_id)})")
                return match.chatroom_id
            
            logger.info(f"STEP 1.3: Getting user instances for users {user_id_1} and {user_id_2}")
            # Get user instances
            user_manager = UserManagement()
            
            user1 = user_manager.get_user_instance(user_id_1)
            user2 = user_manager.get_user_instance(user_id_2)
            
            logger.info(f"STEP 1.3.2: user1 result: {user1 is not None}, user2 result: {user2 is not None}")
            if user1:
                logger.info(f"STEP 1.3.2: user1 found: {user1.telegram_user_name} (ID: {user1.user_id})")
            if user2:
                logger.info(f"STEP 1.3.2: user2 found: {user2.telegram_user_name} (ID: {user2.user_id})")
            
            # 如果用户不存在，打印可用的用户ID列表进行调试
            if not user1 or not user2:
                available_ids = sorted(list(user_manager.user_list.keys()))[:10]  # 显示前10个ID
                logger.error(f"STEP 1.3.2: Available user IDs in cache (first 10): {available_ids}")
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
            chatroom_save_success = await chatroom.save_to_database()
            if not chatroom_save_success:
                logger.error(f"STEP 1.7 FAILED: Could not save chatroom {chatroom.chatroom_id} to database")
                # 从内存中移除失败的chatroom
                self.chatrooms.pop(chatroom.chatroom_id, None)
                return None
            
            logger.info(f"STEP 1.8: Saving updated match {match_id} to database")
            # Save match to database with updated chatroom_id
            match_save_success = await match.save_to_database()
            if not match_save_success:
                logger.error(f"STEP 1.8 FAILED: Could not save match {match_id} to database")
                # 注意：这里不移除chatroom，因为chatroom已经成功创建并保存
                logger.warning(f"STEP 1.8: Chatroom {chatroom.chatroom_id} was created but match update failed")
            
            logger.info(f"STEP 1 SUCCESS: Created chatroom {chatroom.chatroom_id} for match {match_id}")
            return chatroom.chatroom_id
            
        except Exception as e:
            logger.error(f"STEP 1 FAILED: Error getting or creating chatroom for match {match_id}: {e}")
            return None

    async def get_chatroom_history(self, chatroom_id, user_id) -> List[Tuple[str, str, int, str]]:
        """
        Get chat history for a chatroom, replacing user's own name with "I"
        Returns list of (message, datetime, sender_id, sender_name)
        """
        try:
            # 统一转换为int类型
            chatroom_id = int(chatroom_id)
            user_id = int(user_id)
            
            logger.info(f"STEP 2.1: Getting chatroom {chatroom_id} from memory")
            
            # Debug: 打印ChatroomManager的当前状态
            logger.info(f"STEP 2.1 DEBUG: ChatroomManager has {len(self.chatrooms)} chatrooms in memory")
            logger.info(f"STEP 2.1 DEBUG: Available chatroom IDs: {list(self.chatrooms.keys())}")
            logger.info(f"STEP 2.1 DEBUG: Looking for chatroom_id: {chatroom_id} (type: {type(chatroom_id)})")
            
            chatroom = self.chatrooms.get(chatroom_id)
            if not chatroom:
                logger.error(f"STEP 2.1 FAILED: Chatroom {chatroom_id} not found in memory")
                logger.error(f"STEP 2.1 DEBUG: Chatroom details:")
                for cid, room in self.chatrooms.items():
                    logger.error(f"  - ID: {cid} (type: {type(cid)}), Users: {room.user1.user_id if room.user1 else 'None'}, {room.user2.user_id if room.user2 else 'None'}")
                return []
            
            logger.info(f"STEP 2.2: Loading messages from database for chatroom {chatroom_id}")
            
            # Load messages on-demand from database using message_ids
            message_ids = chatroom.message_ids
            if not message_ids:
                logger.info(f"STEP 2.2: No message_ids found for chatroom {chatroom_id}")
                return []
            
            logger.info(f"STEP 2.2: Found {len(message_ids)} message_ids for chatroom {chatroom_id}")
            
            # Load messages from database by ID (using _id for O(log n) lookup)
            messages = []
            for message_id in message_ids:
                try:
                    # 使用_id字段查询，获得O(log n)的查询性能
                    message_data = await Database.find_one("messages", {"_id": message_id})
                    
                    if message_data:
                        # Get sender user instance for sender name
                        user_manager = UserManagement()
                        sender_user = user_manager.get_user_instance(message_data["message_sender_id"])
                        sender_name = sender_user.telegram_user_name if sender_user else f"User{message_data['message_sender_id']}"
                        
                        # Create message tuple: (message_content, datetime_utc, sender_id, sender_name)
                        message_tuple = (
                            message_data["message_content"],
                            message_data["message_send_time_in_utc"],
                            message_data["message_sender_id"],
                            sender_name
                        )
                        messages.append(message_tuple)
                        
                        logger.debug(f"STEP 2.2: Loaded message {message_id}")
                    else:
                        logger.warning(f"STEP 2.2: Message {message_id} not found in database")
                        
                except Exception as e:
                    logger.error(f"STEP 2.2: Error loading message {message_id}: {e}")
                    continue
            
            logger.info(f"STEP 2.2: Successfully loaded {len(messages)} messages from database")
            
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

    async def send_message(self, chatroom_id, sender_user_id, message_content) -> dict:
        """
        Send a message in the specified chatroom
        Creates Message instance, stores in chatroom, and saves to database
        Returns dict with success status and match_id
        """
        try:
            # 统一转换为int类型
            chatroom_id = int(chatroom_id)
            sender_user_id = int(sender_user_id)
            
            logger.info(f"SEND MSG STEP 1: Sending message in chatroom {chatroom_id} from user {sender_user_id}")
            
            # Get chatroom from memory
            chatroom = self.chatrooms.get(chatroom_id)
            if not chatroom:
                logger.error(f"SEND MSG STEP 1 FAILED: Chatroom {chatroom_id} not found in memory")
                return {"success": False, "match_id": None}
            
            logger.info(f"SEND MSG STEP 2: Getting sender user instance for user {sender_user_id}")
            
            # Get sender user instance
            user_manager = UserManagement()
            sender_user = user_manager.get_user_instance(sender_user_id)
            if not sender_user:
                logger.error(f"SEND MSG STEP 2 FAILED: Sender user {sender_user_id} not found")
                return {"success": False, "match_id": None}
            
            # Determine receiver user (the other user in the chatroom)
            if sender_user_id == chatroom.user1_id:
                receiver_user = chatroom.user2
                receiver_user_id = chatroom.user2_id
            elif sender_user_id == chatroom.user2_id:
                receiver_user = chatroom.user1
                receiver_user_id = chatroom.user1_id
            else:
                logger.error(f"SEND MSG STEP 2 FAILED: User {sender_user_id} not authorized for chatroom {chatroom_id}")
                return {"success": False, "match_id": None}
            
            if not receiver_user:
                logger.error(f"SEND MSG STEP 2 FAILED: Receiver user {receiver_user_id} not found")
                return {"success": False, "match_id": None}
            
            logger.info(f"SEND MSG STEP 3: Creating message from {sender_user_id} to {receiver_user_id}")
            
            # Create Message instance
            message = Message(sender_user, receiver_user, message_content, chatroom_id)
            
            logger.info(f"SEND MSG STEP 4: Saving message {message.message_id} to database")
            
            # Save message to database first
            save_success = await message.save_to_database()
            if not save_success:
                logger.error(f"SEND MSG STEP 4 FAILED: Could not save message {message.message_id} to database")
                return {"success": False, "match_id": chatroom.match_id}
            
            logger.info(f"SEND MSG STEP 5: Adding message {message.message_id} to chatroom {chatroom_id}")
            
            # Add message ID to chatroom (don't store message instance in memory)
            chatroom.message_ids.append(message.message_id)
            
            logger.info(f"SEND MSG STEP 6: Updating chatroom {chatroom_id} in database")
            
            # Save updated chatroom to database (to update message_ids)
            chatroom_save_success = await chatroom.save_to_database()
            if not chatroom_save_success:
                logger.warning(f"SEND MSG STEP 6 WARNING: Could not update chatroom {chatroom_id} in database, but message was saved")
            
            logger.info(f"SEND MSG SUCCESS: Message {message.message_id} sent successfully in chatroom {chatroom_id} with match_id {chatroom.match_id}")
            return {"success": True, "match_id": chatroom.match_id}
            
        except Exception as e:
            logger.error(f"SEND MSG FAILED: Error sending message in chatroom {chatroom_id}: {e}")
            return {"success": False, "match_id": None}

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
                    
                    # Messages are already saved to database when sent via send_message()
                    # No need to save them again here since chatroom.messages is empty
                    logger.info(f"Saved chatroom {chatroom_id} structure to database")
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
                
                # Messages are already saved to database when sent via send_message()
                # No need to save them again here since chatroom.messages is empty
                logger.info(f"Saved {success_count}/{total_chatrooms} chatrooms structure to database")
                return success_count == total_chatrooms
                
        except Exception as e:
            logger.error(f"Error saving chatroom history: {e}")
            return False