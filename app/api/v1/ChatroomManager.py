from fastapi import APIRouter, HTTPException
from app.schemas.ChatroomManager import (
    GetOrCreateChatroomRequest, GetOrCreateChatroomResponse,
    GetChatHistoryRequest, GetChatHistoryResponse,
    SaveChatroomHistoryRequest, SaveChatroomHistoryResponse,
    SendMessageRequest, SendMessageResponse
)
from app.services.https.ChatroomManager import ChatroomManager

router = APIRouter()

@router.post("/get_or_create_chatroom", response_model=GetOrCreateChatroomResponse)
# 获取或创建聊天室
async def get_or_create_chatroom(request: GetOrCreateChatroomRequest):
    chatroom_manager = ChatroomManager()
    try:
        chatroom_id = await chatroom_manager.get_or_create_chatroom(
            user_id_1=request.user_id_1,
            user_id_2=request.user_id_2,
            match_id=request.match_id
        )
        if chatroom_id is None:
            raise HTTPException(status_code=404, detail="无法创建或获取聊天室")
        
        return GetOrCreateChatroomResponse(success=True, chatroom_id=chatroom_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/get_chat_history", response_model=GetChatHistoryResponse)
# 获取聊天历史记录
async def get_chat_history(request: GetChatHistoryRequest):
    chatroom_manager = ChatroomManager()
    try:
        chat_history = await chatroom_manager.get_chatroom_history(
            chatroom_id=request.chatroom_id,
            user_id=request.user_id
        )
        
        # 转换格式以匹配响应模型
        messages = []
        for message_content, datetime_str, sender_id, sender_name in chat_history:
            messages.append({
                "sender_name": sender_name,
                "message": message_content,
                "datetime": datetime_str
            })
        
        return GetChatHistoryResponse(success=True, messages=messages)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/save_chatroom_history", response_model=SaveChatroomHistoryResponse)
# 保存聊天室历史记录到数据库
async def save_chatroom_history(request: SaveChatroomHistoryRequest):
    chatroom_manager = ChatroomManager()
    try:
        success = await chatroom_manager.save_chatroom_history(
            chatroom_id=request.chatroom_id
        )
        return SaveChatroomHistoryResponse(success=success)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/send_message", response_model=SendMessageResponse)
# 发送消息到聊天室
async def send_message(request: SendMessageRequest):
    chatroom_manager = ChatroomManager()
    try:
        result = await chatroom_manager.send_message(
            chatroom_id=request.chatroom_id,
            sender_user_id=request.sender_user_id,
            message_content=request.message_content
        )
        return SendMessageResponse(
            success=result["success"],
            match_id=result["match_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 