from fastapi import APIRouter
from app.api.v1 import UserManagement, MatchManager

api_router = APIRouter()

# 注册用户相关路由
api_router.include_router(UserManagement.router, prefix="/users", tags=["users"])

# 注册匹配相关路由
api_router.include_router(MatchManager.router, prefix="/MatchManager", tags=["matches"]) 