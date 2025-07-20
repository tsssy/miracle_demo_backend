from app.config import settings
from app.objects.Match import Match


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