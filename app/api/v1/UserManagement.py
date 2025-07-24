from fastapi import APIRouter, HTTPException
from app.schemas.UserManagement import (
    CreateNewUserRequest, CreateNewUserResponse,
    EditUserAgeRequest, EditUserAgeResponse,
    EditTargetGenderRequest, EditTargetGenderResponse,
    EditSummaryRequest, EditSummaryResponse,
    SaveUserInfoToDatabaseRequest, SaveUserInfoToDatabaseResponse,
    GetUserInfoWithUserIdRequest, GetUserInfoWithUserIdResponse,
    DeactivateUserRequest, DeactivateUserResponse
)
from app.services.https.UserManagement import UserManagement

router = APIRouter()

@router.post("/create_new_user", response_model=CreateNewUserResponse)
# 创建新用户
async def create_new_user(request: CreateNewUserRequest):
    user_manager = UserManagement()
    try:
        user_id = user_manager.create_new_user(
            telegram_user_name=request.telegram_user_name,
            telegram_user_id=request.telegram_user_id,
            gender=request.gender
        )
        return CreateNewUserResponse(success=True, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

@router.post("/edit_user_age", response_model=EditUserAgeResponse)
# 编辑用户年龄
async def edit_user_age(request: EditUserAgeRequest):
    user_manager = UserManagement()
    try:
        success = user_manager.edit_user_age(request.user_id, request.age)
        return EditUserAgeResponse(success=success)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

# 编辑用户目标性别
@router.post("/edit_target_gender", response_model=EditTargetGenderResponse)
async def edit_target_gender(request: EditTargetGenderRequest):
    user_manager = UserManagement()
    try:
        success = user_manager.edit_target_gender(request.user_id, request.target_gender)
        return EditTargetGenderResponse(success=success)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

# 编辑用户简介
@router.post("/edit_summary", response_model=EditSummaryResponse)
async def edit_summary(request: EditSummaryRequest):
    user_manager = UserManagement()
    try:
        success = user_manager.edit_summary(request.user_id, request.summary)
        return EditSummaryResponse(success=success)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

# 保存用户信息到数据库
@router.post("/save_to_database", response_model=SaveUserInfoToDatabaseResponse)
async def save_to_database(request: SaveUserInfoToDatabaseRequest):
    user_manager = UserManagement()
    try:
        success = await user_manager.save_to_database(request.user_id)
        return SaveUserInfoToDatabaseResponse(success=success)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

# 根据用户id获取用户信息
@router.post("/get_user_info_with_user_id", response_model=GetUserInfoWithUserIdResponse)
async def get_user_info_with_user_id(request: GetUserInfoWithUserIdRequest):
    user_manager = UserManagement()
    try:
        user_info = user_manager.get_user_info_with_user_id(request.user_id)
        return GetUserInfoWithUserIdResponse(**user_info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

# 用户注销
@router.post("/deactivate_user", response_model=DeactivateUserResponse)
async def deactivate_user(request: DeactivateUserRequest):
    user_manager = UserManagement()
    try:
        success = await user_manager.deactivate_user(request.user_id)
        return DeactivateUserResponse(success=success)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 
