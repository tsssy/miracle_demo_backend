from typing import Dict, Any
from fastapi import HTTPException, status
from app.core.database import Database
from app.utils.my_logger import MyLogger
from bson import ObjectId

logger = MyLogger("cardpoll_service")


class ServiceCardpoll:
    @staticmethod
    # async def edit_answer(request_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    async def edit_answer(request_data: Dict[str, Any]) -> Dict[str, Any]:  # 暂时不需要用户认证
        """创建或编辑答案 (返回假数据)"""
        logger.info(f"正在创建/编辑答案: {request_data}")
        # TODO
        # logger.info(f"用户 {user_id} 正在创建/编辑答案: {request_data}")

        # answer_id = request_data.get("answer_id") or str(ObjectId())
        # # 如果 is_send 为 False，则必定是草稿。如果 is_send 为 True，则根据 answer_is_draft 的值来定。
        # is_draft = not request_data.get("is_send") or request_data.get("answer_is_draft", False)

        # 模拟返回符合 EditAnswer_Response 的数据
        # return {
        #     "answer_id": answer_id,
        #     "answer_string": request_data["new_answer"],
        #     "is_draft": is_draft
        # }
        return {
            "answer_id": "123",
            "answer_string": "test",
            "is_draft": False
        }

    @staticmethod
    # async def toggle_question_save(request_data: Dict[str, Any], user_id: str) -> Dict[str, Any]: 
    async def toggle_question_save(request_data: Dict[str, Any]) -> Dict[str, Any]:  # 暂时不需要用户认证
        """切换问题的保存状态 (返回假数据)"""
        logger.info(f"正在切换问题 {request_data.get('question_id')} 的保存状态...")
        # TODO
        # 模拟返回一个固定的保存状态
        return {
            "is_saved": True
        }

    @staticmethod
    # async def get_question(request_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    async def get_question(request_data: Dict[str, Any]) -> Dict[str, Any]:  # 暂时不需要用户认证
        """获取一个问题 (返回假数据)"""
        logger.info(f"用户 {request_data.get('telegram_id')} 正在获取问题...")
        # TODO
        # 模拟返回一个包含答案（非草稿）的问题
        return {
            "question_id": str(ObjectId()),
            "question_content": "你最近一次开怀大笑是什么时候？",
            "is_saved": False,
            "answer_id": str(ObjectId()),
            "answer_string": "昨天看了一部喜剧电影，笑得肚子疼。",
            "answer_is_draft": False
        }

    @staticmethod
    async def block_answer(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """屏蔽答案 (返回假数据)"""
        logger.info(f"用户 {request_data.get('telegram_id')} 正在屏蔽答案 {request_data.get('answer_id')}...")
        return {
            "success": True
        }

    @staticmethod
    async def like_answer(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """点赞答案 (返回假数据)"""
        logger.info(f"用户 {request_data.get('telegram_id')} 正在点赞答案 {request_data.get('answer_id')}...")
        # 模拟返回配对成功且已点赞的状态
        return {
            "paired_telegram_id": 987654321,
            "is_liked": True
        }

    @staticmethod
    async def get_answer(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取一个答案 (返回假数据)"""
        logger.info(f"用户 {request_data.get('telegram_id')} 正在获取答案...")
        return {
            "answer_id": str(ObjectId()),
            "answer_content": "我最喜欢的旅行目的地是京都，充满了历史和宁静的感觉。",
            "question_string": "你最想去哪里旅行？",
            "is_liked": False
        } 