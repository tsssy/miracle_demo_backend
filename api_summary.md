# Miracle Demo Backend API Summary

## HTTP API

### UserManagement

#### 1. 创建新用户
- **Route:** `/UserManagement/create_new_user`
- **Method:** POST
- **Request Body:** `CreateNewUserRequest`
- **Response Body:** `CreateNewUserResponse`

#### 2. 编辑用户年龄
- **Route:** `/UserManagement/edit_user_age`
- **Method:** POST
- **Request Body:** `EditUserAgeRequest`
- **Response Body:** `EditUserAgeResponse`

#### 3. 编辑用户目标性别
- **Route:** `/UserManagement/edit_target_gender`
- **Method:** POST
- **Request Body:** `EditTargetGenderRequest`
- **Response Body:** `EditTargetGenderResponse`

#### 4. 编辑用户简介
- **Route:** `/UserManagement/edit_summary`
- **Method:** POST
- **Request Body:** `EditSummaryRequest`
- **Response Body:** `EditSummaryResponse`

#### 5. 保存用户信息到数据库
- **Route:** `/UserManagement/save_to_database`
- **Method:** POST
- **Request Body:** `SaveUserInfoToDatabaseRequest`
- **Response Body:** `SaveUserInfoToDatabaseResponse`

#### 6. 根据用户id获取用户信息
- **Route:** `/UserManagement/get_user_info_with_user_id`
- **Method:** POST
- **Request Body:** `GetUserInfoWithUserIdRequest`
- **Response Body:** `GetUserInfoWithUserIdResponse`

---

### MatchManager

#### 1. 创建匹配
- **Route:** `/MatchManager/create_match`
- **Method:** POST
- **Request Body:** `CreateMatchRequest`
- **Response Body:** `CreateMatchResponse`

#### 2. 获取匹配信息
- **Route:** `/MatchManager/get_match_info`
- **Method:** POST
- **Request Body:** `GetMatchInfoRequest`
- **Response Body:** `GetMatchInfoResponse`

#### 3. 切换点赞状态
- **Route:** `/MatchManager/toggle_like`
- **Method:** POST
- **Request Body:** `ToggleLikeRequest`
- **Response Body:** `ToggleLikeResponse`

#### 4. 保存匹配到数据库
- **Route:** `/MatchManager/save_to_database`
- **Method:** POST
- **Request Body:** `SaveMatchToDatabaseRequest`
- **Response Body:** `SaveMatchToDatabaseResponse`

---

### ChatroomManager

#### 1. 获取或创建聊天室
- **Route:** `/ChatroomManager/get_or_create_chatroom`
- **Method:** POST
- **Request Body:** `GetOrCreateChatroomRequest`
- **Response Body:** `GetOrCreateChatroomResponse`

#### 2. 获取聊天历史记录
- **Route:** `/ChatroomManager/get_chat_history`
- **Method:** POST
- **Request Body:** `GetChatHistoryRequest`
- **Response Body:** `GetChatHistoryResponse`

#### 3. 保存聊天室历史记录
- **Route:** `/ChatroomManager/save_chatroom_history`
- **Method:** POST
- **Request Body:** `SaveChatroomHistoryRequest`
- **Response Body:** `SaveChatroomHistoryResponse`

---

## WebSocket API

### /ws/base
- **说明：** 基础 WebSocket 连接，使用 `ConnectionHandler` 处理。
- **认证消息格式：** `{ "user_id": int }`
- **消息类型：**
  - `message`：普通消息广播，格式 `{ "type": "message", "from": user_id, "content": ... }`
  - 认证失败/成功、错误等均为 JSON 格式返回

### /ws/match
- **说明：** 匹配专用 WebSocket，使用 `MatchSessionHandler` 处理。
- **认证消息格式：** `{ "user_id": int }`
- **消息类型：**
  - `match_info`：匹配信息推送
  - `match_error`：匹配错误信息
  - 连接时自动推送匹配结果

### /ws/message
- **说明：** 消息专用 WebSocket，使用 `MessageConnectionHandler` 处理。
- **认证消息格式：** `{ "user_id": int }`
- **消息类型：**
  - `private_chat_init`：初始化私聊，需传 `target_user_id` 和 `match_id`
  - `private`：私聊消息，需传 `target_user_id`, `chatroom_id`, `content`
  - `broadcast`：广播消息，需传 `content`
  - `private_message`：私聊消息推送
  - `broadcast_message`：广播消息推送
  - `user_joined`/`user_left`：用户加入/离开通知
  - `message_status`/`broadcast_status`：消息状态反馈
  - 错误信息均为 JSON 格式返回

---

> **注：** 所有请求/响应体的详细字段定义请参考 `app/schemas/` 目录下的同名 schema 文件。

// 本文档自动生成，所有接口均带有中文注释说明。 