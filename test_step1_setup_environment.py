#!/usr/bin/env python3
"""
步骤1：设置测试环境
创建测试用户、匹配、聊天室和消息，让用户可以在后台查看数据
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


async def setup_test_environment():
    """设置测试环境：创建用户、匹配、聊天室、消息"""
    print("🔧 步骤1：设置测试环境")
    print("=" * 50)
    
    try:
        # 初始化数据库连接
        await Database.connect()
        print("✅ 数据库连接成功")
        
        # 初始化服务
        print("\n📦 初始化服务...")
        user_manager = UserManagement()
        await user_manager.initialize_from_database()
        print(f"   UserManagement: 已加载 {len(user_manager.user_list)} 个用户")
        
        match_manager = MatchManager()
        await match_manager.construct()
        print(f"   MatchManager: 已加载 {len(match_manager.match_list)} 个匹配")
        
        chatroom_manager = ChatroomManager()
        await chatroom_manager.construct()
        print(f"   ChatroomManager: 已加载 {len(chatroom_manager.chatrooms)} 个聊天室")
        
        # 创建测试用户
        print("\n👥 创建测试用户...")
        test_users = []
        test_user_data = [
            {"name": "TestDeleteUser", "id": 99001, "gender": 1, "age": 25},  # 将被删除的用户
            {"name": "TestUser2", "id": 99002, "gender": 2, "age": 23},      # 女性用户
            {"name": "TestUser3", "id": 99003, "gender": 1, "age": 27},      # 男性用户
            {"name": "TestUser4", "id": 99004, "gender": 2, "age": 24},      # 女性用户
        ]
        
        for user_data in test_user_data:
            # 检查用户是否已存在
            existing_user = user_manager.user_list.get(user_data["id"])
            if existing_user:
                print(f"   ⚠️  用户 {user_data['name']} (ID: {user_data['id']}) 已存在，跳过创建")
                test_users.append(user_data["id"])
                continue
                
            # 创建新用户
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
        
        # 保存用户到数据库
        await user_manager.save_to_database()
        print("   💾 用户数据已保存到数据库")
        
        # 创建匹配
        print("\n💝 创建测试匹配...")
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
            except Exception as e:
                print(f"   ❌ 创建匹配失败 User{user1_id} - User{user2_id}: {e}")
        
        # 保存匹配到数据库
        await match_manager.save_to_database()
        print("   💾 匹配数据已保存到数据库")
        
        # 创建聊天室
        print("\n💬 创建测试聊天室...")
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
                except Exception as e:
                    print(f"   ❌ 创建聊天室失败 (匹配: {match_id}): {e}")
        
        # 发送测试消息
        print("\n📝 发送测试消息...")
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
        
        # 保存聊天室数据
        await chatroom_manager.save_chatroom_history()
        print("   💾 聊天室和消息数据已保存到数据库")
        
        # 显示最终统计
        print("\n📊 测试环境设置完成!")
        print(f"   👥 创建用户: {len(test_users)} 个")
        print(f"   💝 创建匹配: {len(test_matches)} 个")
        print(f"   💬 创建聊天室: {len(test_chatrooms)} 个")
        print(f"   📝 发送消息: {message_count} 条")
        
        # 显示详细信息供后台查看
        print("\n🔍 详细信息（供后台查看）:")
        print(f"   测试用户IDs: {test_users}")
        print(f"   测试匹配IDs: {test_matches}")
        print(f"   测试聊天室IDs: {test_chatrooms}")
        
        # 特别标记将要删除的用户
        print(f"\n⚠️  待删除用户: 99001 (TestDeleteUser)")
        print(f"   该用户的匹配: {[mid for mid in test_matches[:2]]}")  # 前两个匹配属于99001
        print(f"   该用户的聊天室: {[cid for cid in test_chatrooms[:2]]}")  # 前两个聊天室属于99001
        
        return {
            "users": test_users,
            "matches": test_matches,
            "chatrooms": test_chatrooms,
            "messages": message_count
        }
        
    except Exception as e:
        print(f"❌ 设置测试环境失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def verify_database_data():
    """验证数据库中的数据"""
    print("\n🔍 验证数据库数据:")
    
    # 查询测试用户
    test_user_ids = [99001, 99002, 99003, 99004]
    users_in_db = await Database.find("users", {"_id": {"$in": test_user_ids}})
    print(f"   数据库中的测试用户: {len(users_in_db)} 个")
    for user in users_in_db:
        print(f"     - ID: {user['_id']}, 姓名: {user['telegram_user_name']}, 匹配数: {len(user.get('match_ids', []))}")
    
    # 查询匹配
    matches_in_db = await Database.find("matches", {
        "$or": [
            {"user_id_1": {"$in": test_user_ids}},
            {"user_id_2": {"$in": test_user_ids}}
        ]
    })
    print(f"   数据库中的测试匹配: {len(matches_in_db)} 个")
    for match in matches_in_db:
        print(f"     - ID: {match['_id']}, 用户: {match['user_id_1']}↔{match['user_id_2']}, 聊天室: {match.get('chatroom_id', 'None')}")
    
    # 查询聊天室
    chatrooms_in_db = await Database.find("chatrooms", {
        "$or": [
            {"user1_id": {"$in": test_user_ids}},
            {"user2_id": {"$in": test_user_ids}}
        ]
    })
    print(f"   数据库中的测试聊天室: {len(chatrooms_in_db)} 个")
    for chatroom in chatrooms_in_db:
        print(f"     - ID: {chatroom['_id']}, 用户: {chatroom['user1_id']}↔{chatroom['user2_id']}, 消息数: {len(chatroom.get('message_ids', []))}")
    
    # 查询消息
    messages_in_db = await Database.find("messages", {
        "$or": [
            {"message_sender_id": {"$in": test_user_ids}},
            {"message_receiver_id": {"$in": test_user_ids}}
        ]
    })
    print(f"   数据库中的测试消息: {len(messages_in_db)} 条")
    for i, message in enumerate(messages_in_db, 1):
        print(f"     - 消息{i}: ID {message['_id']}, {message['message_sender_id']}→{message['message_receiver_id']}, 聊天室: {message.get('chatroom_id', 'None')}")
        print(f"       内容: \"{message['message_content'][:50]}{'...' if len(message['message_content']) > 50 else ''}\"")


async def main():
    """主函数"""
    result = await setup_test_environment()
    
    if result:
        await verify_database_data()
        print("\n✅ 步骤1完成：测试环境已设置完毕")
        print("💡 现在你可以在后台（数据库管理工具或MongoDB Compass）中查看以下数据:")
        print("   - users 集合: 查看测试用户 99001, 99002, 99003, 99004")
        print("   - matches 集合: 查看涉及这些用户的匹配记录")
        print("   - chatrooms 集合: 查看相关聊天室")
        print("   - messages 集合: 查看测试消息")
        print("\n🔄 下一步: 运行 python test_step2_delete_user.py 来测试用户删除")
    else:
        print("❌ 步骤1失败：无法设置测试环境")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)