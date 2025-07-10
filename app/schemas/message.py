from typing import List
from pydantic import BaseModel, Field

class GetMatchedUsersRequest(BaseModel):
    """
    获取匹配用户请求体schema
    - telegram_id: Telegram用户ID，整数类型
    """
    telegram_id: int = Field(..., description="Telegram用户ID", example=10001)

class GetMatchedUsersResponse(BaseModel):
    """
    获取匹配用户响应体schema
    - telegram_id_list: 匹配到的用户ID列表
    """
    telegram_id_list: List[int] = Field(..., description="匹配到的用户ID列表", example=[10002, 10003]) 