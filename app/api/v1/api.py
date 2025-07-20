from fastapi import APIRouter
from app.api.v1 import UserManagement, MatchManager, ChatroomManager

api_router = APIRouter()

# 注册用户相关路由
api_router.include_router(UserManagement.router, prefix="/UserManagement", tags=["users"])

# 注册匹配相关路由
api_router.include_router(MatchManager.router, prefix="/MatchManager", tags=["matches"])

# 注册聊天室相关路由
api_router.include_router(ChatroomManager.router, prefix="/ChatroomManager", tags=["chatrooms"]) 