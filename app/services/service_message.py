from app.schemas.message import GetMatchedUsersRequest, GetMatchedUsersResponse
from app.core.database import Database

class MessageService:
    @staticmethod
    async def get_matched_users(request: GetMatchedUsersRequest) -> GetMatchedUsersResponse:
        """
        获取匹配用户列表
        - 参数: request（GetMatchedUsersRequest对象，包含telegram_id）
        - 返回: GetMatchedUsersResponse模型
        """
        try:
            # 查找用户
            user = await Database.find_one("User", {"_id": request.telegram_id})
            if not user or not user.get("paired_user"):
                # 用户不存在或没有配对用户
                return GetMatchedUsersResponse(telegram_id_list=[])
            # paired_user字段应为Telegram ID列表
            paired_list = [int(uid) for uid in user["paired_user"]]
            return GetMatchedUsersResponse(telegram_id_list=paired_list)
        except Exception as e:
            # 异常处理，返回空列表
            return GetMatchedUsersResponse(telegram_id_list=[]) 