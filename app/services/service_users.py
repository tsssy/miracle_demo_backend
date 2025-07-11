from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from app.core.database import Database
from app.utils.my_logger import MyLogger
from app.schemas.users import (
    GetTelegramSessionGenderRequest,
    GetTelegramSessionGenderResponse,
    CreateNewFemaleUserRequest,
    CreateNewFemaleUserResponse,
    CreateMaleUserRequest,
    CreateMaleUserResponse,
    GetUserExistRequest,
    GetUserExistResponse
)
from pydantic import BaseModel, Field

logger = MyLogger("user_service")


class UserService:
    @staticmethod
    async def create_new_male_user(user_data: CreateMaleUserRequest) -> CreateMaleUserResponse:
        """
        新建男用户业务逻辑
        - 参数: user_data（CreateMaleUserRequest对象，包含telegram_id和可选mode）
        - 返回: CreateMaleUserResponse模型，表示是否成功创建
        """
        valid_modes = [1, 2, 3]
        # mode为可选，如果传了则校验
        if user_data.mode is not None and user_data.mode not in valid_modes:
            logger.warning(f"无效的 mode 参数: {user_data.mode}")
            return CreateMaleUserResponse(success=False)
        try:
            telegram_id = user_data.telegram_id
            user_document = {
                "_id": telegram_id,  # 用telegram_id作为_id
                "telegram_id": telegram_id,
                "gender": 2,  # 男性为2
                "mode": user_data.mode,
                "question_list": [],
                "answer_list": [],
                "paired_user": [],
                "profile_photo": None,
                "profile": {},
                "model_id": None,
                "saved_list_question": [],
                "saved_list_answer": []
            }
            inserted_id = await Database.insert_one("User", user_document)
            logger.info(f"男用户数据已插入 MongoDB User集合，ID: {inserted_id}")
            return CreateMaleUserResponse(success=True)
        except Exception as e:
            logger.error(f"创建男用户失败: {e}")
            return CreateMaleUserResponse(success=False)

    @staticmethod
    async def create_new_female_user(request: CreateNewFemaleUserRequest) -> CreateNewFemaleUserResponse:
        """
        新建女用户业务逻辑
        - 参数: request（CreateNewFemaleUserRequest对象，包含telegram_id）
        - 返回: CreateNewFemaleUserResponse模型，包含是否成功创建的状态
        - 流程: 在telegram_sessions表中查找telegram_id，如果找到则创建用户和问题
        """
        logger.info(f"尝试创建女性用户，telegram_id: {request.telegram_id}")
        try:
            # 在telegram_sessions表中查找对应的记录
            session = await Database.find_one("telegram_sessions", {"_id": request.telegram_id})
            if not session:
                logger.warning(f"在telegram_sessions表中未找到telegram_id: {request.telegram_id}")
                return CreateNewFemaleUserResponse(success=False)
            if "final_string" not in session:
                logger.warning(f"telegram_sessions记录中缺少final_string字段: telegram_id={request.telegram_id}")
                return CreateNewFemaleUserResponse(success=False)
            # 解析final_string中的问题内容
            import re
            from datetime import datetime
            string_content = session["final_string"]
            pattern = r"问题1: (.*?)\n\n问题2: (.*?)\n\n问题3: (.*?)\n"
            match = re.search(pattern, string_content, re.DOTALL)
            if not match:
                logger.warning(f"final_string字段格式不正确，无法提取问题内容: {string_content}")
                return CreateNewFemaleUserResponse(success=False)
            # 提取问题内容
            question_contents = [match.group(1).strip(), match.group(2).strip(), match.group(3).strip()]
            # 创建问题记录
            question_id_list = []
            for idx, content in enumerate(question_contents):
                question_doc = {
                    "question_id": idx,
                    "content": content,
                    "telegram_id": request.telegram_id,
                    "is_draft": False,
                    "created_at": datetime.utcnow(),
                    "answer_list": [],
                    "blocked_answer_list": [],
                    "liked_answer_list": [],
                    "is_active": True
                }
                qid = await Database.insert_one("Question", question_doc)
                question_id_list.append(qid)
            # 创建用户记录
            user_document = {
                "_id": request.telegram_id,  # 用telegram_id作为_id
                "telegram_id": request.telegram_id,
                "gender": 1,  # 女性为1
                "mode": None,
                "question_list": question_id_list,
                "answer_list": [],
                "paired_user": [],
                "profile_photo": None,
                "profile": {},
                "model_id": None,
                "saved_list_question": [],
                "saved_list_answer": []
            }
            inserted_id = await Database.insert_one("User", user_document)
            logger.info(f"女性用户创建成功，telegram_id: {request.telegram_id}, User集合ID: {inserted_id}")
            return CreateNewFemaleUserResponse(success=True)
        except Exception as e:
            logger.error(f"创建女性用户时发生未知错误: {e}")
            return CreateNewFemaleUserResponse(success=False)

    @staticmethod
    async def get_user_from_telegram_session(request: GetTelegramSessionGenderRequest) -> GetTelegramSessionGenderResponse:
        """
        根据telegram_id从telegram_sessions表中获取用户性别
        - 参数: request（GetTelegramSessionGenderRequest对象，包含telegram_id）
        - 返回: GetTelegramSessionGenderResponse模型，包含gender字段
        """
        logger.info(f"尝试从telegram_sessions表获取telegram_id {request.telegram_id} 的性别")
        try:
            # 在telegram_sessions表中根据_id查询用户记录
            session_record = await Database.find_one("telegram_sessions", {"_id": request.telegram_id})
            # 检查是否找到记录以及是否包含gender字段
            if session_record and "gender" in session_record:
                gender_value = session_record["gender"]
                logger.info(f"成功找到telegram_id {request.telegram_id} 的性别: {gender_value}")
                return GetTelegramSessionGenderResponse(gender=gender_value)
            else:
                logger.warning(f"在telegram_sessions表中未找到telegram_id {request.telegram_id} 或其性别信息")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="用户未找到或性别信息缺失"
                )
        except Exception as e:
            logger.error(f"获取telegram_id {request.telegram_id} 性别时发生未知错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"获取用户性别失败: {e}"
            ) 

    @staticmethod
    async def get_user_exist(request: GetUserExistRequest) -> GetUserExistResponse:
        """
        查询用户是否存在（返回默认值）
        - 参数: request（GetUserExistRequest对象，包含telegram_id）
        - 返回: GetUserExistResponse模型
        """
        # 返回一个默认的存在性结果（假设存在）
        return GetUserExistResponse(success=False) 