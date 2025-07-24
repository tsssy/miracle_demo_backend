from pydantic import BaseModel, Field, validator
from typing import Optional, List

# 创建新用户
class CreateNewUserRequest(BaseModel):
    telegram_user_name: str = Field(..., description="用户的 Telegram 用户名")
    telegram_user_id: int = Field(..., description="用户的 Telegram ID")
    gender: int = Field(..., description="用户性别 1/2/3")
    
    @validator('gender')
    def validate_gender(cls, v):
        """验证性别字段只能是 1、2、3"""
        if v not in [1, 2, 3]:
            raise ValueError('性别必须是 1、2、3 中的一个值')
        return v

class CreateNewUserResponse(BaseModel):
    success: bool = Field(..., description="是否创建成功")
    user_id: int = Field(..., description="新用户的唯一ID") 

# 编辑用户年龄
class EditUserAgeRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")
    age: int = Field(..., description="用户年龄")

class EditUserAgeResponse(BaseModel):
    success: bool = Field(..., description="是否编辑成功")

# 编辑用户目标性别
class EditTargetGenderRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")
    target_gender: int = Field(..., description="用户目标性别 1/2/3")
    
    @validator('target_gender')
    def validate_target_gender(cls, v):
        """验证目标性别字段只能是 1、2、3"""
        if v not in [1, 2, 3]:
            raise ValueError('目标性别必须是 1、2、3 中的一个值')
        return v

class EditTargetGenderResponse(BaseModel):
    success: bool = Field(..., description="是否编辑成功")

# 编辑用户简介
class EditSummaryRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")
    summary: str = Field(..., description="用户简介")

class EditSummaryResponse(BaseModel):
    success: bool = Field(..., description="是否编辑成功")

# 保存用户信息到数据库
class SaveUserInfoToDatabaseRequest(BaseModel):
    user_id: Optional[int] = Field(None, description="用户ID，如果不提供则保存所有用户")

class SaveUserInfoToDatabaseResponse(BaseModel):
    success: bool = Field(..., description="是否保存成功")

# 根据用户id获取用户信息
class GetUserInfoWithUserIdRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")

class GetUserInfoWithUserIdResponse(BaseModel):
    user_id: int = Field(..., description="用户ID")
    telegram_user_name: str = Field(..., description="用户的 Telegram 用户名")
    telegram_id: int = Field(..., description="用户的 Telegram ID")
    gender: int = Field(..., description="用户性别 1/2/3")
    age: Optional[int] = Field(None, description="用户年龄")
    target_gender: Optional[int] = Field(None, description="用户目标性别 1/2/3")
    user_personality_trait: Optional[str] = Field(None, description="用户简介")
    match_ids: List[int] = Field(default_factory=list, description="用户的匹配ID列表")
    
    @validator('gender')
    def validate_gender(cls, v):
        """验证性别字段只能是 1、2、3"""
        if v not in [1, 2, 3]:
            raise ValueError('性别必须是 1、2、3 中的一个值')
        return v
    
    @validator('target_gender')
    def validate_target_gender(cls, v):
        """验证目标性别字段只能是 1、2、3"""
        if v is not None and v not in [1, 2, 3]:
            raise ValueError('目标性别必须是 1、2、3 中的一个值')
        return v

# 用户注销
class DeactivateUserRequest(BaseModel):
    user_id: int = Field(..., description="要注销的用户ID")

class DeactivateUserResponse(BaseModel):
    success: bool = Field(..., description="是否注销成功")