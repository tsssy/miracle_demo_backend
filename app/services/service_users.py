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
        valid_modes = [1, 2, 3]  # 1=friends, 2=long-term_compinionship, 3=short-term_compinionship
        if user_data.get('mode') not in valid_modes:
            logger.warning(f"无效的 mode 参数: {user_data.get('mode')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的 'mode' 参数，请选择 {valid_modes} (1=friends, 2=long-term_compinionship, 3=short-term_compinionship)"
            )

        try:
            # 将telegram_id转换为int64，作为user_id
            telegram_id_int = int(user_data["telegram_id"])
            mode_int = int(user_data["mode"])
            # 构建User集合的完整结构，除user_id、mode、gender外其他字段全部置空
            user_document = {
                "user_id": telegram_id_int,  # 用户唯一ID，int类型
                "gender": 0,  # 男性，int类型
                "mode": mode_int,  # 关系模式，int类型
                "question_list": [],  # 空列表
                "answer_list": [],  # 空列表
                "paired_user": [],  # 空列表
                "profile_photo": None,  # 空，未上传头像
                "profile": {},  # 空字典
                "model_id": None,  # 空
                "saved_list_question": [],  # 空列表
                "saved_list_answer": []  # 空列表
            }
            # 插入用户数据到 MongoDB User集合
            inserted_id = await Database.insert_one("User", user_document)
            logger.info(f"用户数据已插入 MongoDB User集合，ID: {inserted_id}")
            # 返回创建的用户数据，包含ID和mode（不再返回telegram_id）
            return {
                "_id": inserted_id,
                "user_id": telegram_id_int,
                "mode": mode_int
            }
        except ValueError as e:
            logger.error(f"telegram_id转换失败: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的telegram_id格式，请提供有效的数字")
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