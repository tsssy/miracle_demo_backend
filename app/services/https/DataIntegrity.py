from typing import List, Set
from app.core.database import Database
from app.utils.my_logger import MyLogger
from app.services.https.MatchManager import MatchManager
from app.services.https.UserManagement import UserManagement
from app.services.https.ChatroomManager import ChatroomManager

logger = MyLogger("DataIntegrity")


class DataIntegrity:
    """
    数据完备性检查器单例，负责检查和清理不一致的数据
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.match_manager = MatchManager()
            cls._instance.user_manager = UserManagement()
            cls._instance.chatroom_manager = ChatroomManager()
            logger.info("DataIntegrity singleton instance created")
        return cls._instance
        
    async def check_and_clean_all_data(self) -> bool:
        """
        执行所有数据完备性检查和清理
        包括：Match数据、User match_ids、Chatroom数据、Message数据和最终数据库Message检查
        """
        try:
            logger.info("开始数据完备性检查...")
            
            # 1. 检查和清理Match数据
            await self.check_and_clean_matches()
            
            # 2. 检查和清理User的match_ids
            await self.check_and_clean_user_match_ids()
            
            # 3. 检查和清理Chatroom数据
            await self.check_and_clean_chatrooms()
            
            # 4. 检查和清理Message数据
            await self.check_and_clean_messages()
            
            # 5. 最终数据库Message完备性检查
            await self.check_and_clean_database_messages()
            
            logger.info("数据完备性检查完成")
            return True
            
        except Exception as e:
            logger.error(f"数据完备性检查过程中发生错误: {e}")
            return False
    
    async def check_and_clean_matches(self) -> bool:
        """
        检查MatchManager里的每一个Match实例，确保实例中的两个user都在UserManagement里存在
        如果有一个user不存在，该Match实例为非法实例，需要删除
        同时进行反向检查：确保用户的match_ids包含相应的match
        """
        try:
            logger.info("开始检查Match数据完备性...")
            
            invalid_match_ids = []
            valid_matches = []  # 存储有效的match，用于反向检查
            
            # 第一步：轮询MatchManager里的每一个Match实例，检查用户是否存在
            for match_id, match in self.match_manager.match_list.items():
                user_1_exists = self.user_manager.get_user_instance(match.user_id_1) is not None
                user_2_exists = self.user_manager.get_user_instance(match.user_id_2) is not None
                
                # 检查两个用户是否都存在
                if not user_1_exists or not user_2_exists:
                    logger.warning(f"发现非法Match {match_id}: user1({match.user_id_1})存在={user_1_exists}, user2({match.user_id_2})存在={user_2_exists}")
                    invalid_match_ids.append(match_id)
                else:
                    # 记录有效的match用于反向检查
                    valid_matches.append(match)
            
            # 删除非法的Match实例
            for match_id in invalid_match_ids:
                # 从内存中删除
                if match_id in self.match_manager.match_list:
                    del self.match_manager.match_list[match_id]
                    logger.info(f"从内存中删除非法Match {match_id}")
                
                # 从数据库中删除
                await Database.delete_one("matches", {"_id": match_id})
                logger.info(f"从数据库中删除非法Match {match_id}")
            
            # 第二步：反向检查 - 确保用户的match_ids包含相应的match
            updated_users_count = 0
            for match in valid_matches:
                match_id = match.match_id
                user_id_1 = match.user_id_1
                user_id_2 = match.user_id_2
                
                # 检查user1的match_ids
                user_1 = self.user_manager.get_user_instance(user_id_1)
                if user_1 and match_id not in user_1.match_ids:
                    user_1.match_ids.append(match_id)
                    await self.user_manager.save_to_database(user_id_1)
                    updated_users_count += 1
                    logger.info(f"为用户 {user_id_1} 添加缺失的match_id: {match_id}")
                
                # 检查user2的match_ids
                user_2 = self.user_manager.get_user_instance(user_id_2)
                if user_2 and match_id not in user_2.match_ids:
                    user_2.match_ids.append(match_id)
                    await self.user_manager.save_to_database(user_id_2)
                    updated_users_count += 1
                    logger.info(f"为用户 {user_id_2} 添加缺失的match_id: {match_id}")
            
            logger.info(f"Match数据检查完成，删除了 {len(invalid_match_ids)} 个非法Match，为 {updated_users_count} 个用户补充了缺失的match_id")
            return True
            
        except Exception as e:
            logger.error(f"检查Match数据时发生错误: {e}")
            return False
    
    async def check_and_clean_user_match_ids(self) -> bool:
        """
        检查UserManagement里的user实例，检查他们的match_ids里有没有match_id映射出的match不存在
        如果有，在UserManagement的user实例中，以及数据库中，删除该id
        """
        try:
            logger.info("开始检查User的match_ids数据完备性...")
            
            # 获取所有存在的match_ids
            existing_match_ids = set(self.match_manager.match_list.keys())
            
            # 轮询UserManagement里的user实例
            for user_id, user in self.user_manager.user_list.items():
                if hasattr(user, 'match_ids') and user.match_ids:
                    invalid_match_ids = []
                    
                    # 检查每个match_id是否存在对应的match
                    for match_id in user.match_ids:
                        if match_id not in existing_match_ids:
                            logger.warning(f"用户 {user_id} 的match_ids中发现不存在的match_id: {match_id}")
                            invalid_match_ids.append(match_id)
                    
                    # 从用户的match_ids中删除无效的match_id
                    for invalid_id in invalid_match_ids:
                        user.match_ids.remove(invalid_id)
                        logger.info(f"从用户 {user_id} 的match_ids中删除无效match_id: {invalid_id}")
                    
                    # 如果有删除操作，更新数据库中的用户数据
                    if invalid_match_ids:
                        await self.user_manager.save_to_database(user_id)  # 调用UserManagement的save_to_database方法
                        logger.info(f"更新用户 {user_id} 的数据库记录")
            
            logger.info("User match_ids数据检查完成")
            return True
            
        except Exception as e:
            logger.error(f"检查User match_ids数据时发生错误: {e}")
            return False
    
    async def check_and_clean_chatrooms(self) -> bool:
        """
        检查Chatroom列表，检查：
        1: 有没有user_id对应了不存在的user
        2: 有没有chatroom对应了不存在的match
        如果有，在内存和数据库中都把这个chatroom删除
        """
        try:
            logger.info("开始检查Chatroom数据完备性...")
            
            invalid_chatroom_ids = []
            
            # 获取所有存在的user_ids和match_ids
            existing_user_ids = set(self.user_manager.user_list.keys())
            existing_match_ids = set(self.match_manager.match_list.keys())
            
            # 轮询ChatroomManager内存中的所有chatroom
            for chatroom_id, chatroom in self.chatroom_manager.chatrooms.items():
                is_invalid = False
                
                # 检查chatroom中的user1_id和user2_id是否存在
                if chatroom.user1_id not in existing_user_ids:
                    logger.warning(f"Chatroom {chatroom_id} 包含不存在的user1_id: {chatroom.user1_id}")
                    is_invalid = True
                
                if chatroom.user2_id not in existing_user_ids:
                    logger.warning(f"Chatroom {chatroom_id} 包含不存在的user2_id: {chatroom.user2_id}")
                    is_invalid = True
                
                # 检查match_id是否存在 (match_id可能为None)
                if chatroom.match_id is not None and chatroom.match_id not in existing_match_ids:
                    logger.warning(f"Chatroom {chatroom_id} 对应不存在的match_id: {chatroom.match_id}")
                    is_invalid = True
                
                if is_invalid:
                    invalid_chatroom_ids.append(chatroom_id)
            
            # 删除无效的chatroom
            for chatroom_id in invalid_chatroom_ids:
                # 从内存中删除
                if chatroom_id in self.chatroom_manager.chatrooms:
                    del self.chatroom_manager.chatrooms[chatroom_id]
                    logger.info(f"从内存中删除无效Chatroom {chatroom_id}")
                
                # 从数据库中删除
                await Database.delete_one("chatrooms", {"_id": chatroom_id})
                logger.info(f"从数据库中删除无效Chatroom {chatroom_id}")
            
            logger.info(f"Chatroom数据检查完成，删除了 {len(invalid_chatroom_ids)} 个无效Chatroom")
            return True
            
        except Exception as e:
            logger.error(f"检查Chatroom数据时发生错误: {e}")
            return False
    
    async def check_and_clean_messages(self) -> bool:
        """
        检查message列表，主要检查message里的chatroom_id是否存在，如果不存在，删除
        """
        try:
            logger.info("开始检查Message数据完备性...")
            
            # 获取所有存在的chatroom_ids (从ChatroomManager内存中获取)
            existing_chatroom_ids = set(self.chatroom_manager.chatrooms.keys())
            
            # 获取所有message数据
            messages_data = await Database.find("messages")
            invalid_message_ids = []
            
            for message_data in messages_data:
                message_id = message_data.get("_id") or message_data.get("message_id")
                chatroom_id = message_data.get("chatroom_id")
                
                # 检查chatroom_id是否存在于ChatroomManager中
                if chatroom_id and chatroom_id not in existing_chatroom_ids:
                    logger.warning(f"Message {message_id} 包含不存在的chatroom_id: {chatroom_id}")
                    invalid_message_ids.append(message_id)
            
            # 删除无效的message
            for message_id in invalid_message_ids:
                await Database.delete_one("messages", {"_id": message_id})
                logger.info(f"从数据库中删除无效Message {message_id}")
            
            # 反向检查：检查chatroom的message_ids中是否有指向不存在的message
            await self._check_and_clean_chatroom_message_ids()
            
            logger.info(f"Message数据检查完成，删除了 {len(invalid_message_ids)} 个无效Message")
            return True
            
        except Exception as e:
            logger.error(f"检查Message数据时发生错误: {e}")
            return False
    
    async def _check_and_clean_chatroom_message_ids(self) -> bool:
        """
        检查chatroom的message_ids中是否有指向不存在的message，如果有则清理
        """
        try:
            logger.info("开始检查Chatroom的message_ids完备性...")
            
            # 获取所有存在的message_ids
            messages_data = await Database.find("messages")
            existing_message_ids = set()
            for message_data in messages_data:
                message_id = message_data.get("_id") or message_data.get("message_id")
                if message_id:
                    existing_message_ids.add(message_id)
            
            updated_chatroom_count = 0
            
            # 检查每个chatroom的message_ids
            for chatroom_id, chatroom in self.chatroom_manager.chatrooms.items():
                if hasattr(chatroom, 'message_ids') and chatroom.message_ids:
                    invalid_message_ids = []
                    
                    # 检查每个message_id是否存在
                    for message_id in chatroom.message_ids:
                        if message_id not in existing_message_ids:
                            logger.warning(f"Chatroom {chatroom_id} 的message_ids中发现不存在的message_id: {message_id}")
                            invalid_message_ids.append(message_id)
                    
                    # 从chatroom的message_ids中删除无效的message_id
                    if invalid_message_ids:
                        for invalid_id in invalid_message_ids:
                            chatroom.message_ids.remove(invalid_id)
                            logger.info(f"从Chatroom {chatroom_id} 的message_ids中删除无效message_id: {invalid_id}")
                        
                        # 更新数据库中的chatroom数据
                        await chatroom.save_to_database()
                        updated_chatroom_count += 1
                        logger.info(f"更新Chatroom {chatroom_id} 的数据库记录")
            
            logger.info(f"Chatroom message_ids检查完成，更新了 {updated_chatroom_count} 个Chatroom")
            return True
            
        except Exception as e:
            logger.error(f"检查Chatroom message_ids时发生错误: {e}")
            return False
    
    async def check_and_clean_database_messages(self) -> bool:
        """
        最终数据库Message完备性检查
        检查数据库中每个message的：
        1: message_sender_id和message_receiver_id是否对应存在的user
        2: chatroom_id是否对应存在的chatroom
        如果不存在就删除该message
        """
        try:
            logger.info("开始最终数据库Message完备性检查...")
            
            # 获取所有存在的user_ids和chatroom_ids
            existing_user_ids = set(self.user_manager.user_list.keys())
            existing_chatroom_ids = set(self.chatroom_manager.chatrooms.keys())
            
            # 获取数据库中所有message数据
            messages_data = await Database.find("messages")
            invalid_message_ids = []
            
            for message_data in messages_data:
                message_id = message_data.get("_id") or message_data.get("message_id")
                sender_id = message_data.get("message_sender_id")
                receiver_id = message_data.get("message_receiver_id")
                chatroom_id = message_data.get("chatroom_id")
                
                is_invalid = False
                
                # 检查message_sender_id是否存在
                if sender_id and sender_id not in existing_user_ids:
                    logger.warning(f"Message {message_id} 包含不存在的message_sender_id: {sender_id}")
                    is_invalid = True
                
                # 检查message_receiver_id是否存在
                if receiver_id and receiver_id not in existing_user_ids:
                    logger.warning(f"Message {message_id} 包含不存在的message_receiver_id: {receiver_id}")
                    is_invalid = True
                
                # 检查chatroom_id是否存在
                if chatroom_id and chatroom_id not in existing_chatroom_ids:
                    logger.warning(f"Message {message_id} 包含不存在的chatroom_id: {chatroom_id}")
                    is_invalid = True
                
                if is_invalid:
                    invalid_message_ids.append(message_id)
            
            # 删除无效的message
            for message_id in invalid_message_ids:
                await Database.delete_one("messages", {"_id": message_id})
                logger.info(f"从数据库中删除无效Message {message_id}")
            
            logger.info(f"最终数据库Message检查完成，删除了 {len(invalid_message_ids)} 个无效Message")
            return True
            
        except Exception as e:
            logger.error(f"最终数据库Message检查时发生错误: {e}")
            return False
    
    async def run_integrity_check(self) -> dict:
        """
        运行完整的数据完备性检查，返回检查结果统计
        """
        try:
            logger.info("启动数据完备性检查...")
            
            result = {
                "success": True,
                "checks_completed": 0,
                "total_checks": 5,
                "errors": []
            }
            
            # 执行各项检查
            checks = [
                ("matches", self.check_and_clean_matches),
                ("user_match_ids", self.check_and_clean_user_match_ids),
                ("chatrooms", self.check_and_clean_chatrooms),
                ("messages", self.check_and_clean_messages),
                ("database_messages", self.check_and_clean_database_messages)
            ]
            
            for check_name, check_func in checks:
                try:
                    success = await check_func()
                    if success:
                        result["checks_completed"] += 1
                        logger.info(f"{check_name} 检查完成")
                    else:
                        result["errors"].append(f"{check_name} 检查失败")
                        logger.error(f"{check_name} 检查失败")
                except Exception as e:
                    result["errors"].append(f"{check_name} 检查异常: {str(e)}")
                    logger.error(f"{check_name} 检查异常: {e}")
            
            if result["checks_completed"] != result["total_checks"]:
                result["success"] = False
            
            logger.info(f"数据完备性检查完成: {result['checks_completed']}/{result['total_checks']} 项检查成功")
            return result
            
        except Exception as e:
            logger.error(f"数据完备性检查过程发生严重错误: {e}")
            return {
                "success": False,
                "checks_completed": 0,
                "total_checks": 5,
                "errors": [f"严重错误: {str(e)}"]
            }
    
    async def run_database_only_integrity_check(self) -> dict:
        """
        仅对数据库进行完备性检查，不涉及内存管理器
        这是一个高复杂度操作，仅用于手动脚本执行
        """
        try:
            logger.info("启动数据库级别完备性检查...")
            
            result = {
                "success": True,
                "checks_completed": 0,
                "total_checks": 5,
                "errors": [],
                "deleted_records": {
                    "matches": 0,
                    "users": 0,
                    "chatrooms": 0,
                    "messages": 0
                },
                "updated_records": {
                    "users": 0,
                    "chatrooms": 0
                }
            }
            
            # 执行各项数据库检查
            checks = [
                ("database_matches", self._check_database_matches),
                ("database_user_match_ids", self._check_database_user_match_ids),
                ("database_chatrooms", self._check_database_chatrooms),
                ("database_messages", self._check_database_messages),
                ("database_chatroom_message_ids", self._check_database_chatroom_message_ids)
            ]
            
            for check_name, check_func in checks:
                try:
                    check_result = await check_func()
                    if check_result["success"]:
                        result["checks_completed"] += 1
                        # 累加删除的记录数
                        for key, count in check_result.get("deleted", {}).items():
                            if key in result["deleted_records"]:
                                result["deleted_records"][key] += count
                        # 累加更新的记录数
                        if "updated_users" in check_result:
                            result["updated_records"]["users"] += check_result["updated_users"]
                        logger.info(f"{check_name} 数据库检查完成")
                    else:
                        result["errors"].append(f"{check_name} 数据库检查失败")
                        logger.error(f"{check_name} 数据库检查失败")
                except Exception as e:
                    result["errors"].append(f"{check_name} 数据库检查异常: {str(e)}")
                    logger.error(f"{check_name} 数据库检查异常: {e}")
            
            if result["checks_completed"] != result["total_checks"]:
                result["success"] = False
            
            logger.info(f"数据库级别完备性检查完成: {result['checks_completed']}/{result['total_checks']} 项检查成功")
            logger.info(f"删除记录统计: {result['deleted_records']}")
            logger.info(f"更新记录统计: {result['updated_records']}")
            return result
            
        except Exception as e:
            logger.error(f"数据库级别完备性检查发生严重错误: {e}")
            return {
                "success": False,
                "checks_completed": 0,
                "total_checks": 5,
                "errors": [f"严重错误: {str(e)}"],
                "deleted_records": {
                    "matches": 0,
                    "users": 0,
                    "chatrooms": 0,
                    "messages": 0
                },
                "updated_records": {
                    "users": 0,
                    "chatrooms": 0
                }
            }
    
    async def _check_database_matches(self) -> dict:
        """检查数据库中matches表的数据完备性"""
        try:
            logger.info("开始检查数据库matches表...")
            
            # 获取所有用户数据
            users_data = await Database.find("users")
            existing_user_ids = set(user["_id"] for user in users_data)
            users_dict = {user["_id"]: user for user in users_data}  # 用于快速查找用户数据
            
            # 获取所有matches
            matches_data = await Database.find("matches")
            invalid_match_ids = []
            valid_matches = []  # 存储有效的match，用于反向检查
            
            # 第一步：检查match中的用户是否存在
            for match_data in matches_data:
                match_id = match_data.get("_id")
                user_id_1 = match_data.get("user_id_1")
                user_id_2 = match_data.get("user_id_2")
                
                # 检查两个用户是否都存在
                if user_id_1 not in existing_user_ids or user_id_2 not in existing_user_ids:
                    logger.warning(f"数据库中发现无效Match {match_id}: user1({user_id_1})存在={user_id_1 in existing_user_ids}, user2({user_id_2})存在={user_id_2 in existing_user_ids}")
                    invalid_match_ids.append(match_id)
                else:
                    # 记录有效的match用于反向检查
                    valid_matches.append({
                        "match_id": match_id,
                        "user_id_1": user_id_1,
                        "user_id_2": user_id_2
                    })
            
            # 删除无效matches
            deleted_count = 0
            for match_id in invalid_match_ids:
                await Database.delete_one("matches", {"_id": match_id})
                deleted_count += 1
                logger.info(f"从数据库删除无效Match {match_id}")
            
            # 第二步：反向检查 - 确保用户的match_ids包含相应的match
            updated_users_count = 0
            for match in valid_matches:
                match_id = match["match_id"]
                user_id_1 = match["user_id_1"]
                user_id_2 = match["user_id_2"]
                
                # 检查user1的match_ids
                user1_data = users_dict.get(user_id_1)
                if user1_data:
                    user1_match_ids = user1_data.get("match_ids", [])
                    if match_id not in user1_match_ids:
                        # 添加match_id到用户的match_ids列表
                        user1_match_ids.append(match_id)
                        await Database.update_one(
                            "users",
                            {"_id": user_id_1},
                            {"$set": {"match_ids": user1_match_ids}}
                        )
                        updated_users_count += 1
                        logger.info(f"为用户 {user_id_1} 添加缺失的match_id: {match_id}")
                
                # 检查user2的match_ids
                user2_data = users_dict.get(user_id_2)
                if user2_data:
                    user2_match_ids = user2_data.get("match_ids", [])
                    if match_id not in user2_match_ids:
                        # 添加match_id到用户的match_ids列表
                        user2_match_ids.append(match_id)
                        await Database.update_one(
                            "users",
                            {"_id": user_id_2},
                            {"$set": {"match_ids": user2_match_ids}}
                        )
                        updated_users_count += 1
                        logger.info(f"为用户 {user_id_2} 添加缺失的match_id: {match_id}")
            
            logger.info(f"数据库matches检查完成，删除了 {deleted_count} 个无效Match，为 {updated_users_count} 个用户补充了缺失的match_id")
            return {"success": True, "deleted": {"matches": deleted_count}, "updated_users": updated_users_count}
            
        except Exception as e:
            logger.error(f"检查数据库matches时发生错误: {e}")
            return {"success": False, "deleted": {"matches": 0}, "updated_users": 0}
    
    async def _check_database_user_match_ids(self) -> dict:
        """检查数据库中users表的match_ids完备性"""
        try:
            logger.info("开始检查数据库users表的match_ids...")
            
            # 获取所有match_ids
            matches_data = await Database.find("matches")
            existing_match_ids = set(match["_id"] for match in matches_data)
            
            # 获取所有用户
            users_data = await Database.find("users")
            updated_count = 0
            
            for user_data in users_data:
                user_id = user_data.get("_id")
                match_ids = user_data.get("match_ids", [])
                
                if match_ids:
                    invalid_match_ids = []
                    
                    # 检查每个match_id是否存在
                    for match_id in match_ids:
                        if match_id not in existing_match_ids:
                            logger.warning(f"数据库用户 {user_id} 的match_ids中发现不存在的match_id: {match_id}")
                            invalid_match_ids.append(match_id)
                    
                    # 更新用户的match_ids
                    if invalid_match_ids:
                        new_match_ids = [mid for mid in match_ids if mid not in invalid_match_ids]
                        await Database.update_one(
                            "users",
                            {"_id": user_id},
                            {"$set": {"match_ids": new_match_ids}}
                        )
                        updated_count += 1
                        logger.info(f"更新数据库用户 {user_id} 的match_ids，删除了 {len(invalid_match_ids)} 个无效match_id")
            
            logger.info(f"数据库用户match_ids检查完成，更新了 {updated_count} 个用户")
            return {"success": True, "deleted": {"users": updated_count}}
            
        except Exception as e:
            logger.error(f"检查数据库用户match_ids时发生错误: {e}")
            return {"success": False, "deleted": {"users": 0}}
    
    async def _check_database_chatrooms(self) -> dict:
        """检查数据库中chatrooms表的数据完备性"""
        try:
            logger.info("开始检查数据库chatrooms表...")
            
            # 获取所有用户ID和match_ids
            users_data = await Database.find("users")
            existing_user_ids = set(user["_id"] for user in users_data)
            
            matches_data = await Database.find("matches")
            existing_match_ids = set(match["_id"] for match in matches_data)
            
            # 获取所有chatrooms
            chatrooms_data = await Database.find("chatrooms")
            invalid_chatroom_ids = []
            
            for chatroom_data in chatrooms_data:
                chatroom_id = chatroom_data.get("_id")
                user1_id = chatroom_data.get("user1_id")
                user2_id = chatroom_data.get("user2_id")
                match_id = chatroom_data.get("match_id")
                
                is_invalid = False
                
                # 检查用户是否存在
                if user1_id not in existing_user_ids:
                    logger.warning(f"数据库Chatroom {chatroom_id} 包含不存在的user1_id: {user1_id}")
                    is_invalid = True
                
                if user2_id not in existing_user_ids:
                    logger.warning(f"数据库Chatroom {chatroom_id} 包含不存在的user2_id: {user2_id}")
                    is_invalid = True
                
                # 检查match_id是否存在
                if match_id is not None and match_id not in existing_match_ids:
                    logger.warning(f"数据库Chatroom {chatroom_id} 对应不存在的match_id: {match_id}")
                    is_invalid = True
                
                if is_invalid:
                    invalid_chatroom_ids.append(chatroom_id)
            
            # 删除无效chatrooms
            deleted_count = 0
            for chatroom_id in invalid_chatroom_ids:
                await Database.delete_one("chatrooms", {"_id": chatroom_id})
                deleted_count += 1
                logger.info(f"从数据库删除无效Chatroom {chatroom_id}")
            
            logger.info(f"数据库chatrooms检查完成，删除了 {deleted_count} 个无效Chatroom")
            return {"success": True, "deleted": {"chatrooms": deleted_count}}
            
        except Exception as e:
            logger.error(f"检查数据库chatrooms时发生错误: {e}")
            return {"success": False, "deleted": {"chatrooms": 0}}
    
    async def _check_database_messages(self) -> dict:
        """检查数据库中messages表的数据完备性"""
        try:
            logger.info("开始检查数据库messages表...")
            
            # 获取所有用户ID和chatroom_ids
            users_data = await Database.find("users")
            existing_user_ids = set(user["_id"] for user in users_data)
            
            chatrooms_data = await Database.find("chatrooms")
            existing_chatroom_ids = set(chatroom["_id"] for chatroom in chatrooms_data)
            
            # 获取所有messages
            messages_data = await Database.find("messages")
            invalid_message_ids = []
            
            for message_data in messages_data:
                message_id = message_data.get("_id")
                sender_id = message_data.get("message_sender_id")
                receiver_id = message_data.get("message_receiver_id")
                chatroom_id = message_data.get("chatroom_id")
                
                is_invalid = False
                
                # 检查发送者是否存在
                if sender_id and sender_id not in existing_user_ids:
                    logger.warning(f"数据库Message {message_id} 包含不存在的message_sender_id: {sender_id}")
                    is_invalid = True
                
                # 检查接收者是否存在
                if receiver_id and receiver_id not in existing_user_ids:
                    logger.warning(f"数据库Message {message_id} 包含不存在的message_receiver_id: {receiver_id}")
                    is_invalid = True
                
                # 检查chatroom_id是否存在
                if chatroom_id and chatroom_id not in existing_chatroom_ids:
                    logger.warning(f"数据库Message {message_id} 包含不存在的chatroom_id: {chatroom_id}")
                    is_invalid = True
                
                if is_invalid:
                    invalid_message_ids.append(message_id)
            
            # 删除无效messages
            deleted_count = 0
            for message_id in invalid_message_ids:
                await Database.delete_one("messages", {"_id": message_id})
                deleted_count += 1
                logger.info(f"从数据库删除无效Message {message_id}")
            
            logger.info(f"数据库messages检查完成，删除了 {deleted_count} 个无效Message")
            return {"success": True, "deleted": {"messages": deleted_count}}
            
        except Exception as e:
            logger.error(f"检查数据库messages时发生错误: {e}")
            return {"success": False, "deleted": {"messages": 0}}
    
    async def _check_database_chatroom_message_ids(self) -> dict:
        """检查数据库中chatrooms表的message_ids完备性"""
        try:
            logger.info("开始检查数据库chatrooms表的message_ids...")
            
            # 获取所有message_ids
            messages_data = await Database.find("messages")
            existing_message_ids = set(message["_id"] for message in messages_data)
            
            # 获取所有chatrooms
            chatrooms_data = await Database.find("chatrooms")
            updated_count = 0
            
            for chatroom_data in chatrooms_data:
                chatroom_id = chatroom_data.get("_id")
                message_ids = chatroom_data.get("message_ids", [])
                
                if message_ids:
                    invalid_message_ids = []
                    
                    # 检查每个message_id是否存在
                    for message_id in message_ids:
                        if message_id not in existing_message_ids:
                            logger.warning(f"数据库Chatroom {chatroom_id} 的message_ids中发现不存在的message_id: {message_id}")
                            invalid_message_ids.append(message_id)
                    
                    # 更新chatroom的message_ids
                    if invalid_message_ids:
                        new_message_ids = [mid for mid in message_ids if mid not in invalid_message_ids]
                        await Database.update_one(
                            "chatrooms",
                            {"_id": chatroom_id},
                            {"$set": {"message_ids": new_message_ids}}
                        )
                        updated_count += 1
                        logger.info(f"更新数据库Chatroom {chatroom_id} 的message_ids，删除了 {len(invalid_message_ids)} 个无效message_id")
            
            logger.info(f"数据库chatroom message_ids检查完成，更新了 {updated_count} 个chatroom")
            return {"success": True, "deleted": {"chatrooms": updated_count}}
            
        except Exception as e:
            logger.error(f"检查数据库chatroom message_ids时发生错误: {e}")
            return {"success": False, "deleted": {"chatrooms": 0}}