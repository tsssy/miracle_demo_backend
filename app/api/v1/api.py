from fastapi import APIRouter
from app.api.v1.endpoints import users
from app.api.v1.endpoints import cardpoll
from app.api.v1.endpoints import message  # 新增消息相关路由
from app.api.v1.endpoints import question_answer_management  # 新增问答管理相关路由

api_router = APIRouter()

# 注册用户路由
api_router.include_router(users.router, prefix="/users", tags=["users"])
# 注册卡片路由
api_router.include_router(cardpoll.router, prefix="/cardpoll", tags=["cardpoll"])
# 注册消息路由
api_router.include_router(message.router, prefix="/message", tags=["message"])
# 注册问答管理路由
api_router.include_router(question_answer_management.router, prefix="/question_answer_management", tags=["question_answer_management"]) 