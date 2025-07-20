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