from app.config import settings

class Chatroom:
    """
    聊天室类，管理聊天室内容
    """
    def __init__(self, user1=None, user2=None, chatroom_id=None):
        self.chatroom_id = chatroom_id
        self.message_ids = []
        self.messages = []  # type: list[Message]
        self.user1 = user1
        self.user2 = user2

    def send_message(self, sender_user_id, message_, target_user_id):
        pass

    def get_messages(self):
        pass

    def save_to_database(self):
        pass 

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