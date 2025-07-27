from fastapi import APIRouter, HTTPException
from app.schemas.MatchManager import (
    CreateMatchRequest, CreateMatchResponse,
    GetMatchInfoRequest, GetMatchInfoResponse,
    ToggleLikeRequest, ToggleLikeResponse,
    SaveMatchToDatabaseRequest, SaveMatchToDatabaseResponse,
    GetNewMatchesForEveryoneRequest, GetNewMatchesForEveryoneResponse  # 🔧 MODIFIED: 新增导入
)
from app.services.https.MatchManager import MatchManager

router = APIRouter()

@router.post("/create_match", response_model=CreateMatchResponse)
async def create_match(request: CreateMatchRequest):
    match_manager = MatchManager()
    try:
        new_match = await match_manager.create_match(
            user_id_1=request.user_id_1,
            user_id_2=request.user_id_2,
            reason_1=request.reason_1,
            reason_2=request.reason_2,
            match_score=request.match_score
        )
        return CreateMatchResponse(success=True, match_id=new_match.match_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/get_match_info", response_model=GetMatchInfoResponse)
async def get_match_info(request: GetMatchInfoRequest):
    match_manager = MatchManager()
    try:
        match_info = match_manager.get_match_info(
            user_id=request.user_id,
            match_id=request.match_id
        )
        if match_info is None:
            raise HTTPException(status_code=404, detail="Match not found")
        
        return GetMatchInfoResponse(**match_info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/toggle_like", response_model=ToggleLikeResponse)
async def toggle_like(request: ToggleLikeRequest):
    match_manager = MatchManager()
    try:
        success = match_manager.toggle_like(match_id=request.match_id)
        return ToggleLikeResponse(success=success)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/save_to_database", response_model=SaveMatchToDatabaseResponse)
async def save_to_database(request: SaveMatchToDatabaseRequest):
    match_manager = MatchManager()
    try:
        success = await match_manager.save_to_database(match_id=request.match_id)
        return SaveMatchToDatabaseResponse(success=success)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 🔧 MODIFIED: 新增路由 - 批量匹配接口
@router.post("/get_new_matches_for_everyone", response_model=GetNewMatchesForEveryoneResponse)
async def get_new_matches_for_everyone(request: GetNewMatchesForEveryoneRequest):
    """
    为所有女性用户或指定女性用户创建新匹配
    
    Args:
        request: 包含可选user_id和print_message标志的请求体
        
    Returns:
        GetNewMatchesForEveryoneResponse: 包含操作结果和详细消息
        
    Notes:
        - 如果提供user_id，只为该用户匹配（必须是女性，gender=1）
        - 如果不提供user_id，为所有女性用户匹配
        - print_message=True时返回详细的匹配表格
        - 只能给女性用户匹配，男性用户会返回错误
    """
    match_manager = MatchManager()
    try:
        result = await match_manager.get_new_matches_for_everyone(
            user_id=request.user_id,
            print_message=request.print_message
        )
        return GetNewMatchesForEveryoneResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))