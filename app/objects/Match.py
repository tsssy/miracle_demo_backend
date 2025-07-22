import time
from typing import Optional, Dict, Any
from app.core.database import Database
from app.utils.my_logger import MyLogger

logger = MyLogger("Match")


class Match:
    """
    匹配类，管理一个Match
    """
    _match_counter = 0
    _initialized = False
    
    @classmethod
    async def initialize_counter(cls):
        """
        从数据库初始化匹配计数器，确保不会产生重复ID
        """
        if cls._initialized:
            return
            
        try:
            # 查找数据库中最大的_id（match_id存储在_id字段中）
            matches = await Database.find("matches", sort=[("_id", -1)], limit=1)
            
            if matches:
                max_id = matches[0]["_id"]
                cls._match_counter = max_id
                logger.info(f"Match counter initialized from database: starting from {max_id}")
            else:
                cls._match_counter = 0
                logger.info("No existing matches found, starting counter from 0")
                
            cls._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize match counter: {e}")
            # 如果初始化失败，使用时间戳作为起始点以避免冲突
            cls._match_counter = int(time.time() * 1000000)  # 微秒时间戳
            cls._initialized = True
            logger.warning(f"Using timestamp as match counter starting point: {cls._match_counter}")
    
    def __init__(self, telegram_user_session_id_1: int, telegram_user_session_id_2: int, reason_to_id_1: str, reason_to_id_2: str, match_score: int, match_time: str):
        # 确保计数器已初始化
        if not Match._initialized:
            raise RuntimeError("Match counter not initialized. Call Match.initialize_counter() first.")
            
        Match._match_counter += 1
        self.match_id = Match._match_counter
        self.user_id_1 = telegram_user_session_id_1
        self.user_id_2 = telegram_user_session_id_2
        self.description_to_user_1 = reason_to_id_1  # String description
        self.description_to_user_2 = reason_to_id_2  # String description
        self.is_liked = False
        self.match_score = match_score
        self.mutual_game_scores = {}  # {session_id: {score: int, description: str, game_session_id: int}}
        self.chatroom_id = None
        self.match_time = match_time
        
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
        保存匹配到数据库，使用match_id作为_id主键
        """
        try:
            match_data = {
                "_id": self.match_id,  # 使用match_id作为MongoDB的_id主键
                "user_id_1": self.user_id_1,
                "user_id_2": self.user_id_2,
                "description_to_user_1": self.description_to_user_1,
                "description_to_user_2": self.description_to_user_2,
                "is_liked": self.is_liked,
                "match_score": self.match_score,
                "mutual_game_scores": self.mutual_game_scores,
                "chatroom_id": self.chatroom_id,
                "match_time": self.match_time
            }
            
            # 检查匹配是否已存在（基于_id查询，O(log n)复杂度）
            existing_match = await Database.find_one("matches", {"_id": self.match_id})
            
            if existing_match:
                # 更新现有匹配
                await Database.update_one(
                    "matches",
                    {"_id": self.match_id},
                    {"$set": {k: v for k, v in match_data.items() if k != "_id"}}  # 不更新_id字段
                )
                # logger.info(f"Updated match {self.match_id} in database")
            else:
                # 插入新匹配
                await Database.insert_one("matches", match_data)
                # logger.info(f"Saved new match {self.match_id} to database")
            
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
            "chatroom_id": self.chatroom_id,
            "match_time": self.match_time
        }