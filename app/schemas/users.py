from typing import Optional
from pydantic import BaseModel, Field


class GetTelegramSessionGenderRequest(BaseModel):
    """
    获取telegram_sessions性别请求体schema
    - telegram_id: Telegram用户ID，整数类型
    """
    telegram_id: int = Field(..., description="Telegram用户ID", example=123456789)

class GetTelegramSessionGenderResponse(BaseModel):
    """
    获取telegram_sessions性别响应体schema
    - gender: 用户性别，1=女, 2=男, 3=others，范围[1,3]
    """
    gender: int = Field(..., description="用户的性别: 1=女, 2=男, 3=others", ge=1, le=3, example=2)


class CreateNewFemaleUserRequest(BaseModel):
    """
    新建女用户的请求体schema
    - telegram_id: 用户的 Telegram ID，整数类型
    """
    telegram_id: int = Field(..., description="用户的 Telegram ID", example=123456789)


class CreateNewFemaleUserResponse(BaseModel):
    """
    新建女用户的响应体schema
    - success: 是否成功创建女性用户，布尔类型
    """
    success: bool = Field(..., description="是否成功创建女性用户", example=True)


class CreateMaleUserRequest(BaseModel):
    """
    新建男用户的请求体schema
    - telegram_id: 用户的 Telegram ID，整数类型
    - mode: 用户关系模式，1=friends, 2=long-term_compinionship, 3=short-term_compinionship，可选
    """
    telegram_id: int = Field(..., description="用户的 Telegram ID", example=123456789)
    mode: Optional[int] = Field(None, description="用户关系模式: 1=friends, 2=long-term_compinionship, 3=short-term_compinionship", ge=1, le=3, example=1)

class CreateMaleUserResponse(BaseModel):
    """
    新建男用户的响应体schema
    - success: 是否成功创建男用户，布尔类型
    """
    success: bool = Field(..., description="是否成功创建男用户", example=True)


class GetUserExistRequest(BaseModel):
    """
    查询用户是否存在的请求体schema
    - telegram_id: Telegram用户ID，整数类型
    """
    telegram_id: int = Field(..., description="Telegram用户ID", example=10001)

class GetUserExistResponse(BaseModel):
    """
    查询用户是否存在的响应体schema
    - success: 用户是否存在，布尔类型
    """
    success: bool = Field(..., description="用户是否存在", example=True) 