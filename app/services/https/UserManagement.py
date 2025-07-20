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
    database_address = settings.MONGODB_URL

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.user_list = {}
            cls._instance.male_user_list = {}
            cls._instance.female_user_list = {}
            cls._instance._user_id_counter = 1
        return cls._instance

    # 创建新用户
    def create_new_user(self, telegram_user_name, telegram_user_id, gender):
        user_id = int(telegram_user_id) # 用户id就是tg_id
        self._user_id_counter += 1
        user = User(telegram_user_name=telegram_user_name, gender=gender, user_id=user_id)
        self.user_list[user_id] = user
        if gender == 1:
            self.male_user_list[user_id] = user
        elif gender == 2:
            self.female_user_list[user_id] = user
        return user_id

    def get_user_by_session_id(self, user_id):
        pass

    # 编辑用户年龄
    def edit_user_age(self, user_id, age):
        user = self.user_list.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.edit_data(age=age)
        return True

    # 编辑用户目标性别
    def edit_target_gender(self, user_id, target_gender):
        user = self.user_list.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.edit_data(target_gender=target_gender)
        return True

    # 编辑用户总结
    def edit_summary(self, user_id, summary):
        user = self.user_list.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.edit_data(user_personality_summary=summary)
        return True

    async def save_to_database(self, user_id=None):
        """
        保存指定user_id的用户到MongoDB，并使用user_id作为文档的_id。
        如果用户在数据库中已存在，则更新；否则，创建新记录。
        """
        if user_id is None:
            return False

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

    # 根据id获取用户信息
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
            "user_id": user.user_id
        }