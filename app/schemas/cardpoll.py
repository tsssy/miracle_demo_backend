from typing import Optional
from pydantic import BaseModel, Field

# 创建或编辑答案
class EditAnswer_Request(BaseModel):
    telegram_id: int = Field(..., description="用户的 Telegram ID")
    question_id: str = Field(..., description="对应的问题ID")
    new_answer: str = Field(..., description="新的答案内容")
    is_send: bool = Field(..., description="是否发送")
    answer_id: Optional[str] = Field(None, description="要编辑的答案ID (如果提供，则为编辑模式)")
    answer_is_draft: Optional[bool] = Field(None, description="答案是否为草稿")

class EditAnswer_Response(BaseModel):
    answer_id: str = Field(..., description="答案ID")
    answer_string: str = Field(..., description="答案内容")
    is_draft: bool = Field(..., description="是否为草稿")

# 更改问题状态
class ToggleQuestionSave_Request(BaseModel):
    telegram_id: int = Field(..., description="用户的 Telegram ID")
    question_id: str = Field(..., description="问题ID")

class ToggleQuestionSave_Response(BaseModel):
    is_saved: bool = Field(..., description="当前问题的保存状态")

# 获取问题
class GetQuestion_Request(BaseModel):
    telegram_id: int = Field(..., description="用户的 Telegram ID")
    is_swiping_toward_left: bool = Field(..., description="是否向左滑动 (用于获取下一个问题)")

class GetQuestion_Response(BaseModel):
    question_id: str = Field(..., description="问题ID")
    question_content: str = Field(..., description="问题内容")
    is_saved: bool = Field(..., description="当前问题是否已保存")
    answer_id: Optional[str] = Field(None, description="如果存在，表示用户对该问题的答案ID")
    answer_string: Optional[str] = Field(None, description="如果存在，表示用户对该问题的答案内容")
    answer_is_draft: Optional[bool] = Field(None, description="如果存在，表示该答案是否为草稿")

# 屏蔽答案
class BlockAnswer_Request(BaseModel):
    telegram_id: int = Field(..., description="用户的 Telegram ID")
    answer_id: str = Field(..., description="要屏蔽的答案ID")

class BlockAnswer_Response(BaseModel):
    success: bool = Field(..., description="操作是否成功")

# 点赞答案
class LikeAnswer_Request(BaseModel):
    telegram_id: int = Field(..., description="用户的 Telegram ID")
    answer_id: str = Field(..., description="要点赞的答案ID")

class LikeAnswer_Response(BaseModel):
    paired_telegram_id: int = Field(..., description="配对用户的 Telegram ID")
    is_liked: bool = Field(..., description="当前是否为点赞状态")

# 获取答案
class GetAnswer_Request(BaseModel):
    telegram_id: int = Field(..., description="用户的 Telegram ID")
    is_swiping_toward_left: bool = Field(..., description="是否向左滑动 (用于获取下一个答案)")

class GetAnswer_Response(BaseModel):
    answer_id: str = Field(..., description="答案ID")
    answer_content: str = Field(..., description="答案内容")
    question_string: str = Field(..., description="对应的问题内容")
    is_liked: bool = Field(..., description="当前是否为点赞状态")

