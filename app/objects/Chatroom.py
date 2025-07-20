class Chatroom:
    """
    聊天室类，管理聊天室内容
    """
    def __init__(self, user1=None, user2=None, chatroom_id=None):
        self.chatroom_id = chatroom_id
        self.message_ids = []
        self.messages = []  
        self.user1 = user1
        self.user2 = user2

    def send_message(self, sender_user_id, message_, target_user_id):
        pass

    def get_messages(self):
        pass

    def save_to_database(self):
        pass