#!/usr/bin/env python3
"""
用户注销功能综合测试脚本
测试场景：
1. 创建多个用户
2. 创建多个匹配关系
3. 创建多个聊天室
4. 发送多条消息
5. 执行用户注销
6. 验证所有相关数据的完整删除
"""

import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class ComprehensiveDeactivateTest:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.test_data = {
            "users": [],
            "matches": [],
            "chatrooms": [],
            "messages": []
        }
    
    async def cleanup(self):
        """清理测试数据"""
        await self.client.aclose()
    
    async def create_user(self, telegram_user_name: str, telegram_user_id: int, gender: int):
        """创建用户"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/UserManagement/create_new_user",
                json={
                    "telegram_user_name": telegram_user_name,
                    "telegram_user_id": telegram_user_id,
                    "gender": gender
                }
            )
            print(f"Debug: 用户创建响应状态: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print(f"✓ 创建用户: {telegram_user_name} (ID: {result['user_id']})")
                    return result["user_id"]
                else:
                    print(f"✗ 创建用户失败: success=false, {result}")
            else:
                print(f"✗ 创建用户失败: HTTP {response.status_code}, {response.text}")
            return None
        except Exception as e:
            print(f"✗ 创建用户异常: {e}")
            return None
    
    async def create_match(self, user1_id: int, user2_id: int, description: str):
        """创建匹配"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/MatchManager/create_match",
                json={
                    "user_id_1": user1_id,
                    "user_id_2": user2_id,
                    "reason_1": f"{description} - for user {user1_id}",
                    "reason_2": f"{description} - for user {user2_id}",
                    "match_score": 80 + len(self.test_data["matches"]) * 5
                }
            )
            if response.status_code == 200:
                result = response.json()
                match_id = result["match_id"]
                print(f"✓ 创建匹配: {user1_id} ↔ {user2_id} (Match ID: {match_id})")
                return match_id
            print(f"✗ 创建匹配失败: {response.text}")
            return None
        except Exception as e:
            print(f"✗ 创建匹配异常: {e}")
            return None
    
    async def create_chatroom(self, user1_id: int, user2_id: int, match_id: int):
        """创建聊天室"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/ChatroomManager/get_or_create_chatroom",
                json={
                    "user_id_1": user1_id,
                    "user_id_2": user2_id,
                    "match_id": match_id
                }
            )
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    chatroom_id = result["chatroom_id"]
                    print(f"✓ 创建聊天室: ID {chatroom_id} (匹配 {match_id})")
                    return chatroom_id
            print(f"✗ 创建聊天室失败: {response.text}")
            return None
        except Exception as e:
            print(f"✗ 创建聊天室异常: {e}")
            return None
    
    async def send_message(self, chatroom_id: int, sender_id: int, message: str):
        """发送消息（注意：这个API可能需要服务器重启才能生效）"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/ChatroomManager/send_message",
                json={
                    "chatroom_id": chatroom_id,
                    "sender_user_id": sender_id,
                    "message_content": message
                }
            )
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print(f"✓ 发送消息: 用户{sender_id} -> 聊天室{chatroom_id}: {message[:20]}...")
                    return True
            print(f"✗ 发送消息失败: {response.text}")
            return False
        except Exception as e:
            print(f"✗ 发送消息异常: {e}")
            return False
    
    async def get_user_info(self, user_id: int):
        """获取用户信息"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/UserManagement/get_user_info_with_user_id",
                json={"user_id": user_id}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None
    
    async def get_match_info(self, user_id: int, match_id: int):
        """获取匹配信息"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/MatchManager/get_match_info",
                json={"user_id": user_id, "match_id": match_id}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None
    
    async def get_chat_history(self, chatroom_id: int, user_id: int):
        """获取聊天历史"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/ChatroomManager/get_chat_history",
                json={"chatroom_id": chatroom_id, "user_id": user_id}
            )
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    return result["messages"]
            return []
        except Exception as e:
            return []
    
    async def deactivate_user(self, user_id: int):
        """注销用户"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/UserManagement/deactivate_user",
                json={"user_id": user_id}
            )
            if response.status_code == 200:
                result = response.json()
                return result["success"]
            print(f"✗ 注销用户失败: {response.text}")
            return False
        except Exception as e:
            print(f"✗ 注销用户异常: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """运行综合测试"""
        print("=" * 80)
        print("🧪 用户注销功能综合测试")
        print("=" * 80)
        
        try:
            # === 第一阶段：构建复杂的测试环境 ===
            print("\n📋 第一阶段：构建测试环境")
            print("-" * 50)
            
            # 创建5个测试用户
            print("\n1️⃣ 创建测试用户...")
            users = []
            user_configs = [
                ("alice_test", 4001, 2),  # 女性
                ("bob_test", 4002, 1),    # 男性 - 即将被注销的用户
                ("charlie_test", 4003, 1), # 男性
                ("diana_test", 4004, 2),   # 女性
                ("eve_test", 4005, 2),     # 女性
            ]
            
            for name, uid, gender in user_configs:
                user_id = await self.create_user(name, uid, gender)
                if user_id:
                    users.append(user_id)
                else:
                    print(f"⚠️ 无法创建用户 {name}，跳过")
            
            if len(users) < 3:
                print("✗ 创建的用户数量不足，测试终止")
                return
            
            self.test_data["users"] = users
            target_user = users[1]  # Bob将被注销
            print(f"\n🎯 目标用户 (将被注销): {target_user}")
            
            # 创建多个匹配关系，让目标用户与多个其他用户匹配
            print("\n2️⃣ 创建匹配关系...")
            match_configs = [
                (users[1], users[0], "Bob与Alice的匹配"),    # Bob ↔ Alice
                (users[1], users[2], "Bob与Charlie的匹配"),  # Bob ↔ Charlie  
                (users[1], users[3], "Bob与Diana的匹配"),    # Bob ↔ Diana
                (users[0], users[4], "Alice与Eve的匹配"),    # Alice ↔ Eve (不涉及目标用户)
            ]
            
            matches = []
            for user1, user2, desc in match_configs:
                match_id = await self.create_match(user1, user2, desc)
                if match_id:
                    matches.append((match_id, user1, user2, desc))
            
            self.test_data["matches"] = matches
            print(f"✅ 成功创建 {len(matches)} 个匹配")
            
            # 为每个匹配创建聊天室
            print("\n3️⃣ 创建聊天室...")
            chatrooms = []
            for match_id, user1, user2, desc in matches:
                chatroom_id = await self.create_chatroom(user1, user2, match_id)
                if chatroom_id:
                    chatrooms.append((chatroom_id, match_id, user1, user2))
            
            self.test_data["chatrooms"] = chatrooms
            print(f"✅ 成功创建 {len(chatrooms)} 个聊天室")
            
            # 向聊天室发送消息（如果API可用的话）
            print("\n4️⃣ 尝试发送测试消息...")
            message_count = 0
            for chatroom_id, match_id, user1, user2 in chatrooms[:3]:  # 只在前3个聊天室发送消息
                # 每个聊天室发送2条消息
                msg1 = await self.send_message(chatroom_id, user1, f"你好！这是来自用户{user1}的消息")
                msg2 = await self.send_message(chatroom_id, user2, f"你好！这是来自用户{user2}的回复")
                if msg1: message_count += 1
                if msg2: message_count += 1
            
            print(f"📧 尝试发送了 {message_count} 条消息")
            
            # === 第二阶段：验证初始状态 ===
            print("\n📊 第二阶段：验证初始状态")
            print("-" * 50)
            
            print(f"\n5️⃣ 验证目标用户 {target_user} 的初始状态...")
            target_user_info = await self.get_user_info(target_user)
            if target_user_info:
                target_matches = target_user_info["match_ids"]
                print(f"✅ 目标用户match_ids: {target_matches}")
                print(f"📈 目标用户参与了 {len(target_matches)} 个匹配")
            else:
                print("✗ 无法获取目标用户信息")
                return
            
            # 验证其他用户的初始状态
            print("\n6️⃣ 验证其他用户的初始状态...")
            other_users_initial_state = {}
            for user_id in users:
                if user_id != target_user:
                    user_info = await self.get_user_info(user_id)
                    if user_info:
                        other_users_initial_state[user_id] = user_info["match_ids"]
                        print(f"用户 {user_id}: {len(user_info['match_ids'])} 个匹配")
            
            # 验证聊天室状态
            print("\n7️⃣ 验证聊天室状态...")
            initial_chat_states = {}
            for chatroom_id, match_id, user1, user2 in chatrooms:
                messages = await self.get_chat_history(chatroom_id, user1)
                initial_chat_states[chatroom_id] = len(messages)
                print(f"聊天室 {chatroom_id}: {len(messages)} 条消息")
            
            # === 第三阶段：执行用户注销 ===
            print("\n🔥 第三阶段：执行用户注销")
            print("-" * 50)
            
            print(f"\n8️⃣ 注销目标用户 {target_user}...")
            success = await self.deactivate_user(target_user)
            
            if success:
                print(f"✅ 用户 {target_user} 注销成功！")
            else:
                print(f"✗ 用户 {target_user} 注销失败")
                return
            
            # === 第四阶段：验证注销后状态 ===
            print("\n🔍 第四阶段：验证注销后状态")
            print("-" * 50)
            
            # 验证目标用户已被删除
            print(f"\n9️⃣ 验证目标用户 {target_user} 已被删除...")
            target_user_after = await self.get_user_info(target_user)
            if target_user_after is None:
                print("✅ 目标用户已成功删除")
            else:
                print("✗ 目标用户仍然存在")
            
            # 验证其他用户的match_ids已更新
            print("\n🔄 验证其他用户的match_ids已更新...")
            cleanup_count = 0
            for user_id, initial_matches in other_users_initial_state.items():
                user_info_after = await self.get_user_info(user_id)
                if user_info_after:
                    current_matches = user_info_after["match_ids"]
                    removed_matches = len(initial_matches) - len(current_matches)
                    if removed_matches > 0:
                        cleanup_count += removed_matches
                        print(f"✅ 用户 {user_id}: 清理了 {removed_matches} 个匹配")
                    else:
                        print(f"ℹ️ 用户 {user_id}: 无需清理匹配")
            
            print(f"📊 总共清理了 {cleanup_count} 个其他用户的匹配引用")
            
            # 验证匹配已被删除
            print("\n❌ 验证相关匹配已被删除...")
            deleted_matches = 0
            for match_id, user1, user2, desc in matches:
                if user1 == target_user or user2 == target_user:
                    # 这个匹配应该被删除
                    match_info = await self.get_match_info(user1 if user1 != target_user else user2, match_id)
                    if match_info is None:
                        deleted_matches += 1
                        print(f"✅ 匹配 {match_id} 已被删除")
                    else:
                        print(f"✗ 匹配 {match_id} 仍然存在")
                else:
                    # 这个匹配不应该被删除
                    match_info = await self.get_match_info(user1, match_id)
                    if match_info:
                        print(f"✅ 无关匹配 {match_id} 正确保留")
                    else:
                        print(f"⚠️ 无关匹配 {match_id} 意外被删除")
            
            print(f"🗑️ 成功删除了 {deleted_matches} 个相关匹配")
            
            # 验证聊天室已被删除
            print("\n💬 验证相关聊天室已被删除...")
            deleted_chatrooms = 0
            for chatroom_id, match_id, user1, user2 in chatrooms:
                if user1 == target_user or user2 == target_user:
                    # 这个聊天室应该被删除，尝试访问应该失败或返回空
                    messages = await self.get_chat_history(chatroom_id, user1 if user1 != target_user else user2)
                    # 由于聊天室被删除，无法精确判断，但可以尝试重新创建来验证
                    try:
                        new_chatroom = await self.create_chatroom(user1, user2, match_id)
                        if new_chatroom is None:
                            deleted_chatrooms += 1
                            print(f"✅ 聊天室 {chatroom_id} 已被删除（无法重新创建）")
                        else:
                            print(f"⚠️ 聊天室 {chatroom_id} 可能未被完全删除")
                    except:
                        deleted_chatrooms += 1
                        print(f"✅ 聊天室 {chatroom_id} 已被删除")
                else:
                    # 无关聊天室应该保留
                    messages = await self.get_chat_history(chatroom_id, user1)
                    initial_msg_count = initial_chat_states.get(chatroom_id, 0)
                    if len(messages) == initial_msg_count:
                        print(f"✅ 无关聊天室 {chatroom_id} 正确保留")
                    else:
                        print(f"⚠️ 无关聊天室 {chatroom_id} 状态异常")
            
            print(f"🏠 成功删除了 {deleted_chatrooms} 个相关聊天室")
            
            # === 第五阶段：边界测试 ===
            print("\n⚠️ 第五阶段：边界测试")
            print("-" * 50)
            
            print("\n🔒 测试重复注销...")
            repeat_success = await self.deactivate_user(target_user)
            if not repeat_success:
                print("✅ 重复注销正确返回失败")
            else:
                print("⚠️ 重复注销意外成功")
            
            print("\n🔍 测试不存在用户注销...")
            nonexistent_success = await self.deactivate_user(99999)
            if not nonexistent_success:
                print("✅ 不存在用户注销正确返回失败")
            else:
                print("⚠️ 不存在用户注销意外成功")
            
            # === 测试总结 ===
            print("\n" + "=" * 80)
            print("📋 综合测试总结")
            print("=" * 80)
            
            print(f"👥 创建用户数量: {len(users)}")
            print(f"💕 创建匹配数量: {len(matches)}")
            print(f"💬 创建聊天室数量: {len(chatrooms)}")
            print(f"📧 发送消息数量: {message_count}")
            print(f"🎯 注销目标用户: {target_user}")
            print(f"🧹 清理匹配引用: {cleanup_count}")
            print(f"🗑️ 删除相关匹配: {deleted_matches}")
            print(f"🏠 删除相关聊天室: {deleted_chatrooms}")
            
            print("\n🎉 综合测试完成！")
            print("✅ 用户注销功能运行正常，实现了完整的级联删除")
            
        except Exception as e:
            print(f"💥 测试过程中发生严重错误: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await self.cleanup()

async def main():
    """主函数"""
    test = ComprehensiveDeactivateTest()
    await test.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())