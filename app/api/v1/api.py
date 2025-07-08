from fastapi import APIRouter
from app.api.v1.endpoints import users

api_router = APIRouter()

# 注册用户路由
api_router.include_router(users.router, prefix="/users", tags=["users"]) 