from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends
)
from typing import Any
from app.services.service_users import UserService
from app.schemas.users import (
    GetTelegramSessionGenderRequest,
    GetTelegramSessionGenderResponse,
    CreateNewFemaleUserRequest,
    CreateNewFemaleUserResponse,
    CreateMaleUserRequest,
    CreateMaleUserResponse,
    GetUserExistRequest,
    GetUserExistResponse,
    GetUserInfoRequest,
    GetUserInfoResponse,
)
from app.utils.my_logger import MyLogger

logger = MyLogger("user_endpoints")

router = APIRouter()

@router.post("/create_new_male_user", response_model=CreateMaleUserResponse, status_code=status.HTTP_200_OK)
async def users_create_male_user(request: CreateMaleUserRequest) -> Any:
    """
    新建男用户API接口
    - 参数: request（包含telegram_id、telegram_user_name和可选mode的请求体，类型为CreateMaleUserRequest）
    - 返回: 是否成功创建男用户的状态
    """
    try:
        result = await UserService.create_new_male_user(request)
        return result
    except Exception as e:
        logger.error(f"创建男用户失败: {e}")
        return CreateMaleUserResponse(success=False)

@router.post("/create_new_female_user", response_model=CreateNewFemaleUserResponse, status_code=status.HTTP_200_OK)
async def users_create_female_user(request: CreateNewFemaleUserRequest) -> Any:
    """
    新建女用户API接口
    - 参数: request（包含telegram_id、telegram_user_name和可选mode的请求体，类型为CreateNewFemaleUserRequest）
    - 返回: 是否成功创建女用户的状态
    """
    try:
        result = await UserService.create_new_female_user(request)
        return result
    except Exception as e:
        logger.error(f"创建女用户失败: {e}")
        return CreateNewFemaleUserResponse(success=False)

@router.post("/get_user_from_telegram_session", response_model=GetTelegramSessionGenderResponse, status_code=status.HTTP_200_OK)
async def get_user_from_telegram_session(request: GetTelegramSessionGenderRequest) -> Any:
    """
    通过Telegram Session获取用户性别API接口
    - 参数: request（包含telegram_id的请求体，类型为int）
    - 返回: 用户性别信息
    """
    try:
        result = await UserService.get_user_gender_from_telegram_session(request)
        return result
    except Exception as e:
        logger.error(f"获取用户性别失败: {e}")
        return GetTelegramSessionGenderResponse(gender=None)

@router.post("/get_user_exist", response_model=GetUserExistResponse)
async def user_exist(request: GetUserExistRequest) -> GetUserExistResponse:
    """
    查询用户是否存在（定义占位，未实现）
    - 参数: request（包含telegram_id的请求体）
    - 返回: 用户是否存在
    """
    return await UserService.get_user_exist(request)
    #TODO: 实现用户存在性查询逻辑
    #raise NotImplementedError("get_user_exist功能未实现")

@router.post("/get_user_info", response_model=GetUserInfoResponse)
async def get_user_info(request: GetUserInfoRequest) -> GetUserInfoResponse:
    """
    获取用户的详细信息
    - 参数: request (包含 telegram_id 的请求体)
    - 返回: 用户的详细信息
    """
    try:
        return await UserService.get_user_info(request)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"获取用户信息时端点发生错误: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 