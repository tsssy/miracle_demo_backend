#!/usr/bin/env python3
"""
重新创建完整的测试环境，显式保存所有数据
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Database
from app.services.https.UserManagement import UserManagement
from app.services.https.MatchManager import MatchManager
from app.services.https.ChatroomManager import ChatroomManager


async def clean_test_data():
    """清理现有的测试数据"""
    print("🧹 清理现有测试数据...")
    
    test_user_ids = [99001, 99002, 99003, 99004]
    
    # 删除测试用户
    result = await Database.delete_many("users", {"_id": {"$in": test_user_ids}})
    print(f"   删除用户: {result} 个")
    
    # 删除涉及测试用户的匹配
    result = await Database.delete_many("matches", {
        "$or": [
            {"user_id_1": {"$in": test_user_ids}},
            {"user_id_2": {"$in": test_user_ids}}
        ]
    })
    print(f"   删除匹配: {result} 个")
    
    # 删除涉及测试用户的聊天室
    result = await Database.delete_many("chatrooms", {
        "$or": [
            {"user1_id": {"$in": test_user_ids}},
            {"user2_id": {"$in": test_user_ids}}
        ]
    })
    print(f"   删除聊天室: {result} 个")
    
    # 删除涉及测试用户的消息
    result = await Database.delete_many("messages", {
        "$or": [
            {"message_sender_id": {"$in": test_user_ids}},
            {"message_receiver_id": {"$in": test_user_ids}}
        ]
    })
    print(f"   删除消息: {result} 条")


async def create_complete_test_environment():
    """创建完整的测试环境并显式保存所有数据"""
    print("🔧 创建完整测试环境")
    print("=" * 50)
    
    try:
        # 初始化数据库连接
        await Database.connect()
        print("✅ 数据库连接成功")
        
        # 清理现有测试数据
        await clean_test_data()
        
        # 重新初始化服务（清除内存中的缓存）
        print("\n📦 初始化服务...")
        user_manager = UserManagement()
        # 清除单例状态
        UserManagement._initialized = False
        user_manager.user_list.clear()
        user_manager.male_user_list.clear()
        user_manager.female_user_list.clear()
        
        await user_manager.initialize_from_database()
        print(f"   UserManagement: 重新加载 {len(user_manager.user_list)} 个用户")
        
        match_manager = MatchManager()
        match_manager.match_list.clear()
        await match_manager.construct()
        print(f"   MatchManager: 重新加载 {len(match_manager.match_list)} 个匹配")
        
        chatroom_manager = ChatroomManager()
        chatroom_manager.chatrooms.clear()
        await chatroom_manager.construct()
        print(f"   ChatroomManager: 重新加载 {len(chatroom_manager.chatrooms)} 个聊天室")
        
        # 步骤1: 创建测试用户
        print("\n👥 步骤1: 创建测试用户...")
        test_users = []
        test_user_data = [
            {"name": "TestDeleteUser", "id": 99001, "gender": 1, "age": 25},  # 将被删除的用户
            {"name": "TestUser2", "id": 99002, "gender": 2, "age": 23},      # 女性用户
            {"name": "TestUser3", "id": 99003, "gender": 1, "age": 27},      # 男性用户
            {"name": "TestUser4", "id": 99004, "gender": 2, "age": 24},      # 女性用户
        ]
        
        for user_data in test_user_data:
            user_id = user_manager.create_new_user(
                user_data["name"], 
                user_data["id"], 
                user_data["gender"]
            )
            user_manager.edit_user_age(user_id, user_data["age"])
            user_manager.edit_target_gender(user_id, 3 - user_data["gender"])  # 设置为异性
            user_manager.edit_summary(user_id, f"这是测试用户 {user_data['name']}")
            test_users.append(user_id)
            print(f"   ✅ 创建用户: {user_data['name']} (ID: {user_id}, 性别: {'男' if user_data['gender'] == 1 else '女'})")
        
        # 显式保存用户到数据库
        print("   💾 保存用户到数据库...")
        save_success = await user_manager.save_to_database()
        print(f"   {'✅' if save_success else '❌'} 用户保存结果: {save_success}")
        
        # 步骤2: 创建匹配
        print("\n💝 步骤2: 创建测试匹配...")
        test_matches = []
        match_configs = [
            (99001, 99002, "你们都喜欢音乐", "你们都很幽默", 85),  # DeleteUser - User2
            (99001, 99004, "你们都喜欢旅行", "你们都很积极", 78),  # DeleteUser - User4  
            (99003, 99002, "你们都喜欢读书", "你们都很聪明", 92),  # User3 - User2
        ]
        
        for user1_id, user2_id, reason1, reason2, score in match_configs:
            try:
                match = await match_manager.create_match(user1_id, user2_id, reason1, reason2, score)
                if match:
                    test_matches.append(match.match_id)
                    print(f"   ✅ 创建匹配: User{user1_id} - User{user2_id} (ID: {match.match_id}, 分数: {score})")
                    
                    # 显式保存匹配到数据库
                    match_save_success = await match.save_to_database()
                    print(f"   💾 匹配 {match.match_id} 保存: {'✅' if match_save_success else '❌'}")
                    
            except Exception as e:
                print(f"   ❌ 创建匹配失败 User{user1_id} - User{user2_id}: {e}")
        
        # 显式保存所有用户数据（包含更新的match_ids）
        print("   💾 更新用户match_ids到数据库...")
        user_save_success = await user_manager.save_to_database()
        print(f"   {'✅' if user_save_success else '❌'} 用户match_ids保存结果: {user_save_success}")
        
        # 验证match_ids是否正确保存
        print("   🔍 验证用户match_ids:")
        for user_id in test_users:
            user = user_manager.get_user_instance(user_id)
            if user:
                print(f"     用户 {user_id}: match_ids = {user.match_ids}")
        
        # 步骤3: 创建聊天室
        print("\n💬 步骤3: 创建测试聊天室...")
        test_chatrooms = []
        for match_id in test_matches:
            match = match_manager.get_match(match_id)
            if match:
                try:
                    chatroom_id = await chatroom_manager.get_or_create_chatroom(
                        match.user_id_1, match.user_id_2, match.match_id
                    )
                    if chatroom_id:
                        test_chatrooms.append(chatroom_id)
                        print(f"   ✅ 创建聊天室: ID {chatroom_id} (匹配: {match_id}, 用户: {match.user_id_1}↔{match.user_id_2})")
                        
                        # 显式保存聊天室
                        chatroom = chatroom_manager.chatrooms.get(chatroom_id)
                        if chatroom:
                            chatroom_save_success = await chatroom.save_to_database()
                            print(f"   💾 聊天室 {chatroom_id} 保存: {'✅' if chatroom_save_success else '❌'}")
                            
                except Exception as e:
                    print(f"   ❌ 创建聊天室失败 (匹配: {match_id}): {e}")
        
        # 显式保存匹配数据（包含chatroom_id）
        print("   💾 更新匹配chatroom_id到数据库...")
        match_save_success = await match_manager.save_to_database()
        print(f"   {'✅' if match_save_success else '❌'} 匹配chatroom_id保存结果: {match_save_success}")
        
        # 步骤4: 发送测试消息
        print("\n📝 步骤4: 发送测试消息...")
        message_configs = [
            # 聊天室1的消息 (99001 ↔ 99002)
            (test_chatrooms[0] if len(test_chatrooms) > 0 else None, 99001, "嗨！很高兴认识你 😊"),
            (test_chatrooms[0] if len(test_chatrooms) > 0 else None, 99002, "我也是！你好 👋"),
            (test_chatrooms[0] if len(test_chatrooms) > 0 else None, 99001, "你平时喜欢做什么？"),
            
            # 聊天室2的消息 (99001 ↔ 99004)
            (test_chatrooms[1] if len(test_chatrooms) > 1 else None, 99001, "Hello! 🌟"),
            (test_chatrooms[1] if len(test_chatrooms) > 1 else None, 99004, "Hi there! Nice to meet you!"),
            
            # 聊天室3的消息 (99003 ↔ 99002)
            (test_chatrooms[2] if len(test_chatrooms) > 2 else None, 99003, "你好，很高兴遇见你"),
            (test_chatrooms[2] if len(test_chatrooms) > 2 else None, 99002, "你好！我也很高兴认识你"),
        ]
        
        message_count = 0
        for chatroom_id, sender_id, content in message_configs:
            if chatroom_id:
                try:
                    result = await chatroom_manager.send_message(chatroom_id, sender_id, content)
                    if result["success"]:
                        message_count += 1
                        print(f"   ✅ 消息 #{message_count}: 聊天室{chatroom_id}, 发送者{sender_id}")
                        print(f"      内容: \"{content}\"")
                    else:
                        print(f"   ❌ 发送消息失败: 聊天室{chatroom_id}, 发送者{sender_id}")
                except Exception as e:
                    print(f"   ❌ 发送消息异常: {e}")
        
        # 显式保存所有聊天室数据
        print("   💾 保存聊天室和消息数据...")
        chatroom_save_success = await chatroom_manager.save_chatroom_history()
        print(f"   {'✅' if chatroom_save_success else '❌'} 聊天室数据保存结果: {chatroom_save_success}")
        
        # 最终验证
        print("\n📊 测试环境创建完成!")
        print(f"   👥 创建用户: {len(test_users)} 个")
        print(f"   💝 创建匹配: {len(test_matches)} 个")
        print(f"   💬 创建聊天室: {len(test_chatrooms)} 个")
        print(f"   📝 发送消息: {message_count} 条")
        
        # 最终数据验证
        await verify_final_data(test_users, test_matches, test_chatrooms)
        
        return {
            "users": test_users,
            "matches": test_matches,
            "chatrooms": test_chatrooms,
            "messages": message_count
        }
        
    except Exception as e:
        print(f"❌ 创建测试环境失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def verify_final_data(test_users, test_matches, test_chatrooms):
    """验证最终数据完整性"""
    print("\n🔍 最终数据验证:")
    
    # 验证用户
    users_in_db = await Database.find("users", {"_id": {"$in": test_users}})
    print(f"   数据库中的测试用户: {len(users_in_db)}/{len(test_users)}")
    for user in users_in_db:
        print(f"     - 用户 {user['_id']} ({user['telegram_user_name']}): match_ids = {user.get('match_ids', [])}")
    
    # 验证匹配
    matches_in_db = await Database.find("matches", {"_id": {"$in": test_matches}})
    print(f"   数据库中的测试匹配: {len(matches_in_db)}/{len(test_matches)}")
    for match in matches_in_db:
        print(f"     - 匹配 {match['_id']}: {match['user_id_1']}↔{match['user_id_2']}, 聊天室: {match.get('chatroom_id', 'None')}")
    
    # 验证聊天室
    chatrooms_in_db = await Database.find("chatrooms", {"_id": {"$in": test_chatrooms}})
    print(f"   数据库中的测试聊天室: {len(chatrooms_in_db)}/{len(test_chatrooms)}")
    for chatroom in chatrooms_in_db:
        print(f"     - 聊天室 {chatroom['_id']}: {chatroom['user1_id']}↔{chatroom['user2_id']}, 消息数: {len(chatroom.get('message_ids', []))}")
    
    # 验证消息
    messages_in_db = await Database.find("messages", {
        "$or": [
            {"message_sender_id": {"$in": test_users}},
            {"message_receiver_id": {"$in": test_users}}
        ]
    })
    print(f"   数据库中的测试消息: {len(messages_in_db)} 条")
    
    print(f"\n⚠️  待删除用户: 99001 (TestDeleteUser)")
    target_user_matches = [m for m in matches_in_db if m['user_id_1'] == 99001 or m['user_id_2'] == 99001]
    target_user_chatrooms = [c for c in chatrooms_in_db if c['user1_id'] == 99001 or c['user2_id'] == 99001]
    print(f"   该用户的匹配: {[m['_id'] for m in target_user_matches]}")
    print(f"   该用户的聊天室: {[c['_id'] for c in target_user_chatrooms]}")


async def main():
    """主函数"""
    result = await create_complete_test_environment()
    
    if result:
        print("\n✅ 测试环境创建完成！")
        print("💡 现在你可以在后台查看完整的测试数据")
        print("🔄 下一步: 运行用户删除测试")
    else:
        print("❌ 测试环境创建失败")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)