"""
Singleton Status Reporter
用于报告所有单例服务中字典和列表的状态
"""
from typing import Dict, Any
import json


class SingletonStatusReporter:
    """
    单例状态报告器，收集所有单例服务的状态信息
    """
    
    @staticmethod
    def get_singleton_status() -> Dict[str, Any]:
        """
        获取所有单例服务的状态信息
        返回包含所有单例字典大小和内容摘要的字典
        """
        status = {}
        
        # UserManagement 状态
        try:
            from app.services.https.UserManagement import UserManagement
            user_mgmt = UserManagement()
            status["UserManagement"] = {
                "user_list": {
                    "size": len(user_mgmt.user_list),
                    "keys": list(user_mgmt.user_list.keys()) if len(user_mgmt.user_list) <= 10 else f"Too many keys ({len(user_mgmt.user_list)}), showing first 10: {list(user_mgmt.user_list.keys())[:10]}"
                },
                "male_user_list": {
                    "size": len(user_mgmt.male_user_list),
                    "keys": list(user_mgmt.male_user_list.keys()) if len(user_mgmt.male_user_list) <= 10 else f"Too many keys ({len(user_mgmt.male_user_list)}), showing first 10: {list(user_mgmt.male_user_list.keys())[:10]}"
                },
                "female_user_list": {
                    "size": len(user_mgmt.female_user_list),
                    "keys": list(user_mgmt.female_user_list.keys()) if len(user_mgmt.female_user_list) <= 10 else f"Too many keys ({len(user_mgmt.female_user_list)}), showing first 10: {list(user_mgmt.female_user_list.keys())[:10]}"
                },
                "_user_id_counter": getattr(user_mgmt, '_user_id_counter', 'Not initialized')
            }
        except Exception as e:
            status["UserManagement"] = {"error": str(e)}
        
        # MatchManager 状态
        try:
            from app.services.https.MatchManager import MatchManager
            match_mgr = MatchManager()
            status["MatchManager"] = {
                "match_list": {
                    "size": len(match_mgr.match_list),
                    "items": match_mgr.match_list if len(match_mgr.match_list) <= 5 else f"Too many items ({len(match_mgr.match_list)}), showing first 5: {match_mgr.match_list[:5]}"
                }
            }
        except Exception as e:
            status["MatchManager"] = {"error": str(e)}
        
        # ChatroomManager 状态
        try:
            from app.services.https.ChatroomManager import ChatroomManager
            chatroom_mgr = ChatroomManager()
            status["ChatroomManager"] = {
                "chatrooms": {
                    "size": len(chatroom_mgr.chatrooms),
                    "keys": list(chatroom_mgr.chatrooms.keys()) if len(chatroom_mgr.chatrooms) <= 10 else f"Too many keys ({len(chatroom_mgr.chatrooms)}), showing first 10: {list(chatroom_mgr.chatrooms.keys())[:10]}"
                }
            }
        except Exception as e:
            status["ChatroomManager"] = {"error": str(e)}
        
        return status
    
    @staticmethod
    def format_status_for_logging(status: Dict[str, Any]) -> str:
        """
        将状态信息格式化为适合日志记录的字符串
        """
        try:
            return json.dumps(status, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            return f"Error formatting status: {e}\nRaw status: {status}"
    
    @staticmethod
    def get_status_summary() -> str:
        """
        获取状态摘要的简短版本
        """
        try:
            status = SingletonStatusReporter.get_singleton_status()
            summary_parts = []
            
            for service_name, service_data in status.items():
                if "error" in service_data:
                    summary_parts.append(f"{service_name}: ERROR - {service_data['error']}")
                else:
                    sizes = []
                    for dict_name, dict_info in service_data.items():
                        if isinstance(dict_info, dict) and "size" in dict_info:
                            sizes.append(f"{dict_name}({dict_info['size']})")
                        elif dict_name == "_user_id_counter":
                            sizes.append(f"counter({dict_info})")
                    summary_parts.append(f"{service_name}: {', '.join(sizes)}")
            
            return " | ".join(summary_parts)
        except Exception as e:
            return f"Error generating summary: {e}"