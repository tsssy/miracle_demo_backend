from app.config import settings
from app.objects.Chatroom import Chatroom


class ChatroomManager:
    """
    聊天室管理器，全局唯一，管理所有聊天室
    """
    _instance = None
    database_address = settings.MONGODB_URL

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.chatrooms = {}
        return cls._instance

    def get_chatroom_history(self, chatroom_id, user_id):
        pass