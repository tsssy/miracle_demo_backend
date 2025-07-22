from typing import Optional, Dict, Any
from app.config import settings
from app.objects.Match import Match
from app.core.database import Database
from app.utils.my_logger import MyLogger
from datetime import datetime, timezone

logger = MyLogger("MatchManager")


class MatchManager:
    """
    匹配管理单例，负责管理所有匹配
    """
    _instance = None
    database_address = settings.MONGODB_URL

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.match_list = {}  # Dictionary to store matches by match_id
            logger.info("MatchManager singleton instance created")
        return cls._instance

    async def construct(self) -> bool:
        """
        Initialize MatchManager by initializing match counter and loading matches from database
        """
        try:
            # Initialize Match counter from database
            logger.info("MatchManager construct: Initializing Match counter...")
            await Match.initialize_counter()
            
            # Load existing matches from database
            logger.info("MatchManager construct: Loading matches from database...")
            matches_data = await Database.find("matches")
            logger.info(f"MatchManager construct: Found {len(matches_data)} matches in database")
            
            loaded_count = 0
            for match_data in matches_data:
                try:
                    match_id = match_data["_id"]  # match_id现在存储在_id字段中
                    user_id_1 = match_data["user_id_1"]
                    user_id_2 = match_data["user_id_2"]
                    
                    logger.info(f"MatchManager construct: Processing match {match_id} (users: {user_id_1}, {user_id_2})")
                    
                    # 创建Match实例但使用现有ID
                    # 先临时禁用初始化检查
                    Match._initialized = True
                    original_counter = Match._match_counter
                    
                    # 创建Match实例
                    match = Match(
                        telegram_user_session_id_1=user_id_1,
                        telegram_user_session_id_2=user_id_2,
                        reason_to_id_1=match_data.get("description_to_user_1", ""),
                        reason_to_id_2=match_data.get("description_to_user_2", ""),
                        match_score=match_data.get("match_score", 0),
                        match_time=match_data.get("match_time", "Unknown")
                    )
                    
                    # 恢复原始计数器并设置正确的match_id
                    Match._match_counter = original_counter
                    match.match_id = match_id
                    
                    # 设置其他属性
                    match.is_liked = match_data.get("is_liked", False)
                    match.mutual_game_scores = match_data.get("mutual_game_scores", {})
                    match.chatroom_id = match_data.get("chatroom_id")
                    
                    # 存储到内存
                    self.match_list[match_id] = match
                    loaded_count += 1
                    
                    logger.info(f"MatchManager construct: Successfully loaded match {match_id}")
                    
                except Exception as e:
                    logger.error(f"MatchManager construct: Error loading match from database: {e}")
                    continue
            
            logger.info(f"MatchManager construct: Loaded {loaded_count} matches from database")
            logger.info(f"MatchManager construct completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"MatchManager construct: Error constructing MatchManager: {e}")
            return False

    async def create_match(self, user_id_1: int, user_id_2: int, reason_1: str, reason_2: str, match_score: int) -> Match:
        """
        创建新的匹配
        """
        try:
            # Create new match instance
            new_match = Match(
                telegram_user_session_id_1=user_id_1,
                telegram_user_session_id_2=user_id_2,
                reason_to_id_1=reason_1,
                reason_to_id_2=reason_2,
                match_score=match_score,
                match_time=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            )
            
            # Store in memory
            self.match_list[new_match.match_id] = new_match
            
            # Add match_id to corresponding user instances
            from app.services.https.UserManagement import UserManagement
            user_manager = UserManagement()
            
            user_1 = user_manager.get_user_instance(user_id_1)
            user_2 = user_manager.get_user_instance(user_id_2)
            
            if user_1:
                if new_match.match_id not in user_1.match_ids:
                    user_1.match_ids.append(new_match.match_id)
                    logger.info(f"Added match {new_match.match_id} to user {user_id_1} match_ids")
            else:
                logger.warning(f"User {user_id_1} not found in UserManagement")
            
            if user_2:
                if new_match.match_id not in user_2.match_ids:
                    user_2.match_ids.append(new_match.match_id)
                    logger.info(f"Added match {new_match.match_id} to user {user_id_2} match_ids")
            else:
                logger.warning(f"User {user_id_2} not found in UserManagement")
            
            logger.info(f"Created match {new_match.match_id} between users {user_id_1} and {user_id_2}")
            return new_match
            
        except Exception as e:
            logger.error(f"Error creating match between users {user_id_1} and {user_id_2}: {e}")
            raise

    def get_match(self, match_id) -> Optional[Match]:
        """
        根据match_id获取匹配
        """
        try:
            # 统一转换为int类型
            match_id = int(match_id)
            
            match = self.match_list.get(match_id)
            if match:
                logger.info(f"Retrieved match {match_id}")
                return match
            else:
                logger.warning(f"Match {match_id} not found in memory")
                return None
        except Exception as e:
            logger.error(f"Error retrieving match {match_id}: {e}")
            return None

    def toggle_like(self, match_id: int) -> bool:
        """
        切换匹配的喜欢状态
        """
        try:
            match = self.get_match(match_id)
            if match:
                success = match.toggle_like()
                if success:
                    logger.info(f"Toggled like status for match {match_id}")
                return success
            else:
                logger.error(f"Cannot toggle like: Match {match_id} not found")
                return False
        except Exception as e:
            logger.error(f"Error toggling like for match {match_id}: {e}")
            return False

    async def save_to_database(self, match_id: Optional[int] = None) -> bool:
        """
        保存匹配到数据库
        如果没有指定match_id，则保存所有匹配
        """
        try:
            if match_id is not None:
                # Save specific match
                match = self.get_match(match_id)
                if match:
                    success = await match.save_to_database()
                    if success:
                        logger.info(f"Saved match {match_id} to database")
                    return success
                else:
                    logger.error(f"Cannot save: Match {match_id} not found")
                    return False
            else:
                # Save all matches
                success_count = 0
                total_matches = len(self.match_list)
                
                for match in self.match_list.values():
                    if await match.save_to_database():
                        success_count += 1
                
                logger.info(f"Saved {success_count}/{total_matches} matches to database")
                return success_count == total_matches
                
        except Exception as e:
            logger.error(f"Error saving matches to database: {e}")
            return False

    def get_match_info(self, user_id: int, match_id: int) -> Optional[Dict[str, Any]]:
        """
        获取匹配信息，返回对特定用户的视图
        """
        try:
            match = self.get_match(match_id)
            if not match:
                logger.error(f"Match {match_id} not found")
                return None
            
            # Get target user ID
            target_user_id = match.get_target_user_id(user_id)
            if target_user_id is None:
                logger.error(f"User {user_id} not found in match {match_id}")
                return None
            
            # Get description for the requesting user
            description_for_user = match.get_reason_for_profile(user_id)
            
            match_info = {
                "target_user_id": target_user_id,
                "description_for_target": description_for_user,
                "is_liked": match.is_liked,
                "match_score": match.match_score,
                "mutual_game_scores": match.mutual_game_scores,
                "chatroom_id": match.chatroom_id
            }
            
            logger.info(f"Retrieved match info for user {user_id} in match {match_id}")
            return match_info
            
        except Exception as e:
            logger.error(f"Error getting match info for user {user_id} in match {match_id}: {e}")
            return None
    
    def get_user_matches(self, user_id: int) -> list[Match]:
        """
        获取用户的所有匹配
        """
        try:
            user_matches = []
            for match in self.match_list.values():
                if match.user_id_1 == user_id or match.user_id_2 == user_id:
                    user_matches.append(match)
            
            logger.info(f"Found {len(user_matches)} matches for user {user_id}")
            return user_matches
            
        except Exception as e:
            logger.error(f"Error getting matches for user {user_id}: {e}")
            return []
    
    async def load_from_database(self) -> bool:
        """
        从数据库加载所有匹配
        """
        try:
            matches_data = await Database.find("matches")
            loaded_count = 0
            
            for match_data in matches_data:
                try:
                    # Reconstruct Match object from database data
                    match = Match(
                        telegram_user_session_id_1=match_data["user_id_1"],
                        telegram_user_session_id_2=match_data["user_id_2"],
                        reason_to_id_1=match_data["description_to_user_1"],
                        reason_to_id_2=match_data["description_to_user_2"],
                        match_score=match_data["match_score"],
                        match_time=match_data.get("match_time", "Unknown")
                    )
                    
                    # Restore additional properties
                    match.match_id = match_data["match_id"]
                    match.is_liked = match_data.get("is_liked", False)
                    match.mutual_game_scores = match_data.get("mutual_game_scores", {})
                    match.chatroom_id = match_data.get("chatroom_id")
                    
                    # User instances are automatically populated in Match.__init__()
                    
                    # Store in memory
                    self.match_list[match.match_id] = match
                    loaded_count += 1
                    
                except Exception as e:
                    logger.error(f"Error reconstructing match from database data: {e}")
                    continue
            
            logger.info(f"Loaded {loaded_count} matches from database")
            return True
            
        except Exception as e:
            logger.error(f"Error loading matches from database: {e}")
            return False