from app.schemas.question_answer_management import (
    NewQuestionRequest, NewQuestionResponse,
    ToggleQuestionActiveRequest, ToggleQuestionActiveResponse,
    GetAnswerListRequest, GetAnswerListResponse,
    GetQuestionListRequest, GetQuestionListResponse,
    GetQAMAnswerRequest, GetQAMAnswerResponse,
    GetAnswerInfoRequest, GetAnswerInfoResponse
)
from app.core.database import Database
from datetime import datetime
from bson import ObjectId

class QuestionAnswerManagementService:
    @staticmethod
    async def new_question(request: NewQuestionRequest) -> NewQuestionResponse:
        """
        新建问题
        - 参数: request（NewQuestionRequest对象）
        - 返回: NewQuestionResponse
        """
        # 获取是否为草稿
        is_draft = getattr(request, "is_draft", False)
        # 构建要插入到Question集合的文档
        question_doc = {
            "content": request.question_string,  # 问题内容
            "telegram_id": request.telegram_id,  # 创建该问题的用户telegram_id
            "is_draft": is_draft,               # 是否为草稿
            "is_active": False if is_draft else True,  # 草稿一定是False，非草稿新建为True
            "created_at": datetime.utcnow(),     # 创建时间
            "answer_list": [],                  # 回答列表，存储ObjectId
            "blocked_answer_list": [],          # 拉黑回答列表
            "liked_answer_list": []             # 收藏回答列表
        }
        try:
            # 插入新问题到Question集合，返回ObjectId
            inserted_id = await Database.insert_one("Question", question_doc)
            # 更新User的question_list，直接存ObjectId类型
            await Database.update_one(
                "User",
                {"_id": request.telegram_id},
                {"$push": {"question_list": ObjectId(inserted_id)}}
            )
            # 返回成功响应
            return NewQuestionResponse(success=True)
        except Exception as e:
            # 插入或更新失败，返回失败响应
            return NewQuestionResponse(success=False)

    @staticmethod
    async def toggle_question_active(request: ToggleQuestionActiveRequest) -> ToggleQuestionActiveResponse:
        """
        切换问题激活状态
        - 参数: request（ToggleQuestionActiveRequest对象）
        - 返回: ToggleQuestionActiveResponse
        """
        try:
            # 根据question_id查找问题
            question_id = request.question_id
            question = await Database.find_one("Question", {"_id": ObjectId(question_id)})
            if not question:
                # 未找到该问题
                return ToggleQuestionActiveResponse(success=False)
            # 草稿问题不允许切换is_active
            if question.get("is_draft", False):
                return ToggleQuestionActiveResponse(success=False)
            # 取反is_active
            new_is_active = not question.get("is_active", True)
            # 更新is_active字段
            modified_count = await Database.update_one(
                "Question",
                {"_id": ObjectId(question_id)},
                {"$set": {"is_active": new_is_active}}
            )
            if modified_count > 0:
                # 更新成功
                return ToggleQuestionActiveResponse(success=True)
            else:
                # 未修改任何文档
                return ToggleQuestionActiveResponse(success=False)
        except Exception as e:
            # 异常处理，返回失败
            return ToggleQuestionActiveResponse(success=False)

    @staticmethod
    async def get_answer_list_for_a_question(request: GetAnswerListRequest) -> GetAnswerListResponse:
        """
        获取问题答案列表
        - 参数: request（GetAnswerListRequest对象）
        - 返回: GetAnswerListResponse
        """
        try:
            # 查找对应问题
            question = await Database.find_one("Question", {"_id": ObjectId(request.question_id)})
            if not question or not question.get("answer_list"):
                # 没有找到问题或没有答案
                return GetAnswerListResponse(answer_list=[], answer_string=[])
            answer_id_list = question["answer_list"]
            answer_list = []
            answer_string = []
            # 遍历answer_id，查找Answer集合获取内容
            for aid in answer_id_list:
                # 直接用ObjectId查找
                answer = await Database.find_one("Answer", {"_id": aid})
                if answer:
                    answer_list.append(str(answer["_id"]))  # 返回给前端转为str
                    answer_string.append(answer.get("content", ""))
            return GetAnswerListResponse(answer_list=answer_list, answer_string=answer_string)
        except Exception as e:
            # 异常处理，返回空列表
            return GetAnswerListResponse(answiser_lt=[], answer_string=[])

    @staticmethod
    async def get_question_list(request: GetQuestionListRequest) -> GetQuestionListResponse:
        """
        获取问题列表
        - 参数: request（GetQuestionListRequest对象）
        - 返回: GetQuestionListResponse
        """
        try:
            # 在User集合中查找_id为telegram_id的用户
            user = await Database.find_one("User", {"_id": request.telegram_id})
            if not user or not user.get("question_list"):
                # 用户不存在或没有问题列表
                return GetQuestionListResponse(question_list=[], question_strings=[])
            question_id_list = user["question_list"]
            question_list = []
            question_strings = []
            # 遍历用户的问题ID列表，查找每个问题内容
            for qid in question_id_list:
                # 用ObjectId查找，保证类型一致
                question = await Database.find_one("Question", {"_id": ObjectId(qid)})
                if question:
                    question_list.append(str(question["_id"]))  # 返回给前端转为str
                    question_strings.append(question.get("content", ""))
            return GetQuestionListResponse(question_list=question_list, question_strings=question_strings)
        except Exception as e:
            # 异常处理，返回空列表
            return GetQuestionListResponse(question_list=[], question_strings=[])

    @staticmethod
    async def get_qa_answer(request: GetQAMAnswerRequest) -> GetQAMAnswerResponse:
        """
        获取问答答案
        - 参数: request（GetQAMAnswerRequest对象）
        - 返回: GetQAMAnswerResponse
        """
        try:
            # 1. 查找用户，获取answer_list
            user = await Database.find_one("User", {"_id": request.telegram_id})
            if not user or not user.get("answer_list"):
                # 用户不存在或没有回答
                return GetQAMAnswerResponse(answer_id_list=[], question_id_list=[], answer_content=[], question_content=[])
            answer_id_list = user["answer_list"]
            answer_ids = []
            question_ids = []
            answer_contents = []
            question_contents = []
            # 2. 遍历answer_list查找Answer内容和question_id
            for aid in answer_id_list:
                answer = await Database.find_one("Answer", {"_id": aid})
                if answer:
                    answer_ids.append(str(answer["_id"]))
                    qid = answer.get("question_id")
                    question_ids.append(str(qid) if qid else "")
                    answer_contents.append(answer.get("content", ""))
                    # 3. 查找对应问题内容，兼容qid为ObjectId或字符串
                    if qid:
                        try:
                            # 如果qid不是ObjectId则尝试转换
                            qid_obj = qid if isinstance(qid, ObjectId) else ObjectId(qid)
                            question = await Database.find_one("Question", {"_id": qid_obj})
                            question_contents.append(question.get("content", "") if question else "")
                        except Exception:
                            # 转换失败或查找失败，补空字符串
                            question_contents.append("")
                    else:
                        question_contents.append("")
            return GetQAMAnswerResponse(
                answer_id_list=answer_ids,
                question_id_list=question_ids,
                answer_content=answer_contents,
                question_content=question_contents
            )
        except Exception as e:
            # 异常处理，返回空列表
            return GetQAMAnswerResponse(answer_id_list=[], question_id_list=[], answer_content=[], question_content=[])

    @staticmethod
    async def get_answer_info(request: GetAnswerInfoRequest) -> GetAnswerInfoResponse:
        """
        获取单个答案的详细信息
        """
        try:
            answer = await Database.find_one("Answer", {"_id": ObjectId(request.answer_id)})
            if not answer:
                return None
            return GetAnswerInfoResponse(
                answer_id=str(answer["_id"]),
                content=answer.get("content", ""),
                question_id=str(answer.get("question_id", "")),
                telegram_id=answer.get("telegram_id", ""),
                is_draft=answer.get("is_draft", False),
                created_at=answer.get("created_at"),
                liked_user_ids=[str(uid) for uid in answer.get("liked_user_ids", [])],
                is_active=answer.get("is_active", True)
            )
        except Exception as e:
            return None 