#!/usr/bin/env python3
"""
用户注销功能测试脚本
测试用户注销的完整流程：
1. 创建测试用户
2. 创建匹配关系 
3. 验证初始状态
4. 执行用户注销
5. 验证注销后的状态
"""

import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class TestDeactivateUser:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.test_users = []
        self.test_matches = []
    
    async def cleanup(self):
        """清理测试数据"""
        await self.client.aclose()
    
    async def create_test_user(self, telegram_user_name: str, telegram_user_id: int, gender: int):
        """创建测试用户"""
        try:
            response = await self.client.post(
                f"{BASE_URL}/UserManagement/create_new_user",
                json={
                    "telegram_user_name": telegram_user_name,
                    "telegram_user_id": telegram_user_id,
                    "gender": gender
                }
            )
            print(f"创建用户响应状态: {response.status_code}")
            print(f"创建用户响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print(f"✓ 创建用户成功: {telegram_user_name} (ID: {result['user_id']})")
                    return result["user_id"]
            print(f"✗ 创建用户失败: {response.text}")
            return None
        except Exception as e:
            print(f"✗ 创建用户异常: {e}")
            return None
    
    async def create_test_match(self, user1_id: int, user2_id: int):
        """创建测试匹配"""
        response = await self.client.post(
            f"{BASE_URL}/MatchManager/create_match",
            json={
                "user_id_1": user1_id,
                "user_id_2": user2_id,
                "reason_1": f"测试匹配原因给用户{user1_id}",
                "reason_2": f"测试匹配原因给用户{user2_id}",
                "match_score": 85
            }
        )
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print(f"✓ 创建匹配成功: 用户{user1_id} 和 用户{user2_id} (Match ID: {result['match_id']})")
                return result["match_id"]
        print(f"✗ 创建匹配失败: {response.text}")
        return None
    
    async def get_user_info(self, user_id: int):
        """获取用户信息"""
        response = await self.client.post(
            f"{BASE_URL}/UserManagement/get_user_info_with_user_id",
            json={"user_id": user_id}
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    async def get_match_info(self, user_id: int, match_id: int):
        """获取匹配信息"""
        response = await self.client.post(
            f"{BASE_URL}/MatchManager/get_match_info",
            json={
                "user_id": user_id,
                "match_id": match_id
            }
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    async def deactivate_user(self, user_id: int):
        """注销用户"""
        response = await self.client.post(
            f"{BASE_URL}/UserManagement/deactivate_user",
            json={"user_id": user_id}
        )
        if response.status_code == 200:
            result = response.json()
            return result["success"]
        print(f"✗ 注销用户失败: {response.text}")
        return False
    
    async def save_all_data(self):
        """保存所有数据到数据库"""
        # 保存用户数据
        user_response = await self.client.post(
            f"{BASE_URL}/UserManagement/save_to_database",
            json={}
        )
        
        # 保存匹配数据
        match_response = await self.client.post(
            f"{BASE_URL}/MatchManager/save_to_database",
            json={}
        )
        
        return user_response.status_code == 200 and match_response.status_code == 200
    
    async def run_test(self):
        """运行完整的测试"""
        print("=" * 60)
        print("开始用户注销功能测试")
        print("=" * 60)
        
        try:
            # Step 1: 创建测试用户
            print("\n1. 创建测试用户...")
            user1_id = await self.create_test_user("test_user_1", 9001, 1)  # 男性
            user2_id = await self.create_test_user("test_user_2", 9002, 2)  # 女性
            user3_id = await self.create_test_user("test_user_3", 9003, 1)  # 男性
            
            if not all([user1_id, user2_id, user3_id]):
                print("✗ 创建测试用户失败，测试终止")
                return
            
            self.test_users = [user1_id, user2_id, user3_id]
            
            # Step 2: 创建匹配关系
            print("\n2. 创建匹配关系...")
            match1_id = await self.create_test_match(user1_id, user2_id)  # user1 和 user2
            match2_id = await self.create_test_match(user1_id, user3_id)  # user1 和 user3
            
            if not all([match1_id, match2_id]):
                print("✗ 创建匹配关系失败，测试终止")
                return
            
            self.test_matches = [match1_id, match2_id]
            
            # Step 3: 保存数据到数据库
            print("\n3. 保存数据到数据库...")
            if await self.save_all_data():
                print("✓ 数据保存成功")
            else:
                print("✗ 数据保存失败")
                return
            
            # Step 4: 验证初始状态
            print("\n4. 验证初始状态...")
            user1_info = await self.get_user_info(user1_id)
            user2_info = await self.get_user_info(user2_id)
            user3_info = await self.get_user_info(user3_id)
            
            print(f"用户1 (ID: {user1_id}) match_ids: {user1_info['match_ids']}")
            print(f"用户2 (ID: {user2_id}) match_ids: {user2_info['match_ids']}")
            print(f"用户3 (ID: {user3_id}) match_ids: {user3_info['match_ids']}")
            
            # Step 5: 执行用户注销 (注销user1)
            print(f"\n5. 注销用户1 (ID: {user1_id})...")
            success = await self.deactivate_user(user1_id)
            
            if success:
                print(f"✓ 用户{user1_id}注销成功")
            else:
                print(f"✗ 用户{user1_id}注销失败")
                return
            
            # Step 6: 验证注销后的状态
            print("\n6. 验证注销后的状态...")
            
            # 验证user1已被删除
            user1_info_after = await self.get_user_info(user1_id)
            if user1_info_after is None:
                print(f"✓ 用户{user1_id}已成功删除")
            else:
                print(f"✗ 用户{user1_id}仍然存在")
            
            # 验证user2和user3的match_ids已更新
            user2_info_after = await self.get_user_info(user2_id)
            user3_info_after = await self.get_user_info(user3_id)
            
            print(f"注销后 - 用户2 (ID: {user2_id}) match_ids: {user2_info_after['match_ids']}")
            print(f"注销后 - 用户3 (ID: {user3_id}) match_ids: {user3_info_after['match_ids']}")
            
            # 验证匹配是否已删除
            for match_id in self.test_matches:
                match_info = await self.get_match_info(user2_id, match_id)
                if match_info is None:
                    print(f"✓ 匹配{match_id}已成功删除")
                else:
                    print(f"✗ 匹配{match_id}仍然存在")
            
            print("\n" + "=" * 60)
            print("测试完成！")
            print("=" * 60)
            
        except Exception as e:
            print(f"✗ 测试过程中发生错误: {e}")
        
        finally:
            await self.cleanup()

async def main():
    """主函数"""
    test = TestDeactivateUser()
    await test.run_test()

if __name__ == "__main__":
    asyncio.run(main())