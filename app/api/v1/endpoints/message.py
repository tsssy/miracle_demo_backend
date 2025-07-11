from fastapi import APIRouter, HTTPException
from app.schemas.message import GetMatchedUsersRequest, GetMatchedUsersResponse
from app.services.service_message import MessageService

router = APIRouter()

@router.post("/get_matched_users", response_model=GetMatchedUsersResponse)
async def get_matched_users(request: GetMatchedUsersRequest):
    """
    获取匹配用户列表接口
    - 入参: GetMatchedUsersRequest（telegram_id）
    - 出参: GetMatchedUsersResponse（telegram_id_list）
    """
    return await MessageService.get_matched_users(request) 