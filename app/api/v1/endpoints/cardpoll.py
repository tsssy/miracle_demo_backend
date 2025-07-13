from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.services.service_cardpoll import ServiceCardpoll
from app.schemas.cardpoll import (
    EditAnswerRequest, EditAnswerResponse,
    ToggleQuestionSaveRequest, ToggleQuestionSaveResponse,
    GetQuestionRequest, GetQuestionResponse,
    BlockAnswerRequest, BlockAnswerResponse,
    LikeAnswerRequest, LikeAnswerResponse,
    GetCardPollAnswerRequest, GetCardPollAnswerResponse
)
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/edit_answer", response_model=EditAnswerResponse, summary="创建或编辑答案")
# async def edit_answer(request: EditAnswer_Request, current_user: Dict[str, Any] = Depends(get_current_active_user)):
async def edit_answer(request: EditAnswerRequest): # 暂时不需要用户认证
    """
    创建或编辑一个答案。
    - 如果提供了 answer_id，则为编辑模式。
    - 如果未提供 answer_id，则为创建新答案模式。
    """
    try:
        response = await ServiceCardpoll.edit_answer(request=request)   # 暂时不需要用户认证
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/toggle_question_save", response_model=ToggleQuestionSaveResponse, summary="切换问题保存状态")
# async def toggle_question_save(request: ToggleQuestionSave_Request, current_user: Dict[str, Any] = Depends(get_current_active_user)):
async def toggle_question_save(request: ToggleQuestionSaveRequest): # 暂时不需要用户认证
    """收藏或取消收藏一个问题。"""
    try:
        # request_data = request.dict()
        # response_data = await ServiceCardpoll.toggle_question_save(request_data=request_data, user_id=current_user['_id'])
        response = await ServiceCardpoll.toggle_question_save(request=request)   # 暂时不需要用户认证
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/get_question", response_model=GetQuestionResponse, summary="获取一个问题")
async def get_question(request: GetQuestionRequest):
    """获取一个随机或推荐的问题以供回答。"""
    try:
        # request_data = request.dict()
        response = await ServiceCardpoll.get_question(request=request)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/block_answer", response_model=BlockAnswerResponse, summary="拉黑答案")
async def block_answer(request: BlockAnswerRequest):
    """拉黑一个答案，使其不再出现。"""
    try:
        # request_data = request.dict()
        response = await ServiceCardpoll.block_answer(request=request)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/like_answer", response_model=LikeAnswerResponse, summary="点赞答案")
async def like_answer(request: LikeAnswerRequest):
    """点赞或取消点赞一个答案。"""
    try:
        # request_data = request.dict()
        response = await ServiceCardpoll.like_answer(request=request)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/get_answer", response_model=GetCardPollAnswerResponse, summary="获取一个答案")
async def get_answer(request: GetCardPollAnswerRequest):
    """根据滑动方向获取一个答案的详细信息。"""
    try:
        # request_data = request.dict()
        response = await ServiceCardpoll.get_answer(request=request)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 