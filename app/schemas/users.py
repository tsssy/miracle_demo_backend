from typing import Optional
from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    telegram_id: str = Field(..., description="用户的 Telegram ID")
    mode: int = Field(..., description="用户关系模式: 1=friends, 2=long-term_compinionship, 3=short-term_compinionship", ge=1, le=3)


class UserResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="用户ID") # MongoDB的_id字段
    telegram_id: str = Field(..., description="用户的 Telegram ID")
    mode: int = Field(..., description="用户关系模式: 1=friends, 2=long-term_compinionship, 3=short-term_compinionship")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            str: lambda v: v # 这里我们假设ObjectId已经被转换成了str
        }


class UserGenderResponse(BaseModel):
    gender: str = Field(..., description="用户的性别")


class UserGenderRequest(BaseModel):
    user_id: str = Field(..., description="用户ID") 