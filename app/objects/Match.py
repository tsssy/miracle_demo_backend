import time
from typing import Optional, Dict, Any
from app.core.database import Database
from app.utils.my_logger import MyLogger

logger = MyLogger("Match")


class Match:
    """
    匹配类，管理一个Match
    """
    def __init__(self, telegram_user_session_id_1: int, telegram_user_session_id_2: int, reason_to_id_1: str, reason_to_id_2: str, match_score: int):
        self.match_id = int(time.time() * 1000000)  # Generate unique match ID using timestamp
        self.user_id_1 = telegram_user_session_id_1
        self.user_id_2 = telegram_user_session_id_2
        self.description_to_user_1 = reason_to_id_1  # String description
        self.description_to_user_2 = reason_to_id_2  # String description
        self.is_liked = False
        self.match_score = match_score
        self.mutual_game_scores = {}  # {session_id: {score: int, description: str, game_session_id: int}}
        self.chatroom_id = None
        
        self.chatroom = None
        self.user_1 = None
        self.user_2 = None
        
        # Populate user instances from UserManagement
        self._populate_user_instances()
        
        logger.info(f"Created new match with ID: {self.match_id} between users {self.user_id_1} and {self.user_id_2}")

    def _populate_user_instances(self):
        """
        从UserManagement单例获取用户实例
        """
        try:
            from app.services.https.UserManagement import UserManagement
            user_manager = UserManagement()
            
            self.user_1 = user_manager.get_user_instance(self.user_id_1)
            self.user_2 = user_manager.get_user_instance(self.user_id_2)
            
            if self.user_1 is None:
                logger.warning(f"User {self.user_id_1} not found in UserManagement")
            if self.user_2 is None:
                logger.warning(f"User {self.user_id_2} not found in UserManagement")
                
        except Exception as e:
            logger.error(f"Error populating user instances: {e}")
            self.user_1 = None
            self.user_2 = None

    def get_target_user(self, user_id: int):
        """
        根据给定的user_id返回另一个用户实例
        """
        if user_id == self.user_id_1:
            return self.user_2
        elif user_id == self.user_id_2:
            return self.user_1
        else:
            logger.error(f"User ID {user_id} not found in match {self.match_id}")
            return None

    def get_reason_for_profile(self, user_id: int) -> Optional[str]:
        """
        获取针对特定用户的匹配原因
        """
        if user_id == self.user_id_1:
            return self.description_to_user_1
        elif user_id == self.user_id_2:
            return self.description_to_user_2
        else:
            logger.error(f"User ID {user_id} not found in match {self.match_id}")
            return None

    def get_match_id(self) -> int:
        """
        返回匹配ID
        """
        return self.match_id

    def toggle_like(self) -> bool:
        """
        切换喜欢状态
        """
        try:
            self.is_liked = not self.is_liked
            logger.info(f"Match {self.match_id} like status toggled to: {self.is_liked}")
            return True
        except Exception as e:
            logger.error(f"Error toggling like for match {self.match_id}: {e}")
            return False

    async def save_to_database(self) -> bool:
        """
        保存匹配到数据库
        """
        try:
            match_data = {
                "match_id": self.match_id,
                "user_id_1": self.user_id_1,
                "user_id_2": self.user_id_2,
                "description_to_user_1": self.description_to_user_1,
                "description_to_user_2": self.description_to_user_2,
                "is_liked": self.is_liked,
                "match_score": self.match_score,
                "mutual_game_scores": self.mutual_game_scores,
                "chatroom_id": self.chatroom_id,
                "created_at": time.time()
            }
            
            # Check if match already exists
            existing_match = await Database.find_one("matches", {"match_id": self.match_id})
            
            if existing_match:
                # Update existing match
                await Database.update_one(
                    "matches",
                    {"match_id": self.match_id},
                    {"$set": match_data}
                )
                # logger.info(f"Updated match {self.match_id} in database")
            else:
                # Insert new match
                await Database.insert_one("matches", match_data)
                logger.info(f"Saved new match {self.match_id} to database")
            
            return True
        except Exception as e:
            logger.error(f"Error saving match {self.match_id} to database: {e}")
            return False
    
    def get_target_user_id(self, user_id: int) -> Optional[int]:
        """
        获取目标用户ID
        """
        if user_id == self.user_id_1:
            return self.user_id_2
        elif user_id == self.user_id_2:
            return self.user_id_1
        else:
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        """
        return {
            "match_id": self.match_id,
            "user_id_1": self.user_id_1,
            "user_id_2": self.user_id_2,
            "description_to_user_1": self.description_to_user_1,
            "description_to_user_2": self.description_to_user_2,
            "is_liked": self.is_liked,
            "match_score": self.match_score,
            "mutual_game_scores": self.mutual_game_scores,
            "chatroom_id": self.chatroom_id
        }