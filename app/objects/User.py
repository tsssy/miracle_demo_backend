class User:
    """
    用户类，管理单一用户的数据
    """
    def __init__(self, telegram_user_name: str = None, gender: int = None, user_id: int = None):
        # 用户基本信息
        self.telegram_user_name = telegram_user_name
        self.gender = gender
        self.age = None
        self.target_gender = None
        self.user_personality_summary = None
        self.user_id = user_id
        self.match_ids = []  # type: list[int]
        self.blocked_user_ids = []  # type: list[str]

    def edit_data(self, telegram_user_name=None, gender=None, age=None, target_gender=None, user_personality_summary=None):
        """编辑用户数据"""
        if telegram_user_name is not None:
            self.telegram_user_name = telegram_user_name
        if gender is not None:
            self.gender = gender
        if age is not None:
            self.age = age
        if target_gender is not None:
            self.target_gender = target_gender
        if user_personality_summary is not None:
            self.user_personality_summary = user_personality_summary

    def get_user_id(self):
        pass

    def save_to_database(self):
        pass

    def block_user(self, blocked_user_id):
        pass

    def like_match(self, match_id):
        pass