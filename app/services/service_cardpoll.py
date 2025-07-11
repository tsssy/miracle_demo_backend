from typing import Dict, Any
from fastapi import HTTPException, status
from app.core.database import Database
from app.utils.my_logger import MyLogger
from bson import ObjectId
from app.schemas.cardpoll import (
    EditAnswerResponse,
    ToggleQuestionSaveResponse,
    GetQuestionResponse,
    BlockAnswerResponse,
    LikeAnswerResponse,
    GetCardPollAnswerResponse
)

logger = MyLogger("cardpoll_service")


class ServiceCardpoll:
    @staticmethod
    async def edit_answer(request_data: Dict[str, Any]) -> EditAnswerResponse:
        """
        创建或编辑答案（返回假数据，直接用schema回复体）
        """
        logger.info(f"正在创建/编辑答案: {request_data}")
        return EditAnswerResponse(
            answer_id="123",
            answer_string="test",
            is_draft=False
        )

    @staticmethod
    async def toggle_question_save(request_data: Dict[str, Any]) -> ToggleQuestionSaveResponse:
        """
        切换问题的保存状态（返回假数据，直接用schema回复体）
        """
        logger.info(f"正在切换问题 {request_data.get('question_id')} 的保存状态...")
        return ToggleQuestionSaveResponse(
            is_saved=True
        )

    @staticmethod
    async def get_question(request_data: Dict[str, Any]) -> GetQuestionResponse:
        """
        获取一个问题（返回假数据，直接用schema回复体）
        """
        logger.info(f"用户 {request_data.get('telegram_id')} 正在获取问题...")
        return GetQuestionResponse(
            question_id=str(ObjectId()),
            question_content="你最近一次开怀大笑是什么时候？",
            is_saved=False,
            answer_id=str(ObjectId()),
            answer_string="昨天看了一部喜剧电影，笑得肚子疼。",
            answer_is_draft=False
        )

    @staticmethod
    async def block_answer(request_data: Dict[str, Any]) -> BlockAnswerResponse:
        """
        屏蔽答案（返回假数据，直接用schema回复体）
        """
        logger.info(f"用户 {request_data.get('telegram_id')} 正在屏蔽答案 {request_data.get('answer_id')}...")
        return BlockAnswerResponse(
            success=True
        )

    @staticmethod
    async def like_answer(request_data: Dict[str, Any]) -> LikeAnswerResponse:
        """
        点赞答案（返回假数据，直接用schema回复体）
        """
        logger.info(f"用户 {request_data.get('telegram_id')} 正在点赞答案 {request_data.get('answer_id')}...")
        return LikeAnswerResponse(
            paired_telegram_id=987654321,
            is_liked=True
        )

    @staticmethod
    async def get_answer(request_data: Dict[str, Any]) -> GetCardPollAnswerResponse:
        """
        获取一个答案（返回假数据，直接用schema回复体）
        """
        logger.info(f"用户 {request_data.get('telegram_id')} 正在获取答案...")
        return GetCardPollAnswerResponse(
            answer_id=str(ObjectId()),
            answer_content="我最喜欢的旅行目的地是京都，充满了历史和宁静的感觉。",
            question_string="你最想去哪里旅行？",
            is_liked=False
        ) 