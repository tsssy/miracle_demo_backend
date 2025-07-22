# Miracle Demo Backend API Summary

## HTTP API

---

### 用户管理 UserManagement

#### 1. 创建新用户 create_new_user
- **Route:** `/UserManagement/create_new_user`
- **Method:** POST
- **请求体 Request Body:**

**CreateNewUserRequest**
```python
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
```
- **响应体 Response Body:**

**CreateNewUserResponse**
```python
class CreateNewUserResponse(BaseModel):
    success: bool = Field(..., description="是否创建成功")
    user_id: int = Field(..., description="新用户的唯一ID")
```

---

#### 2. 编辑用户年龄 edit_user_age
- **Route:** `/UserManagement/edit_user_age`
- **Method:** POST
- **请求体 Request Body:**

**EditUserAgeRequest**
```python
class EditUserAgeRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")
    age: int = Field(..., description="用户年龄")
```
- **响应体 Response Body:**

**EditUserAgeResponse**
```python
class EditUserAgeResponse(BaseModel):
    success: bool = Field(..., description="是否编辑成功")
```

---

#### 3. 编辑用户目标性别 edit_target_gender
- **Route:** `/UserManagement/edit_target_gender`
- **Method:** POST
- **请求体 Request Body:**

**EditTargetGenderRequest**
```python
class EditTargetGenderRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")
    target_gender: int = Field(..., description="用户目标性别 1/2/3")
    @validator('target_gender')
    def validate_target_gender(cls, v):
        """验证目标性别字段只能是 1、2、3"""
        if v not in [1, 2, 3]:
            raise ValueError('目标性别必须是 1、2、3 中的一个值')
        return v
```
- **响应体 Response Body:**

**EditTargetGenderResponse**
```python
class EditTargetGenderResponse(BaseModel):
    success: bool = Field(..., description="是否编辑成功")
```

---

#### 4. 编辑用户简介 edit_summary
- **Route:** `/UserManagement/edit_summary`
- **Method:** POST
- **请求体 Request Body:**

**EditSummaryRequest**
```python
class EditSummaryRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")
    summary: str = Field(..., description="用户简介")
```
- **响应体 Response Body:**

**EditSummaryResponse**
```python
class EditSummaryResponse(BaseModel):
    success: bool = Field(..., description="是否编辑成功")
```

---

#### 5. 保存用户信息到数据库 save_to_database
- **Route:** `/UserManagement/save_to_database`
- **Method:** POST
- **请求体 Request Body:**

**SaveUserInfoToDatabaseRequest**
```python
class SaveUserInfoToDatabaseRequest(BaseModel):
    user_id: Optional[int] = Field(None, description="用户ID，如果不提供则保存所有用户")
```
- **响应体 Response Body:**

**SaveUserInfoToDatabaseResponse**
```python
class SaveUserInfoToDatabaseResponse(BaseModel):
    success: bool = Field(..., description="是否保存成功")
```

---

#### 6. 根据用户id获取用户信息 get_user_info_with_user_id
- **Route:** `/UserManagement/get_user_info_with_user_id`
- **Method:** POST
- **请求体 Request Body:**

**GetUserInfoWithUserIdRequest**
```python
class GetUserInfoWithUserIdRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")
```
- **响应体 Response Body:**

**GetUserInfoWithUserIdResponse**
```python
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
```

---

### 匹配管理 MatchManager

#### 1. 创建匹配 create_match
- **Route:** `/MatchManager/create_match`
- **Method:** POST
- **请求体 Request Body:**

**CreateMatchRequest**
```python
class CreateMatchRequest(BaseModel):
    user_id_1: int = Field(..., description="第一个用户ID")
    user_id_2: int = Field(..., description="第二个用户ID")
    reason_1: str = Field(..., description="给用户1的匹配原因")
    reason_2: str = Field(..., description="给用户2的匹配原因")
    match_score: int = Field(..., description="匹配分数")
```
- **响应体 Response Body:**

**CreateMatchResponse**
```python
class CreateMatchResponse(BaseModel):
    match_id: int = Field(..., description="新创建的匹配ID")
```

---

#### 2. 获取匹配信息 get_match_info
- **Route:** `/MatchManager/get_match_info`
- **Method:** POST
- **请求体 Request Body:**

**GetMatchInfoRequest**
```python
class GetMatchInfoRequest(BaseModel):
    user_id: int = Field(..., description="请求用户ID")
    match_id: int = Field(..., description="匹配ID")
```
- **响应体 Response Body:**

**GetMatchInfoResponse**
```python
class GetMatchInfoResponse(BaseModel):
    target_user_id: int = Field(..., description="目标用户ID")
    description_for_target: str = Field(..., description="给目标用户的描述")
    is_liked: bool = Field(..., description="是否已点赞")
    match_score: int = Field(..., description="匹配分数")
    mutual_game_scores: Dict = Field(..., description="互动游戏分数")
    chatroom_id: Optional[int] = Field(None, description="聊天室ID")
```

---

#### 3. 切换点赞状态 toggle_like
- **Route:** `/MatchManager/toggle_like`
- **Method:** POST
- **请求体 Request Body:**

**ToggleLikeRequest**
```python
class ToggleLikeRequest(BaseModel):
    match_id: int = Field(..., description="匹配ID")
```
- **响应体 Response Body:**

**ToggleLikeResponse**
```python
class ToggleLikeResponse(BaseModel):
    success: bool = Field(..., description="操作是否成功")
```

---

#### 4. 保存匹配到数据库 save_to_database
- **Route:** `/MatchManager/save_to_database`
- **Method:** POST
- **请求体 Request Body:**

**SaveMatchToDatabaseRequest**
```python
class SaveMatchToDatabaseRequest(BaseModel):
    match_id: Optional[int] = Field(None, description="匹配ID，如果不提供则保存所有匹配")
```
- **响应体 Response Body:**

**SaveMatchToDatabaseResponse**
```python
class SaveMatchToDatabaseResponse(BaseModel):
    success: bool = Field(..., description="保存是否成功")
```

---

### 聊天室管理 ChatroomManager

#### 1. 获取或创建聊天室 get_or_create_chatroom
- **Route:** `/ChatroomManager/get_or_create_chatroom`
- **Method:** POST
- **请求体 Request Body:**

**GetOrCreateChatroomRequest**
```python
class GetOrCreateChatroomRequest(BaseModel):
    user_id_1: int = Field(..., description="第一个用户的ID")
    user_id_2: int = Field(..., description="第二个用户的ID")
    match_id: int = Field(..., description="匹配ID")
```
- **响应体 Response Body:**

**GetOrCreateChatroomResponse**
```python
class GetOrCreateChatroomResponse(BaseModel):
    success: bool = Field(..., description="是否操作成功")
    chatroom_id: int = Field(..., description="聊天室ID")
```

---

#### 2. 获取聊天历史记录 get_chat_history
- **Route:** `/ChatroomManager/get_chat_history`
- **Method:** POST
- **请求体 Request Body:**

**GetChatHistoryRequest**
```python
class GetChatHistoryRequest(BaseModel):
    chatroom_id: int = Field(..., description="聊天室ID")
    user_id: int = Field(..., description="请求用户的ID")
```
- **响应体 Response Body:**

**GetChatHistoryResponse**
```python
class ChatMessage(BaseModel):
    sender_name: str = Field(..., description="发送者名称或'I'")
    message: str = Field(..., description="消息内容")
    datetime: str = Field(..., description="消息时间")

class GetChatHistoryResponse(BaseModel):
    success: bool = Field(..., description="是否获取成功")
    messages: List[ChatMessage] = Field(default=[], description="聊天记录")
```

---

#### 3. 保存聊天室历史记录 save_chatroom_history
- **Route:** `/ChatroomManager/save_chatroom_history`
- **Method:** POST
- **请求体 Request Body:**

**SaveChatroomHistoryRequest**
```python
class SaveChatroomHistoryRequest(BaseModel):
    chatroom_id: Optional[int] = Field(None, description="聊天室ID，如果不提供则保存所有聊天室")
```
- **响应体 Response Body:**

**SaveChatroomHistoryResponse**
```python
class SaveChatroomHistoryResponse(BaseModel):
    success: bool = Field(..., description="是否保存成功")
``` 