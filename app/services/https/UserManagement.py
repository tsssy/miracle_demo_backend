from fastapi import HTTPException, status
from app.config import settings
from app.core.database import Database
from app.objects.User import User


class UserManagement:
    """
    用户管理单例，负责管理所有用户
    属性：
        user_list: dict{user_id, User}  # 所有用户
        male_user_list: dict{user_id, User}
        female_user_list: dict{user_id, User}
        database_address: str
    """
    _instance = None
    _initialized = False
    database_address = settings.MONGODB_URL

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.user_list = {}
            cls._instance.male_user_list = {}
            cls._instance.female_user_list = {}
            cls._instance.user_counter = 0  # 用户计数器
        return cls._instance

    async def initialize_from_database(self):
        """从数据库初始化用户缓存 [内部方法，非API调用]"""
        if UserManagement._initialized:
            return
        
        # 从数据库获取所有用户
        users_from_db = await Database.find("users", {})
        loaded_count = 0
        
        for user_data in users_from_db:
            # 创建User对象
            user = User(
                telegram_user_name=user_data.get("telegram_user_name"),
                gender=user_data.get("gender"),
                user_id=user_data.get("_id")
            )
            user.age = user_data.get("age")
            user.target_gender = user_data.get("target_gender")
            user.user_personality_summary = user_data.get("user_personality_summary")
            user.match_ids = user_data.get("match_ids", [])
            user.blocked_user_ids = user_data.get("blocked_user_ids", [])
            
            # 添加到缓存列表
            user_id = user.user_id
            self.user_list[user_id] = user
            
            # 根据性别分类
            if user.gender == 1:
                self.male_user_list[user_id] = user
            elif user.gender == 2:
                self.female_user_list[user_id] = user
            
            loaded_count += 1
        
        # 更新用户计数器
        self.user_counter = len(self.user_list)
        UserManagement._initialized = True
        
        # 打印加载统计信息
        print(f"UserManagement: 成功从数据库加载 {loaded_count} 个用户到内存")
        print(f"UserManagement: 男性用户: {len(self.male_user_list)}, 女性用户: {len(self.female_user_list)}")

    # 创建新用户 [API调用]
    def create_new_user(self, telegram_user_name, telegram_user_id, gender):
        user_id = int(telegram_user_id) # 用户id就是tg_id
        user = User(telegram_user_name=telegram_user_name, gender=gender, user_id=user_id)
        self.user_list[user_id] = user
        if gender == 1:
            self.male_user_list[user_id] = user
        elif gender == 2:
            self.female_user_list[user_id] = user
        
        # 更新用户计数器
        self.user_counter = len(self.user_list)
        return user_id

    # 编辑用户年龄 [API调用]
    def edit_user_age(self, user_id, age):
        user = self.user_list.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.edit_data(age=age)
        return True

    # 编辑用户目标性别 [API调用]
    def edit_target_gender(self, user_id, target_gender):
        user = self.user_list.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.edit_data(target_gender=target_gender)
        return True

    # 编辑用户总结 [API调用]
    def edit_summary(self, user_id, summary):
        user = self.user_list.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.edit_data(user_personality_summary=summary)
        return True

    # 保存用户信息到数据库 [API调用]
    async def save_to_database(self, user_id=None):
        """
        保存用户到MongoDB，并使用user_id作为文档的_id。
        如果指定了user_id，则保存该用户；如果没有指定，则保存所有内存中的用户。
        如果用户在数据库中已存在，则更新；否则，创建新记录。
        [API调用]
        """
        if user_id is None:
            # 保存所有内存中的用户
            success_count = 0
            total_users = len(self.user_list)
            
            for user in self.user_list.values():
                try:
                    # 使用 user_id 作为 MongoDB 的 _id
                    user_dict = {
                        "_id": user.user_id,
                        "telegram_user_name": user.telegram_user_name,
                        "gender": user.gender,
                        "age": user.age,
                        "target_gender": user.target_gender,
                        "user_personality_summary": user.user_personality_summary,
                        "match_ids": user.match_ids,
                        "blocked_user_ids": user.blocked_user_ids,
                    }

                    # 检查用户是否已在数据库中
                    existing_user_in_db = await Database.find_one("users", {"_id": user.user_id})

                    if existing_user_in_db:
                        # 如果存在，则更新。$set 的内容不能包含 _id
                        update_payload = user_dict.copy()
                        del update_payload["_id"]
                        await Database.update_one(
                            "users",
                            {"_id": user.user_id},
                            {"$set": update_payload}
                        )
                    else:
                        # 如果不存在，则插入 (包含 _id)
                        await Database.insert_one("users", user_dict)
                    
                    success_count += 1
                    
                except Exception as e:
                    # 记录单个用户保存失败，但继续保存其他用户
                    print(f"保存用户 {user.user_id} 失败: {e}")
                    continue
            
            return success_count == total_users
        else:
            # 保存指定的用户
            user = self.user_list.get(user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="要保存的用户在内存中不存在")

            # 使用 user_id 作为 MongoDB 的 _id
            user_dict = {
                "_id": user.user_id,
                "telegram_user_name": user.telegram_user_name,
                "gender": user.gender,
                "age": user.age,
                "target_gender": user.target_gender,
                "user_personality_summary": user.user_personality_summary,
                "match_ids": user.match_ids,
                "blocked_user_ids": user.blocked_user_ids,
            }

            # 检查用户是否已在数据库中
            existing_user_in_db = await Database.find_one("users", {"_id": user.user_id})

            if existing_user_in_db:
                # 如果存在，则更新。$set 的内容不能包含 _id
                update_payload = user_dict.copy()
                del update_payload["_id"]
                await Database.update_one(
                    "users",
                    {"_id": user.user_id},
                    {"$set": update_payload}
                )
            else:
                # 如果不存在，则插入 (包含 _id)
                await Database.insert_one("users", user_dict)

            return True

    # 根据id获取用户信息 [API调用]
    def get_user_info_with_user_id(self, user_id):
        # Check if input is string and all numbers, convert to int if so
        if isinstance(user_id, str) and user_id.isdigit():
            user_id = int(user_id)
        
        user = self.user_list.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        return {
            "telegram_user_name": user.telegram_user_name,
            "telegram_id": user.user_id,
            "gender": user.gender,
            "age": user.age,
            "target_gender": user.target_gender,
            "user_personality_trait": user.user_personality_summary,
            "user_id": user.user_id,
            "match_ids": user.match_ids
        }

    # 获取用户统计信息 [内部方法，非API调用]
    def get_user_statistics(self):
        """获取用户统计信息 [内部方法，非API调用]"""
        return {
            "total_users": self.user_counter,
            "male_users": len(self.male_user_list),
            "female_users": len(self.female_user_list),
            "user_list_size": len(self.user_list)
        }

    # 获得用户列表 [内部方法，非API调用]
    def get_user_list(self):
        return self.user_list

    # 获得男性用户列表 [内部方法，非API调用]
    def get_male_user_list(self):
        return self.male_user_list

    # 获得女性用户列表 [内部方法，非API调用]
    def get_female_user_list(self):
        return self.female_user_list

    # 获得用户实例 [内部方法，非API调用]
    def get_user_instance(self, user_id):
        return self.user_list.get(user_id)

    # 用户注销 [API调用]
    async def deactivate_user(self, user_id):
        """
        用户注销功能，删除用户及其相关的匹配数据
        数据流程：
        1. 检查用户是否存在
        2. 获取用户的所有match_ids
        3. 从MatchManager获取相关Match实例
        4. 获取Match中涉及的其他用户
        5. 删除用户（内存+数据库）
        6. 从其他用户的match_ids中移除相关match_id
        7. 删除相关Match实例（内存+数据库）
        [API调用]
        """
        try:
            # Convert string to int if needed
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            
            # Step 1: 检查用户是否存在
            target_user = self.user_list.get(user_id)
            if not target_user:
                return False
            
            # Step 2: 获取用户的所有match_ids
            user_match_ids = target_user.match_ids.copy()  # 创建副本，避免修改时的问题
            
            # Step 3: 从MatchManager获取相关Match实例
            from app.services.https.MatchManager import MatchManager
            match_manager = MatchManager()
            
            matches_to_delete = []
            other_users_to_update = set()  # 使用set避免重复
            
            for match_id in user_match_ids:
                match_instance = match_manager.get_match(match_id)
                if match_instance:
                    matches_to_delete.append(match_instance)
                    
                    # Step 4: 获取Match中涉及的其他用户
                    other_user_id = match_instance.get_target_user_id(user_id)
                    if other_user_id:
                        other_user = self.get_user_instance(other_user_id)
                        if other_user:
                            other_users_to_update.add((other_user, match_id))
            
            # Step 5: 删除本人用户实例（内存+数据库）
            # 从内存中删除
            del self.user_list[user_id]
            
            # 从性别分类列表中删除
            if target_user.gender == 1:
                self.male_user_list.pop(user_id, None)
            elif target_user.gender == 2:
                self.female_user_list.pop(user_id, None)
            
            # 从数据库中删除
            await Database.delete_one("users", {"_id": user_id})
            
            # Step 6: 从其他用户的match_ids中移除相关match_id
            for other_user, match_id in other_users_to_update:
                if match_id in other_user.match_ids:
                    other_user.match_ids.remove(match_id)
                    # 更新数据库中的用户数据
                    await Database.update_one(
                        "users",
                        {"_id": other_user.user_id},
                        {"$pull": {"match_ids": match_id}}
                    )
            
            # Step 7: 删除相关Match实例（内存+数据库）
            for match_instance in matches_to_delete:
                # 从MatchManager内存中删除
                match_manager.match_list.pop(match_instance.match_id, None)
                
                # 从数据库中删除
                await Database.delete_one("matches", {"_id": match_instance.match_id})
            
            # 更新用户计数器
            self.user_counter = len(self.user_list)
            
            print(f"用户注销成功: 删除用户 {user_id}，清理了 {len(matches_to_delete)} 个匹配，更新了 {len(other_users_to_update)} 个其他用户")
            return True
            
        except Exception as e:
            print(f"用户注销失败: {e}")
            return False