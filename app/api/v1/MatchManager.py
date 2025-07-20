from fastapi import APIRouter, HTTPException
from app.schemas.MatchManager import (
    CreateMatchRequest, CreateMatchResponse,
    GetMatchInfoRequest, GetMatchInfoResponse,
    ToggleLikeRequest, ToggleLikeResponse
)
from app.services.https.MatchManager import MatchManager

router = APIRouter()

@router.post("/create_match", response_model=CreateMatchResponse)
async def create_match(request: CreateMatchRequest):
    match_manager = MatchManager()
    try:
        new_match = match_manager.create_match(
            user_id_1=request.user_id_1,
            user_id_2=request.user_id_2,
            reason_1=request.reason_1,
            reason_2=request.reason_2,
            match_score=request.match_score
        )
        return CreateMatchResponse(match_id=new_match.match_id)
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