from fastapi import APIRouter, HTTPException
from app.schemas.question_answer_management import (
    NewQuestionRequest, NewQuestionResponse,
    ToggleQuestionActiveRequest, ToggleQuestionActiveResponse,
    GetAnswerListRequest, GetAnswerListResponse,
    GetQuestionListRequest, GetQuestionListResponse,
    GetQAMAnswerRequest, GetQAMAnswerResponse,
    GetAnswerInfoRequest, GetAnswerInfoResponse
)
from app.services.service_question_answer_management import QuestionAnswerManagementService

router = APIRouter()

@router.post("/new_question", response_model=NewQuestionResponse)
async def new_question(request: NewQuestionRequest):
    """
    新建问题接口
    - 入参: NewQuestionRequest（telegram_id, question_string, is_draft）
    - 出参: NewQuestionResponse（success）
    """
    return await QuestionAnswerManagementService.new_question(request)

@router.post("/toggle_question_active", response_model=ToggleQuestionActiveResponse)
async def toggle_question_active(request: ToggleQuestionActiveRequest):
    """
    切换问题激活状态接口
    - 入参: ToggleQuestionActiveRequest（question_id）
    - 出参: ToggleQuestionActiveResponse（success）
    """
    return await QuestionAnswerManagementService.toggle_question_active(request)

@router.post("/get_answer_list_for_a_question", response_model=GetAnswerListResponse)
async def get_answer_list_for_a_question(request: GetAnswerListRequest):
    """
    获取问题答案列表接口
    - 入参: GetAnswerListRequest（question_id）
    - 出参: GetAnswerListResponse（answer_list, answer_string）
    """
    return await QuestionAnswerManagementService.get_answer_list_for_a_question(request)

@router.post("/get_question_list", response_model=GetQuestionListResponse)
async def get_question_list(request: GetQuestionListRequest):
    """
    获取问题列表接口
    - 入参: GetQuestionListRequest（telegram_id）
    - 出参: GetQuestionListResponse（question_list, question_strings）
    """
    return await QuestionAnswerManagementService.get_question_list(request)

@router.post("/get_qa_answer", response_model=GetQAMAnswerResponse)
async def get_qa_answer(request: GetQAMAnswerRequest):
    """
    获取问答答案接口
    - 入参: GetQAMAnswerRequest（telegram_id）
    - 出参: GetQAMAnswerResponse（answer_id_list, question_id_list, answer_content, question_content）
    """
    return await QuestionAnswerManagementService.get_qa_answer(request)

@router.post("/get_answer_info", response_model=GetAnswerInfoResponse)
async def get_answer_info(request: GetAnswerInfoRequest):
    result = await QuestionAnswerManagementService.get_answer_info(request)
    if not result:
        raise HTTPException(status_code=404, detail="Answer not found")
    return result 