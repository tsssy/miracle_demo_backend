from pydantic import BaseModel, Field
from typing import Optional, List, Tuple

# Get or create chatroom
class GetOrCreateChatroomRequest(BaseModel):
    user_id_1: int = Field(..., description="第一个用户的ID")
    user_id_2: int = Field(..., description="第二个用户的ID")
    match_id: int = Field(..., description="匹配ID")

class GetOrCreateChatroomResponse(BaseModel):
    success: bool = Field(..., description="是否操作成功")
    chatroom_id: int = Field(..., description="聊天室ID")

# Get chat history
class GetChatHistoryRequest(BaseModel):
    chatroom_id: int = Field(..., description="聊天室ID")
    user_id: int = Field(..., description="请求用户的ID")

class ChatMessage(BaseModel):
    sender_name: str = Field(..., description="发送者名称或'I'")
    message: str = Field(..., description="消息内容")
    datetime: str = Field(..., description="消息时间")

class GetChatHistoryResponse(BaseModel):
    success: bool = Field(..., description="是否获取成功")
    messages: List[ChatMessage] = Field(default=[], description="聊天记录")

# Save chatroom history
class SaveChatroomHistoryRequest(BaseModel):
    chatroom_id: Optional[int] = Field(None, description="聊天室ID，如果不提供则保存所有聊天室")

class SaveChatroomHistoryResponse(BaseModel):
    success: bool = Field(..., description="是否保存成功")

# Send message
class SendMessageRequest(BaseModel):
    chatroom_id: int = Field(..., description="聊天室ID")
    sender_user_id: int = Field(..., description="发送者用户ID")
    message_content: str = Field(..., description="消息内容")

class SendMessageResponse(BaseModel):
    success: bool = Field(..., description="是否发送成功")
    match_id: Optional[int] = Field(None, description="关联的匹配ID")