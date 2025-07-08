from typing import Optional
from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    telegram_id: str = Field(..., description="用户的 Telegram ID")
    mode: str = Field(..., description="用户关系模式", pattern="^(friends|long-term_compinionship|short-term_compinionship)$")


class UserResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="用户ID") # MongoDB的_id字段
    telegram_id: str = Field(..., description="用户的 Telegram ID")
    mode: str = Field(..., description="用户关系模式")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            str: lambda v: v # 这里我们假设ObjectId已经被转换成了str
        } 