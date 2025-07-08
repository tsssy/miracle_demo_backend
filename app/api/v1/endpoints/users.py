from fastapi import APIRouter, HTTPException, status
from app.services.service_users import UserService
from app.schemas.users import UserCreateRequest, UserResponse

router = APIRouter()


@router.post("/male_users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_male_user(user_data: UserCreateRequest):
    """创建一个新的男性用户"""
    try:
        created_user = await UserService.create_male_user(user_data.dict())
        return created_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"创建用户失败: {e}") 