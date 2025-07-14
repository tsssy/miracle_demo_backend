from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from app.core.database import Database
from app.utils.my_logger import MyLogger
from bson import ObjectId
from datetime import datetime
from app.schemas.cardpoll import (
    EditAnswerRequest, EditAnswerResponse,
    ToggleQuestionSaveRequest, ToggleQuestionSaveResponse,
    GetQuestionRequest, GetQuestionResponse,
    BlockAnswerRequest, BlockAnswerResponse,
    LikeAnswerRequest, LikeAnswerResponse,
    GetCardPollAnswerRequest, GetCardPollAnswerResponse
)
import asyncio
import random

logger = MyLogger("cardpoll_service")


class ServiceCardpoll:
    # 用于存储每个用户的当前问题指针 (question_id)
    _user_question_pointers: Dict[int, ObjectId] = {}

    @staticmethod
    async def edit_answer(request: EditAnswerRequest) -> EditAnswerResponse:
        """创建或编辑答案"""
        request_data = request.dict()

        telegram_id_str = request_data.get("telegram_id")
        question_id_str = request_data.get("question_id")
        answer_id_str = request_data.get("answer_id")
        new_answer_content = request_data.get("new_answer")
        is_send = request_data.get("is_send")
        answer_is_draft = request_data.get("answer_is_draft")

        # 确保 telegram_id 是整数类型
        try:
            telegram_id = int(telegram_id_str)
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="telegram_id 格式不正确")

        # 1. 查找用户并校验性别：只有男性用户才能创建或编辑答案
        user = await Database.find_one("User", {"_id": telegram_id})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        if user.get("gender") != 2: # 2 代表男性
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有男性用户才能创建或编辑答案")

        # 判断最终草稿状态：这里的answer_is_draft是否多余？仅用is_send判断即可？待确认 TODO
        is_draft = not is_send

        try:
            if answer_id_str is None:
                # --- 场景一：创建新答案 ---
                logger.info(f"用户 {telegram_id} 正在为问题 {question_id_str} 创建新答案...")

                # 1. 在 Answer 集合中插入新文档
                answer_document = {
                    "question_id": ObjectId(question_id_str),
                    "telegram_id": telegram_id,
                    "content": new_answer_content,
                    "is_draft": is_draft,
                    "created_at": datetime.utcnow(),
                    "liked_user_ids": []
                }
                new_answer_id = await Database.insert_one("Answer", answer_document)

                # 2. 在 User 集合中更新回答者信息
                await Database.update_one(
                    "User",
                    {"_id": telegram_id},
                    {"$push": {"answer_list": ObjectId(new_answer_id)}}
                )

                # 3. 在 Question 集合中更新问题信息
                await Database.update_one(
                    "Question",
                    {"_id": ObjectId(question_id_str)},
                    {"$push": {"answer_list": ObjectId(new_answer_id)}}
                )
                
                logger.info(f"新答案创建成功，ID: {new_answer_id}")
                return EditAnswerResponse(
                    answer_id=str(new_answer_id),
                    answer_string=new_answer_content,
                    is_draft=is_draft
                )

            else:
                # --- 场景二：编辑现有答案 ---
                logger.info(f"用户 {telegram_id} 正在编辑答案 {answer_id_str}...")
                answer_oid = ObjectId(answer_id_str)

                # 安全检查：确认该答案属于当前用户
                existing_answer = await Database.find_one("Answer", {"_id": answer_oid})
                if not existing_answer or existing_answer.get("telegram_id") != telegram_id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无法编辑不属于自己的答案")

                # 更新 Answer 文档
                update_document = {
                    "$set": {
                        "content": new_answer_content,
                        "is_draft": is_draft
                    }
                }
                await Database.update_one("Answer", {"_id": answer_oid}, update_document)
                
                logger.info(f"答案 {answer_id_str} 更新成功")
                return EditAnswerResponse(
                    answer_id=answer_id_str,
                    answer_string=new_answer_content,
                    is_draft=is_draft
                )

        except HTTPException as e:
            raise e # 将HTTP异常直接抛出
        except Exception as e:
            logger.error(f"处理答案失败: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"处理答案时发生内部错误: {e}")

    @staticmethod
    async def toggle_question_save(request: ToggleQuestionSaveRequest) -> ToggleQuestionSaveResponse:
        """切换问题的收藏状态（收藏/取消收藏）"""
        telegram_id = request.telegram_id
        question_id_str = request.question_id
        
        logger.info(f"用户 {telegram_id} 正在切换问题 {question_id_str} 的收藏状态...")

        try:
            question_oid = ObjectId(question_id_str)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的 question_id 格式")

        try:
            # 1. 查找用户
            user = await Database.find_one("User", {"_id": telegram_id})
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

            # 2. 检查问题是否已保存
            saved_questions = user.get("saved_list_question", [])
            is_currently_saved = question_oid in saved_questions

            # 3. 更新用户文档
            if is_currently_saved:
                # 如果已保存，则取消保存（移除）
                await Database.update_one(
                    "User",
                    {"_id": telegram_id},
                    {"$pull": {"saved_list_question": question_oid}}
                )
                new_saved_status = False
                logger.info(f"用户 {telegram_id} 取消收藏问题 {question_id_str}")
            else:
                # 如果未保存，则保存（添加）
                await Database.update_one(
                    "User",
                    {"_id": telegram_id},
                    {"$addToSet": {"saved_list_question": question_oid}}
                )
                new_saved_status = True
                logger.info(f"用户 {telegram_id} 收藏了问题 {question_id_str}")
                
            return ToggleQuestionSaveResponse(is_saved=new_saved_status)

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"切换问题保存状态失败: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"处理请求时发生内部错误: {e}")

    # get_question 简单版本
    # @staticmethod
    # async def get_question(request: GetQuestionRequest) -> GetQuestionResponse:
    #     """
    #     获取一个问题
    #     """
    #     # 考虑前端给后端加一个option参数：current_question_id?
    #     # 如果current_question_id存在，则根据id和is_swiping_toward_left是左/右，返回数据库里的上一条/下一条问题
    #     # 如果current_question_id不存在，则随机获取一个活跃的问题，作为初始问题
    #     # TODO

    #     request_data = request.dict()
    #     telegram_id = request_data.get("telegram_id")

    #     logger.info(f"用户 {telegram_id} 正在获取问题...")

    #     try:
    #         # 1. 查找用户
    #         user = await Database.find_one("User", {"_id": telegram_id})
    #         if not user:
    #             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    #         # 2. 随机获取一个活跃的问题
    #         # 这里我们简单地随机获取一个问题，实际应用中会涉及更复杂的推荐逻辑
    #         random_question = await Database.find_one("Question", {"is_active": True})
    #         if not random_question:
    #             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目前没有可用的问题")

    #         question_id = str(random_question.get("_id"))
    #         question_content = random_question.get("content")

    #         # 3. 检查问题是否已收藏
    #         is_saved = ObjectId(question_id) in user.get("saved_question_ids", [])

    #         # 4. 检查用户是否已回答该问题
    #         user_answer = await Database.find_one(
    #             "Answer",
    #             {"question_id": ObjectId(question_id), "telegram_id": telegram_id}
    #         )

    #         answer_id = None
    #         answer_string = None
    #         answer_is_draft = None

    #         if user_answer:
    #             answer_id = str(user_answer.get("_id"))
    #             answer_string = user_answer.get("content")
    #             answer_is_draft = user_answer.get("is_draft")

    #         return GetQuestionResponse(
    #             question_id=question_id,
    #             question_content=question_content,
    #             is_saved=is_saved,
    #             answer_id=answer_id,
    #             answer_string=answer_string,
    #             answer_is_draft=answer_is_draft
    #         )

    #     except HTTPException as e:
    #         raise e
    #     except Exception as e:
    #         logger.error(f"获取问题失败: {e}")
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"处理请求时发生内部错误: {e}")

    # get_question 后端缓存版本
    @staticmethod
    async def get_question(request: GetQuestionRequest) -> GetQuestionResponse:
        """
        获取一个问题（支持滑动浏览，使用内存缓存维护用户当前问题位置）
        """
        telegram_id = request.telegram_id
        is_swiping_toward_left = request.is_swiping_toward_left

        logger.info(f"用户 {telegram_id} 正在获取问题 (滑动方向: {'左' if is_swiping_toward_left else '右'})...")

        try:
            # 1. 查找用户
            user = await Database.find_one("User", {"_id": telegram_id})
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

            # 2. 获取所有活跃的问题，按 _id 排序（天然按创建时间排序）
            all_active_questions = await Database.find("Question", {"is_active": True}, sort=[("_id", 1)])
            if not all_active_questions:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目前没有可用的问题")
            
            # 将 ObjectId 转换为字符串列表，方便比较和查找索引
            active_question_oids = [q.get("_id") for q in all_active_questions]

            # 3. 获取或初始化当前问题指针
            current_question_oid: Optional[ObjectId] = ServiceCardpoll._user_question_pointers.get(telegram_id)
            
            # 验证当前指针是否有效（对应问题是否还在活跃列表中）
            if current_question_oid not in active_question_oids:
                # 如果指针无效或不存在，随机选择一个作为初始问题
                current_question_index = 0
                if active_question_oids:
                    current_question_index = random.randint(0, len(active_question_oids) - 1)
                new_question_oid = active_question_oids[current_question_index]
                logger.info(f"用户 {telegram_id} 初始或重置问题指针为: {str(new_question_oid)}")
            else:
                # 找到当前问题在列表中的索引
                current_question_index = active_question_oids.index(current_question_oid)

                # 根据滑动方向确定下一个问题
                if is_swiping_toward_left:
                    # 向左滑：下一条 (索引增加)
                    next_index = (current_question_index + 1) % len(active_question_oids)
                else:
                    # 向右滑：上一条 (索引减少)
                    next_index = (current_question_index - 1 + len(active_question_oids)) % len(active_question_oids)
                
                new_question_oid = active_question_oids[next_index]
            
            # 获取新问题文档
            new_question_doc = next((q for q in all_active_questions if q.get("_id") == new_question_oid), None)
            if not new_question_doc: # 理论上不会发生，除非数据不一致
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="无法找到新的问题文档")

            ServiceCardpoll._user_question_pointers[telegram_id] = new_question_oid # 更新指针

            question_id = str(new_question_doc.get("_id"))
            question_content = new_question_doc.get("content")

            # 4. 检查问题是否已收藏
            is_saved = ObjectId(question_id) in user.get("saved_list_question", [])

            # 5. 检查用户是否已回答该问题
            user_answer = await Database.find_one(
                "Answer",
                {"question_id": ObjectId(question_id), "telegram_id": telegram_id}
            )

            answer_id = None
            answer_string = None
            answer_is_draft = None

            if user_answer:
                answer_id = str(user_answer.get("_id"))
                answer_string = user_answer.get("content")
                answer_is_draft = user_answer.get("is_draft")

            return GetQuestionResponse(
                question_id=question_id,
                question_content=question_content,
                is_saved=is_saved,
                answer_id=answer_id,
                answer_string=answer_string,
                answer_is_draft=answer_is_draft
            )

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"获取问题失败: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"处理请求时发生内部错误: {e}")

    @staticmethod
    async def block_answer(request: BlockAnswerRequest) -> BlockAnswerResponse:
        """拉黑一个答案（单向操作，仅限女性用户）"""

        telegram_id = request.telegram_id
        answer_id_str = request.answer_id
        
        logger.info(f"用户 {telegram_id} 正在拉黑答案 {answer_id_str}...")

        try:
            answer_oid = ObjectId(answer_id_str)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的 answer_id 格式")

        try:
            # 1. 查找用户并校验性别：只有女性用户才能拉黑答案
            user = await Database.find_one("User", {"_id": telegram_id})
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
            if user.get("gender") != 1: # 1 代表女性
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有女性用户才能拉黑答案")

            # 2. 查找答案，获取其所属问题ID
            answer = await Database.find_one("Answer", {"_id": answer_oid})
            if not answer:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="答案不存在")
            question_oid = ObjectId(answer.get("question_id"))

            # 3. 查找问题并验证所有权：确保该问题是当前女性用户创建的
            question = await Database.find_one("Question", {"_id": question_oid})
            if not question:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")
            if question.get("telegram_id") != telegram_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权拉黑不属于您问题下的答案")

            # 4. 将答案ID添加到该问题文档的屏蔽列表
            # 使用 $addToSet 可以确保即使重复请求也不会重复添加
            await Database.update_one(
                "Question",
                {"_id": question_oid},
                {"$addToSet": {"blocked_answer_list": answer_oid}}
            )
            
            logger.info(f"用户 {telegram_id} 成功拉黑答案 {answer_id_str} (问题ID: {str(question_oid)})")
            return BlockAnswerResponse(success=True)

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"拉黑答案失败: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"处理请求时发生内部错误: {e}")

    @staticmethod
    async def like_answer(request: LikeAnswerRequest) -> LikeAnswerResponse:
        """喜欢/取消喜欢一个答案，并处理配对关系（仅限女性用户喜欢男性用户的回答）"""
        liker_telegram_id = request.telegram_id
        answer_id_str = request.answer_id

        logger.info(f"用户 {liker_telegram_id} 正在尝试喜欢答案 {answer_id_str}...")

        try:
            answer_oid = ObjectId(answer_id_str)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的 answer_id 格式")

        try:
            # 1. 并发获取所需文档
            liker_doc, answer_doc = await asyncio.gather(
                Database.find_one("User", {"_id": liker_telegram_id}),
                Database.find_one("Answer", {"_id": answer_oid})
            )

            if not liker_doc:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"用户 {liker_telegram_id} 不存在")
            if not answer_doc:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"答案 {answer_id_str} 不存在")

            likee_telegram_id = answer_doc.get("telegram_id")
            if liker_telegram_id == likee_telegram_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不能喜欢自己的答案")

            likee_doc = await Database.find_one("User", {"_id": likee_telegram_id})
            if not likee_doc:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"答案作者 {likee_telegram_id} 不存在")

            # 2. 权限验证：必须是女性用户喜欢男性用户的回答
            if not (liker_doc.get("gender") == 1 and likee_doc.get("gender") == 2):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有女性用户才能喜欢男性用户的回答")

            # 3. 判断是“喜欢”还是“取消喜欢”
            is_currently_liked = liker_telegram_id in answer_doc.get("liked_user_ids", [])

            if is_currently_liked:
                # --- 取消喜欢 ---
                logger.info(f"用户 {liker_telegram_id} 取消喜欢答案 {answer_id_str} (作者: {likee_telegram_id})")
                await asyncio.gather(
                    # 从答案的喜欢列表中移除
                    Database.update_one("Answer", {"_id": answer_oid}, {"$pull": {"liked_user_ids": liker_telegram_id}}),
                    # 从女方的配对列表中移除男方
                    Database.update_one("User", {"_id": liker_telegram_id}, {"$pull": {"paired_user": likee_telegram_id}}),
                    # 从男方的配对列表中移除女方
                    Database.update_one("User", {"_id": likee_telegram_id}, {"$pull": {"paired_user": liker_telegram_id}})
                )
                return LikeAnswerResponse(paired_telegram_id=likee_telegram_id, is_liked=False)
            else:
                # --- 添加喜欢 ---
                logger.info(f"用户 {liker_telegram_id} 喜欢了答案 {answer_id_str} (作者: {likee_telegram_id})，建立配对")
                await asyncio.gather(
                    # 添加到答案的喜欢列表
                    Database.update_one("Answer", {"_id": answer_oid}, {"$addToSet": {"liked_user_ids": liker_telegram_id}}),
                    # 为女方添加配对的男方
                    Database.update_one("User", {"_id": liker_telegram_id}, {"$addToSet": {"paired_user": likee_telegram_id}}),
                    # 为男方添加配对的女方
                    Database.update_one("User", {"_id": likee_telegram_id}, {"$addToSet": {"paired_user": likee_telegram_id}})
                )
                return LikeAnswerResponse(paired_telegram_id=likee_telegram_id, is_liked=True)

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"喜欢/取消喜欢答案失败: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"处理请求时发生内部错误: {e}")

    @staticmethod
    async def get_answer(request: GetCardPollAnswerRequest) -> GetCardPollAnswerResponse:
        """
        获取一个答案
        """
        request_data = request.dict()
        telegram_id = request_data.get("telegram_id")
        is_swiping_toward_left = request_data.get("is_swiping_toward_left") # 暂时不处理滑动逻辑

        logger.info(f"用户 {telegram_id} 正在获取答案...")

        try:
            # 1. 查找并验证请求用户 (必须是女性)
            user = await Database.find_one("User", {"_id": telegram_id})
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
            if user.get("gender") != 1: # 1 代表女性
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有女性用户才能浏览答案")

            user_question_ids = user.get("question_list", [])
            if not user_question_ids:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="您尚未创建任何问题，无法查看答案")

            # 将用户的问题列表随机打乱，以增加多样性
            random.shuffle(user_question_ids)

            # 遍历所有问题，直到找到一个有合格答案的问题
            for question_id_str in user_question_ids:
                question_oid = ObjectId(question_id_str)
                
                # 获取问题文档以检查其状态和屏蔽列表
                question_doc = await Database.find_one("Question", {"_id": question_oid, "is_active": True})
                if not question_doc:
                    continue  # 如果问题不存在或不活跃，跳到下一个

                question_string = question_doc.get("content")
                blocked_answer_ids = question_doc.get("blocked_answer_list", [])

                # 为当前问题构建聚合管道
                pipeline = [
                    {"$match": {"question_id": question_oid, "is_draft": False}},
                    {"$match": {"_id": {"$nin": [ObjectId(aid) for aid in blocked_answer_ids]}}},
                    {
                        "$lookup": {
                            "from": "User",
                            "localField": "telegram_id",
                            "foreignField": "_id",
                            "as": "author_info"
                        }
                    },
                    {"$unwind": "$author_info"},
                    {"$match": {"author_info.gender": 2}},
                    {"$sample": {"size": 1}}
                ]
                
                answer_collection = Database.get_collection("Answer")
                random_answer_list = await answer_collection.aggregate(pipeline).to_list(length=None)

                # 如果找到了答案，立即处理并返回
                if random_answer_list:
                    random_answer = random_answer_list[0]
                    answer_id = str(random_answer.get("_id"))
                    answer_content = random_answer.get("content")
                    is_liked = telegram_id in random_answer.get("liked_user_ids", [])

                    return GetCardPollAnswerResponse(
                        answer_id=answer_id,
                        answer_content=answer_content,
                        question_string=question_string,
                        is_liked=is_liked
                    )

            # 如果遍历完所有问题都没有找到答案，则报告无更多答案
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="没有更多可供浏览的答案")

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"获取答案失败: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"处理请求时发生内部错误: {e}") 