from typing import Dict, Any
from fastapi import HTTPException, status
from app.core.database import Database
from app.utils.my_logger import MyLogger

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

        try:
            # 插入用户数据到 MongoDB
            # MongoDB 集合名称我们约定为 'users'
            inserted_id = await Database.insert_one("users", user_data)
            logger.info(f"用户数据已插入 MongoDB，ID: {inserted_id}")

            # 返回创建的用户数据，包含ID
            return {
                "_id": inserted_id, # 返回ObjectId的字符串形式
                "telegram_id": user_data["telegram_id"],
                "mode": user_data["mode"]
            }
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"创建用户失败: {e}")

    @staticmethod
    async def get_user_gender(user_id: str) -> Dict[str, Any]:
        """根据用户ID获取用户性别"""
        logger.info(f"尝试获取用户ID {user_id} 的性别")
        try:
            # 将 user_id 转换为整数类型
            user_id_int = int(user_id)
            # 关键修改：将查询键从 'user_id' 改为 '_id'
            user = await Database.find_one("telegram_sessions", {"_id": user_id_int})
            if user and "gender" in user:
                logger.info(f"找到用户ID {user_id} 的性别: {user["gender"]}")
                return {"gender": user["gender"]}
            else:
                logger.warning(f"未找到用户ID {user_id} 或其性别信息")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户未找到或性别信息缺失")
        except ValueError:
            logger.error(f"用户ID {user_id} 无法转换为整数。")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的用户ID格式，请提供整数ID。")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取用户ID {user_id} 性别失败: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取用户性别失败: {e}") 