from pydantic import BaseModel, Field
from typing import Optional, Dict

# 创建匹配
class CreateMatchRequest(BaseModel):
    user_id_1: int = Field(..., description="第一个用户ID")
    user_id_2: int = Field(..., description="第二个用户ID")
    reason_1: str = Field(..., description="给用户1的匹配原因")
    reason_2: str = Field(..., description="给用户2的匹配原因")
    match_score: int = Field(..., description="匹配分数")

class CreateMatchResponse(BaseModel):
    success: bool = Field(..., description="创建是否成功")
    match_id: int = Field(..., description="新创建的匹配ID")

# 获取匹配信息
class GetMatchInfoRequest(BaseModel):
    user_id: int = Field(..., description="请求用户ID")
    match_id: int = Field(..., description="匹配ID")

class GetMatchInfoResponse(BaseModel):
    target_user_id: int = Field(..., description="目标用户ID")
    description_for_target: str = Field(..., description="给目标用户的描述")
    is_liked: bool = Field(..., description="是否已点赞")
    match_score: int = Field(..., description="匹配分数")
    mutual_game_scores: Dict = Field(..., description="互动游戏分数")
    chatroom_id: Optional[int] = Field(None, description="聊天室ID")

# 切换点赞状态
class ToggleLikeRequest(BaseModel):
    match_id: int = Field(..., description="匹配ID")

class ToggleLikeResponse(BaseModel):
    success: bool = Field(..., description="操作是否成功")

# 保存匹配到数据库
class SaveMatchToDatabaseRequest(BaseModel):
    match_id: Optional[int] = Field(None, description="匹配ID，如果不提供则保存所有匹配")

class SaveMatchToDatabaseResponse(BaseModel):
    success: bool = Field(..., description="保存是否成功")

# 🔧 MODIFIED: 新增 - 获取所有女性用户匹配
class GetNewMatchesForEveryoneRequest(BaseModel):
    user_id: Optional[int] = Field(None, description="用户ID，如果提供则只为该用户匹配")
    print_message: bool = Field(..., description="是否打印详细消息")

class GetNewMatchesForEveryoneResponse(BaseModel):
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="结果消息")