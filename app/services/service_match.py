from app.config import settings

class Match:
    """
    匹配类，管理一个Match
    """
    def __init__(self, telegram_user_session_id_1, telegram_user_session_id_2, reason_to_id_1, reason_to_id_2, match_score):
        self.match_id = None
        self.telegram_user_session_id_1 = telegram_user_session_id_1
        self.telegram_user_session_id_2 = telegram_user_session_id_2
        self.description_to_user_1 = reason_to_id_1
        self.description_to_user_2 = reason_to_id_2
        self.is_liked = False
        self.match_score = match_score
        self.mutual_game_scores = {}
        self.chatroom = None

    def get_target_user(self, user_id):
        pass

    def get_reason_for_profile(self):
        pass

    def get_match_id(self):
        pass

    def toggle_like(self):
        pass

    def save_to_database(self):
        pass 

class MatchManager:
    """
    匹配管理单例，负责管理所有匹配
    """
    _instance = None
    database_address = settings.MONGODB_URL

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.match_list = []
        return cls._instance

    def create_match(self, user_id_1, user_id_2, reason_1, reason_2, match_score):
        pass

    def get_match(self, match_id):
        pass

    def toggle_like(self, match_id):
        pass

    def save_to_database(self, match_id=None):
        pass

    def get_match_info(self, user_id, match_id):
        pass 