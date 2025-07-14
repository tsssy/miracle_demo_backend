from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class NewQuestionRequest(BaseModel):
    """
    新建问题请求体
    - telegram_id: Telegram用户ID
    - question_string: 问题内容
    - is_draft: 是否为草稿，默认False
    """
    telegram_id: int = Field(..., description="Telegram用户ID", example=10001)
    question_string: str = Field(..., description="问题内容", example="你喜欢什么颜色？")
    is_draft: Optional[bool] = Field(False, description="是否为草稿", example=False)

class NewQuestionResponse(BaseModel):
    """
    新建问题响应体
    - success: 是否成功
    """
    success: bool = Field(..., description="是否成功", example=True)

class ToggleQuestionActiveRequest(BaseModel):
    """
    切换问题激活状态请求体
    - question_id: 问题ID
    """
    question_id: str = Field(..., description="问题ID", example="q123456")

class ToggleQuestionActiveResponse(BaseModel):
    """
    切换问题激活状态响应体
    - success: 是否成功
    """
    success: bool = Field(..., description="是否成功", example=True)

class GetAnswerListRequest(BaseModel):
    """
    获取问题答案列表请求体
    - question_id: 问题ID
    """
    question_id: str = Field(..., description="问题ID", example="q123456")

class GetAnswerListResponse(BaseModel):
    """
    获取问题答案列表响应体
    - answer_list: 答案字符串列表
    - answer_string: 答案字符串列表（冗余，按需求保留）
    """
    answer_list: List[str] = Field(..., description="答案字符串列表", example=["蓝色", "红色"])
    answer_string: List[str] = Field(..., description="答案字符串列表（冗余）", example=["蓝色", "红色"])

class GetQuestionListRequest(BaseModel):
    """
    获取问题列表请求体
    - telegram_id: Telegram用户ID
    """
    telegram_id: int = Field(..., description="Telegram用户ID", example=10001)

class GetQuestionListResponse(BaseModel):
    """
    获取问题列表响应体
    - question_list: 问题ID列表
    - question_strings: 问题内容列表
    """
    question_list: List[str] = Field(..., description="问题ID列表", example=["q1", "q2"])
    question_strings: List[str] = Field(..., description="问题内容列表", example=["你喜欢什么颜色？", "你喜欢什么运动？"])

class GetQAMAnswerRequest(BaseModel):
    """
    获取问答答案请求体
    - telegram_id: Telegram用户ID
    """
    telegram_id: int = Field(..., description="Telegram用户ID", example=10001)

class GetQAMAnswerResponse(BaseModel):
    """
    获取问答答案响应体
    - answer_id_list: 答案ID列表
    - question_id_list: 问题ID列表
    - answer_content: 答案内容列表
    - question_content: 问题内容列表
    """
    answer_id_list: List[str] = Field(..., description="答案ID列表", example=["a1", "a2"])
    question_id_list: List[str] = Field(..., description="问题ID列表", example=["q1", "q2"])
    answer_content: List[str] = Field(..., description="答案内容列表", example=["蓝色", "足球"])
    question_content: List[str] = Field(..., description="问题内容列表", example=["你喜欢什么颜色？", "你喜欢什么运动？"]) 

class GetAnswerInfoRequest(BaseModel):
    answer_id: str

class GetAnswerInfoResponse(BaseModel):
    answer_id: str
    content: str
    question_id: str
    telegram_id: str
    is_draft: bool
    created_at: datetime
    liked_user_ids: List[str]
    is_active: bool 