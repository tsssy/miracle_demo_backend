from app.schemas.message import GetMatchedUsersRequest, GetMatchedUsersResponse

class MessageService:
    @staticmethod
    async def get_matched_users(request: GetMatchedUsersRequest) -> GetMatchedUsersResponse:
        """
        获取匹配用户列表（返回示例数据）
        - 参数: request（GetMatchedUsersRequest对象，包含telegram_id）
        - 返回: GetMatchedUsersResponse模型
        """
        # 返回一组示例数据
        return GetMatchedUsersResponse(
            telegram_id_list=[10002, 10003, 10004]
        ) 