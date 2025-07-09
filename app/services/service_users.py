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
    async def create_female_user(session_id: int) -> Dict[str, Any]:
        """
        创建一个新的女性用户。
        1. 从telegram_session库获取_id和string
        2. 提取string中的三个问题内容，插入Question集合，收集question_id
        3. User的question_list存入新插入的question_id列表
        4. gender为1，user_id为int，其他字段空置
        """
        logger.info(f"尝试创建新女性用户: session_id={session_id}")
        try:
            # 从telegram_session库获取对应session
            session = await Database.find_one("telegram_sessions", {"_id": session_id})
            if not session or "string" not in session:
                logger.warning(f"未找到session或string字段: session_id={session_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应的telegram_session或string字段")
            string_content = session["string"]

            # 正则提取问题内容
            import re
            from datetime import datetime
            pattern = r"问题1: (.*?)\n\n问题2: (.*?)\n\n问题3: (.*?)\n"
            match = re.search(pattern, string_content, re.DOTALL)
            if not match:
                logger.warning(f"string字段格式不正确: {string_content}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="string字段格式不正确，无法提取问题内容")
            question_contents = [match.group(1).strip(), match.group(2).strip(), match.group(3).strip()]

            user_id_int = int(session["_id"])
            question_id_list = []
            # 插入每个问题到Question集合
            for idx, content in enumerate(question_contents):
                question_doc = {
                    "question_id": idx,  # 问题在user.question_list中的索引
                    "content": content,  # 问题内容
                    "user_id": user_id_int,  # 提问者id
                    "is_draft": False,  # 默认非草稿
                    "created_at": datetime.utcnow(),  # 当前时间
                    "answer_list": [],
                    "blocked_answer_list": [],
                    "liked_answer_list": [],
                    "is_active": True
                }
                qid = await Database.insert_one("Question", question_doc)
                question_id_list.append(qid)

            # 构建User集合的完整结构
            user_document = {
                "user_id": user_id_int,  # 用户唯一ID，int类型
                "gender": 1,  # 女性，int类型
                "mode": None,  # 女性用户mode可置为None或后续补充
                "question_list": question_id_list,  # 存入新插入的question_id列表
                "answer_list": [],
                "paired_user": [],
                "profile_photo": None,
                "profile": {},
                "model_id": None,
                "saved_list_question": [],
                "saved_list_answer": []
            }
            # 插入用户数据到 MongoDB User集合
            inserted_id = await Database.insert_one("User", user_document)
            logger.info(f"女性用户数据已插入 MongoDB User集合，ID: {inserted_id}")
            # 返回创建的用户数据，包含ID、user_id、gender、question_list
            return {
                "_id": inserted_id,
                "user_id": user_id_int,
                "gender": 1,
                "question_list": question_id_list
            }
        except Exception as e:
            logger.error(f"创建女性用户失败: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"创建女性用户失败: {e}")

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