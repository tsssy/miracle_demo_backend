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
    GetUserExistResponse
)
from app.utils.my_logger import MyLogger

logger = MyLogger("user_endpoints")

router = APIRouter()

@router.post("/male_users", response_model=CreateMaleUserResponse, status_code=status.HTTP_200_OK)
async def users_create_male_user(request: CreateMaleUserRequest) -> Any:
    """
    新建男用户API接口
    - 参数: request（包含telegram_id和可选mode的请求体，类型为int）
    - 返回: 是否成功创建男用户的状态
    """
    try:
        result = await UserService.create_new_male_user(request)
        return result
    except Exception as e:
        logger.error(f"创建男用户失败: {e}")
        return CreateMaleUserResponse(success=False)

@router.post("/female_users", response_model=CreateNewFemaleUserResponse, status_code=status.HTTP_200_OK)
async def users_create_female_user(request: CreateNewFemaleUserRequest) -> Any:
    """
    新建女用户API接口
    - 参数: request（包含telegram_id的请求体，类型为int）
    - 返回: 是否成功创建女性用户的状态
    - 流程: 在telegram_sessions表中查找telegram_id，如果找到则创建用户和问题
    """
    try:
        result = await UserService.create_new_female_user(request.telegram_id)
        return result
    except Exception as e:
        logger.error(f"创建女性用户失败: {e}")
        return CreateNewFemaleUserResponse(success=False)

@router.post("/telegram_session", response_model=GetTelegramSessionGenderResponse)
async def users_get_user_from_telegram_session(request: GetTelegramSessionGenderRequest) -> Any:
    """
    根据telegram_id从telegram_sessions表中获取用户性别
    - 参数: request（包含telegram_id的请求体，类型为int）
    - 返回: 用户性别信息
    """
    try:
        user_info = await UserService.get_user_from_telegram_session(request)
        return user_info
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取用户性别失败: {e}")

@router.post("/user_exist", response_model=GetUserExistResponse)
async def user_exist(request: GetUserExistRequest) -> GetUserExistResponse:
    """
    查询用户是否存在（定义占位，未实现）
    - 参数: request（包含telegram_id的请求体）
    - 返回: 用户是否存在
    """
    # TODO: 实现用户存在性查询逻辑
    raise NotImplementedError("get_user_exist功能未实现") 