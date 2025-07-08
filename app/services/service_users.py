from typing import Dict, Any
from fastapi import HTTPException, status
from app.core.database import Database
from app.utils.my_logger import MyLogger
import uuid

logger = MyLogger("user_service")


class UserService:
    @staticmethod
    async def create_male_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建一个新的男性用户"""
        logger.info(f"尝试创建新男性用户: {user_data.get('telegram_id')}")

        # 检查 mode 字段是否有效
        valid_modes = ['friends', 'long-term_compinionship', 'short-term_compinionship']
        if user_data.get('mode') not in valid_modes:
            logger.warning(f"无效的 mode 参数: {user_data.get('mode')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的 'mode' 参数，请选择 {valid_modes}"
            )

        # 暂时模拟数据库插入，直接返回模拟数据
        # try:
        #     # 插入用户数据到 MongoDB
        #     # MongoDB 集合名称我们约定为 'users'
        #     inserted_id = await Database.insert_one("users", user_data)
        #     logger.info(f"用户数据已插入 MongoDB，ID: {inserted_id}")

        #     # 返回创建的用户数据，包含ID
        #     return {
        #         "_id": inserted_id, # 返回ObjectId的字符串形式
        #         "telegram_id": user_data["telegram_id"],
        #         "mode": user_data["mode"]
        #     }
        # except Exception as e:
        #     logger.error(f"创建用户失败: {e}")
        #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"创建用户失败: {e}")
        
        # 返回模拟数据
        mock_id = str(uuid.uuid4())
        logger.info(f"模拟用户创建成功，模拟ID: {mock_id}")
        return {
            "_id": mock_id,
            "telegram_id": user_data["telegram_id"],
            "mode": user_data["mode"]
        } 