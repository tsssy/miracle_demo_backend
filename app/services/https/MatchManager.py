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

    # 🔧 MODIFIED: 新增方法 - 批量匹配接口
    async def get_new_matches_for_everyone(self, user_id: Optional[int] = None, print_message: bool = False) -> dict:
        """
        为所有女性用户或指定女性用户创建新匹配
        
        Args:
            user_id: 可选的用户ID，如果提供则只为该用户匹配
            print_message: 是否在消息中包含详细信息
            
        Returns:
            dict: 包含success状态和message信息的字典
        """
        try:
            from app.services.https.UserManagement import UserManagement
            from app.services.https.N8nWebhookManager import N8nWebhookManager
            
            user_manager = UserManagement()
            n8n_manager = N8nWebhookManager()
            
            # 第一步：参数验证和确定目标女性用户列表
            if user_id is not None:
                # 检查指定用户是否存在
                target_user = user_manager.get_user_instance(user_id)
                if not target_user:
                    return {"success": False, "message": "错误：指定的用户不存在"}
                
                # 检查用户性别，只能给女性用户匹配（1代表女性）
                if target_user.gender != 1:  # 1代表女性
                    return {"success": False, "message": "错误：只能给女性用户匹配"}
                
                female_users_to_match = [target_user]
                logger.info(f"开始为指定女性用户 {user_id} 创建匹配")
            else:
                # 获取所有女性用户（gender == 1）
                female_user_dict = user_manager.get_female_user_list()
                female_users_to_match = list(female_user_dict.values())
                logger.info(f"开始为所有 {len(female_users_to_match)} 个女性用户创建匹配")
            
            # 第二步：遍历女性用户进行匹配
            successful_matches = []
            failed_matches = []
            
            for female_user in female_users_to_match:
                try:
                    logger.info(f"正在为女性用户 {female_user.user_id} ({female_user.telegram_user_name}) 请求匹配...")
                    
                    # 调用N8n获取匹配的男性用户
                    match_results = await n8n_manager.request_matches(
                        user_id=female_user.user_id, 
                        num_of_matches=1
                    )
                    
                    if match_results and len(match_results) > 0:
                        match_data = match_results[0]  # 取第一个匹配结果
                        
                        # 🔧 MODIFIED: 修复description为空问题 - 使用N8n实际返回的字段名
                        # 从匹配结果中提取信息（根据N8n实际返回字段调整）
                        male_user_id = match_data.get("matched_user_id", match_data.get("user_id"))
                        reason_to_female = match_data.get("reason_of_match_given_to_self_user", "")
                        reason_to_male = match_data.get("reason_of_match_given_to_matched_user", "")
                        match_score = match_data.get("match_score", match_data.get("score", 0))
                        
                        # 验证男性用户是否存在
                        male_user = user_manager.get_user_instance(male_user_id)
                        if not male_user:
                            failed_matches.append({
                                "user_id": female_user.user_id,
                                "error": f"匹配的男性用户 {male_user_id} 不存在"
                            })
                            continue
                        
                        # 创建匹配
                        # 创建匹配
                        new_match = await self.create_match(
                            user_id_1=female_user.user_id,  # 女性用户作为user_id_1
                            user_id_2=male_user_id,         # 男性用户作为user_id_2
                            reason_1=reason_to_female,
                            reason_2=reason_to_male,
                            match_score=int(match_score)
                        )
                        
                        # 保存用户的match_ids更新到数据库
                        await user_manager.save_to_database(female_user.user_id)
                        await user_manager.save_to_database(male_user_id)
                        
                        successful_matches.append(new_match)
                        logger.info(f"成功创建匹配 {new_match.match_id}: {female_user.telegram_user_name} <-> {male_user.telegram_user_name}")
                        
                    else:
                        failed_matches.append({
                            "user_id": female_user.user_id,
                            "error": "N8n未返回匹配结果"
                        })
                        
                except Exception as e:
                    failed_matches.append({
                        "user_id": female_user.user_id,
                        "error": str(e)
                    })
                    logger.error(f"为用户 {female_user.user_id} 创建匹配时出错: {e}")
            
            # 第三步：构建返回消息
            total_female_users = len(female_users_to_match)
            successful_count = len(successful_matches)
            failed_count = len(failed_matches)
            
            message_parts = [f"一共匹配了 {successful_count}/{total_female_users} 个女性用户"]
            
            if failed_count > 0:
                message_parts.append(f"失败 {failed_count} 个")
            
            # 如果需要打印详细消息且有成功的匹配
            if print_message and successful_matches:
                message_parts.append("\n\n匹配详情表：")
                message_parts.append("=" * 50)
                
                for i, match in enumerate(successful_matches, 1):
                    # 获取用户信息
                    female_user = user_manager.get_user_instance(match.user_id_1)
                    male_user = user_manager.get_user_instance(match.user_id_2)
                    
                    # 构建详细信息
                    match_detail = f"""
【匹配 {i}】匹配ID: {match.match_id}
• 女性用户: {female_user.telegram_user_name} (ID: {female_user.user_id}, 性别: {'女' if female_user.gender == 1 else '男'})
• 男性用户: {male_user.telegram_user_name} (ID: {male_user.user_id}, 性别: {'男' if male_user.gender == 2 else '女'})
• 匹配分数: {match.match_score}
• 给女性的描述: {match.description_to_user_1}
• 给男性的描述: {match.description_to_user_2}
• 匹配时间: {match.match_time}
• 是否点赞: {'是' if match.is_liked else '否'}
• 互动游戏分数: {match.mutual_game_scores if match.mutual_game_scores else '无'}
• 聊天室ID: {match.chatroom_id if match.chatroom_id else '未创建'}
{'-' * 40}"""
                    message_parts.append(match_detail)
            
            # 如果有失败的匹配且需要详细信息
            if print_message and failed_matches:
                message_parts.append(f"\n\n失败的匹配 ({failed_count} 个)：")
                for i, failed in enumerate(failed_matches, 1):
                    user = user_manager.get_user_instance(failed["user_id"])
                    user_name = user.telegram_user_name if user else "未知用户"
                    message_parts.append(f"{i}. {user_name} (ID: {failed['user_id']}): {failed['error']}")
            
            final_message = "\n".join(message_parts)
            
            logger.info(f"匹配完成: 成功 {successful_count}, 失败 {failed_count}")
            return {"success": True, "message": final_message}
            
        except Exception as e:
            error_msg = f"执行匹配过程中发生错误: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}