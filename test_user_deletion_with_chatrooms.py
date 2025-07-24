#!/usr/bin/env python3
"""
全面测试用户删除功能，特别关注聊天室清理逻辑
测试场景：
1. 创建多个用户
2. 创建多个匹配和聊天室
3. 发送消息
4. 删除用户，验证相关聊天室和消息被正确删除
"""

import asyncio
import httpx
import json
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Database
from app.services.https.UserManagement import UserManagement
from app.services.https.MatchManager import MatchManager
from app.services.https.ChatroomManager import ChatroomManager


class UserDeletionChatroomTest:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.test_users = []
        self.test_matches = []
        self.test_chatrooms = []
        self.test_messages = []

    async def setup_test_data(self):
        """创建测试数据：用户、匹配、聊天室、消息"""
        print("=== 设置测试数据 ===")
        
        # 初始化数据库连接
        await Database.connect()
        print("数据库连接已初始化")
        
        # 初始化服务
        user_manager = UserManagement()
        await user_manager.initialize_from_database()
        
        match_manager = MatchManager()
        await match_manager.construct()
        
        chatroom_manager = ChatroomManager()
        await chatroom_manager.construct()
        
        # 创建测试用户
        test_user_data = [
            {"name": "TestUser1", "id": 10001, "gender": 1, "age": 25},  # 男性
            {"name": "TestUser2", "id": 10002, "gender": 2, "age": 23},  # 女性
            {"name": "TestUser3", "id": 10003, "gender": 1, "age": 27},  # 男性
            {"name": "TestUser4", "id": 10004, "gender": 2, "age": 24},  # 女性
        ]
        
        for user_data in test_user_data:
            user_id = user_manager.create_new_user(
                user_data["name"], 
                user_data["id"], 
                user_data["gender"]
            )
            user_manager.edit_user_age(user_id, user_data["age"])
            user_manager.edit_target_gender(user_id, 3 - user_data["gender"])  # 异性
            user_manager.edit_summary(user_id, f"测试用户 {user_data['name']}")
            self.test_users.append(user_id)
            print(f"创建用户: {user_data['name']} (ID: {user_id})")
        
        # 保存用户到数据库
        await user_manager.save_to_database()
        
        # 创建匹配
        # 匹配1: User1 和 User2
        match1 = await match_manager.create_match(
            10001, 10002, 
            "测试匹配原因1", "测试匹配原因2", 85
        )
        if match1:
            self.test_matches.append(match1.match_id)
            print(f"创建匹配1: User1-User2 (match_id: {match1.match_id})")
        
        # 匹配2: User1 和 User4  
        match2 = await match_manager.create_match(
            10001, 10004,
            "测试匹配原因3", "测试匹配原因4", 78
        )
        if match2:
            self.test_matches.append(match2.match_id)
            print(f"创建匹配2: User1-User4 (match_id: {match2.match_id})")
        
        # 匹配3: User3 和 User2
        match3 = await match_manager.create_match(
            10003, 10002,
            "测试匹配原因5", "测试匹配原因6", 92
        )
        if match3:
            self.test_matches.append(match3.match_id)
            print(f"创建匹配3: User3-User2 (match_id: {match3.match_id})")
        
        # 保存匹配到数据库
        await match_manager.save_to_database()
        
        # 为每个匹配创建聊天室
        for match_id in self.test_matches:
            match = match_manager.get_match(match_id)
            if match:
                chatroom_id = await chatroom_manager.get_or_create_chatroom(
                    match.user_id_1, match.user_id_2, match.match_id
                )
                if chatroom_id:
                    self.test_chatrooms.append(chatroom_id)
                    print(f"创建聊天室: {chatroom_id} (匹配: {match_id})")
        
        # 发送测试消息
        message_data = [
            (self.test_chatrooms[0], 10001, "你好，很高兴认识你！"),
            (self.test_chatrooms[0], 10002, "我也是，你好！"),
            (self.test_chatrooms[1], 10001, "Hi there!"),
            (self.test_chatrooms[1], 10004, "Hello!"),
            (self.test_chatrooms[2], 10003, "Nice to meet you"),
            (self.test_chatrooms[2], 10002, "Nice to meet you too!"),
        ]
        
        for chatroom_id, sender_id, content in message_data:
            result = await chatroom_manager.send_message(chatroom_id, sender_id, content)
            if result["success"]:
                print(f"发送消息: 聊天室{chatroom_id}, 发送者{sender_id}")
        
        # 保存聊天室数据
        await chatroom_manager.save_chatroom_history()
        
        print(f"测试数据设置完成:")
        print(f"- 用户: {len(self.test_users)} 个")
        print(f"- 匹配: {len(self.test_matches)} 个")
        print(f"- 聊天室: {len(self.test_chatrooms)} 个")

    async def verify_before_deletion(self):
        """删除前验证数据存在"""
        print("\n=== 删除前数据验证 ===")
        
        # 验证数据库中的数据
        users_count = len(await Database.find("users", {"_id": {"$in": self.test_users}}))
        matches_count = len(await Database.find("matches", {"_id": {"$in": self.test_matches}}))
        chatrooms_count = len(await Database.find("chatrooms", {"_id": {"$in": self.test_chatrooms}}))
        
        # 查询所有测试消息
        all_messages = await Database.find("messages", {})
        test_messages_count = sum(1 for msg in all_messages 
                                 if msg.get("chatroom_id") in self.test_chatrooms)
        
        print(f"数据库中的数据:")
        print(f"- 测试用户: {users_count}/{len(self.test_users)}")
        print(f"- 测试匹配: {matches_count}/{len(self.test_matches)}")
        print(f"- 测试聊天室: {chatrooms_count}/{len(self.test_chatrooms)}")
        print(f"- 测试消息: {test_messages_count}")
        
        # 验证内存中的数据
        user_manager = UserManagement()
        match_manager = MatchManager()
        chatroom_manager = ChatroomManager()
        
        memory_users = sum(1 for uid in self.test_users if uid in user_manager.user_list)
        memory_matches = sum(1 for mid in self.test_matches if mid in match_manager.match_list)
        memory_chatrooms = sum(1 for cid in self.test_chatrooms if cid in chatroom_manager.chatrooms)
        
        print(f"内存中的数据:")
        print(f"- 测试用户: {memory_users}/{len(self.test_users)}")
        print(f"- 测试匹配: {memory_matches}/{len(self.test_matches)}")
        print(f"- 测试聊天室: {memory_chatrooms}/{len(self.test_chatrooms)}")
        
        return {
            "db_users": users_count,
            "db_matches": matches_count,
            "db_chatrooms": chatrooms_count,
            "db_messages": test_messages_count,
            "memory_users": memory_users,
            "memory_matches": memory_matches,  
            "memory_chatrooms": memory_chatrooms
        }

    async def delete_user_and_verify(self, user_id):
        """删除用户并验证聊天室清理"""
        print(f"\n=== 删除用户 {user_id} ===")
        
        # 获取该用户的匹配和聊天室信息
        user_manager = UserManagement()
        user = user_manager.get_user_instance(user_id)
        if not user:
            print(f"用户 {user_id} 不存在")
            return False
        
        user_matches = user.match_ids.copy()
        print(f"用户 {user_id} 的匹配: {user_matches}")
        
        # 获取相关聊天室
        match_manager = MatchManager()
        related_chatrooms = []
        for match_id in user_matches:
            match = match_manager.get_match(match_id)
            if match and match.chatroom_id:
                related_chatrooms.append(match.chatroom_id)
        
        print(f"相关聊天室: {related_chatrooms}")
        
        # 执行删除
        success = await user_manager.deactivate_user(user_id)
        print(f"删除结果: {'成功' if success else '失败'}")
        
        if not success:
            return False
        
        # 验证删除结果
        print(f"\n=== 验证用户 {user_id} 删除结果 ===")
        
        # 1. 验证用户被删除（内存和数据库）
        user_in_memory = user_manager.get_user_instance(user_id)
        user_in_db = await Database.find_one("users", {"_id": user_id})
        
        print(f"用户在内存中: {'存在' if user_in_memory else '不存在'}")
        print(f"用户在数据库中: {'存在' if user_in_db else '不存在'}")
        
        # 2. 验证匹配被删除
        matches_in_memory = [mid for mid in user_matches if mid in match_manager.match_list]
        matches_in_db = await Database.find("matches", {"_id": {"$in": user_matches}})
        
        print(f"相关匹配在内存中: {len(matches_in_memory)}/{len(user_matches)}")
        print(f"相关匹配在数据库中: {len(matches_in_db)}/{len(user_matches)}")
        
        # 3. 验证聊天室被删除（重点测试）
        chatroom_manager = ChatroomManager()
        chatrooms_in_memory = [cid for cid in related_chatrooms if cid in chatroom_manager.chatrooms]
        chatrooms_in_db = await Database.find("chatrooms", {"_id": {"$in": related_chatrooms}})
        
        print(f"相关聊天室在内存中: {len(chatrooms_in_memory)}/{len(related_chatrooms)}")
        print(f"相关聊天室在数据库中: {len(chatrooms_in_db)}/{len(related_chatrooms)}")
        
        # 4. 验证消息被删除
        messages_in_db = await Database.find("messages", {"chatroom_id": {"$in": related_chatrooms}})
        print(f"相关消息在数据库中: {len(messages_in_db)}")
        
        # 验证结果
        deletion_success = (
            not user_in_memory and not user_in_db and
            len(matches_in_memory) == 0 and len(matches_in_db) == 0 and
            len(chatrooms_in_memory) == 0 and len(chatrooms_in_db) == 0 and
            len(messages_in_db) == 0
        )
        
        print(f"删除验证结果: {'✓ 成功' if deletion_success else '✗ 失败'}")
        
        if not deletion_success:
            print("失败详情:")
            if user_in_memory or user_in_db:
                print("- 用户未完全删除")
            if matches_in_memory or matches_in_db:
                print("- 匹配未完全删除")
            if chatrooms_in_memory or chatrooms_in_db:
                print("- 聊天室未完全删除 ⚠️")
            if messages_in_db:
                print("- 消息未完全删除")
        
        return deletion_success

    async def verify_other_users_unaffected(self):
        """验证其他用户的数据未受影响"""
        print(f"\n=== 验证其他用户数据完整性 ===")
        
        user_manager = UserManagement()
        
        # User1 已被删除，检查 User2, User3, User4
        remaining_users = [10002, 10003, 10004]
        
        for user_id in remaining_users:
            user = user_manager.get_user_instance(user_id)
            if user:
                print(f"用户 {user_id}: 存在，匹配数量: {len(user.match_ids)}")
                # 检查用户的匹配是否仍然有效
                match_manager = MatchManager()
                valid_matches = []
                for match_id in user.match_ids:
                    match = match_manager.get_match(match_id)
                    if match:
                        valid_matches.append(match_id)
                print(f"  有效匹配: {valid_matches}")
            else:
                print(f"用户 {user_id}: 不存在 ⚠️")

    async def cleanup_test_data(self):
        """清理测试数据"""
        print(f"\n=== 清理剩余测试数据 ===")
        
        # 删除剩余的测试用户
        user_manager = UserManagement()
        remaining_users = [uid for uid in self.test_users if uid in user_manager.user_list]
        
        for user_id in remaining_users:
            await user_manager.deactivate_user(user_id)
            print(f"清理用户: {user_id}")

    async def run_test(self):
        """运行完整测试"""
        try:
            print("开始用户删除聊天室清理测试")
            print("=" * 50)
            
            # 1. 设置测试数据
            await self.setup_test_data()
            
            # 2. 删除前验证
            before_data = await self.verify_before_deletion()
            
            # 3. 删除 User1 (ID: 10001) - 这个用户有2个匹配和2个聊天室
            deletion_success = await self.delete_user_and_verify(10001)
            
            # 4. 验证其他用户数据完整性
            await self.verify_other_users_unaffected()
            
            # 5. 删除后整体验证
            print(f"\n=== 整体数据验证 ===")
            after_data = await self.verify_before_deletion()
            
            # 6. 清理剩余测试数据
            await self.cleanup_test_data()
            
            print("\n" + "=" * 50)
            print(f"测试结果: {'✓ 聊天室清理功能正常' if deletion_success else '✗ 聊天室清理功能异常'}")
            
            return deletion_success
            
        except Exception as e:
            print(f"测试执行错误: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """主测试函数"""
    test = UserDeletionChatroomTest()
    success = await test.run_test()
    
    if success:
        print("\n🎉 测试通过: 用户删除时聊天室被正确清理")
    else:
        print("\n❌ 测试失败: 用户删除时聊天室清理存在问题")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)