#!/usr/bin/env python3
"""
直接测试用户注销功能（不通过HTTP API）
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.https.UserManagement import UserManagement
from app.services.https.MatchManager import MatchManager
from app.objects.User import User
from app.objects.Match import Match
from app.core.database import Database

async def test_deactivate_user():
    """直接测试用户注销功能"""
    print("=" * 60)
    print("开始用户注销功能直接测试")
    print("=" * 60)
    
    try:
        # 连接数据库
        print("1. 连接数据库...")
        await Database.connect()
        print("✓ 数据库连接成功")
        
        # 初始化服务
        print("\n2. 初始化服务...")
        user_manager = UserManagement()
        await user_manager.initialize_from_database()
        
        match_manager = MatchManager()
        await match_manager.construct()
        print("✓ 服务初始化成功")
        
        # 创建测试用户
        print("\n3. 创建测试用户...")
        user1_id = user_manager.create_new_user("test_deactivate_1", 7001, 1)  # 男性
        user2_id = user_manager.create_new_user("test_deactivate_2", 7002, 2)  # 女性
        user3_id = user_manager.create_new_user("test_deactivate_3", 7003, 1)  # 男性
        
        print(f"✓ 创建用户成功: {user1_id}, {user2_id}, {user3_id}")
        
        # 创建匹配
        print("\n4. 创建匹配关系...")
        match1 = await match_manager.create_match(user1_id, user2_id, "测试匹配1", "测试匹配2", 85)
        match2 = await match_manager.create_match(user1_id, user3_id, "测试匹配3", "测试匹配4", 75)
        
        print(f"✓ 创建匹配成功: {match1.match_id}, {match2.match_id}")
        
        # 保存到数据库
        print("\n5. 保存数据到数据库...")
        await user_manager.save_to_database()
        await match_manager.save_to_database()
        print("✓ 数据保存成功")
        
        # 验证初始状态
        print("\n6. 验证初始状态...")
        user1 = user_manager.get_user_instance(user1_id)
        user2 = user_manager.get_user_instance(user2_id)
        user3 = user_manager.get_user_instance(user3_id)
        
        print(f"用户1 match_ids: {user1.match_ids}")
        print(f"用户2 match_ids: {user2.match_ids}")
        print(f"用户3 match_ids: {user3.match_ids}")
        print(f"MatchManager中的匹配数量: {len(match_manager.match_list)}")
        
        # 执行用户注销
        print(f"\n7. 注销用户1 (ID: {user1_id})...")
        success = await user_manager.deactivate_user(user1_id)
        
        if success:
            print("✓ 用户注销成功")
        else:
            print("✗ 用户注销失败")
            return
        
        # 验证注销后的状态
        print("\n8. 验证注销后的状态...")
        
        # 检查用户1是否被删除
        user1_after = user_manager.get_user_instance(user1_id)
        if user1_after is None:
            print("✓ 用户1已成功删除")
        else:
            print("✗ 用户1仍然存在")
        
        # 检查用户2和用户3的match_ids是否已清理
        user2_after = user_manager.get_user_instance(user2_id)
        user3_after = user_manager.get_user_instance(user3_id)
        
        print(f"注销后 - 用户2 match_ids: {user2_after.match_ids}")
        print(f"注销后 - 用户3 match_ids: {user3_after.match_ids}")
        
        # 检查匹配是否被删除
        match1_after = match_manager.get_match(match1.match_id)
        match2_after = match_manager.get_match(match2.match_id)
        
        if match1_after is None:
            print(f"✓ 匹配{match1.match_id}已成功删除")
        else:
            print(f"✗ 匹配{match1.match_id}仍然存在")
            
        if match2_after is None:
            print(f"✓ 匹配{match2.match_id}已成功删除")
        else:
            print(f"✗ 匹配{match2.match_id}仍然存在")
        
        print(f"注销后 - MatchManager中的匹配数量: {len(match_manager.match_list)}")
        
        # 验证数据库状态
        print("\n9. 验证数据库状态...")
        
        # 检查数据库中的用户
        user1_db = await Database.find_one("users", {"_id": user1_id})
        if user1_db is None:
            print("✓ 用户1已从数据库中删除")
        else:
            print("✗ 用户1仍在数据库中")
        
        # 检查数据库中的匹配
        match1_db = await Database.find_one("matches", {"_id": match1.match_id})
        match2_db = await Database.find_one("matches", {"_id": match2.match_id})
        
        if match1_db is None:
            print(f"✓ 匹配{match1.match_id}已从数据库中删除")
        else:
            print(f"✗ 匹配{match1.match_id}仍在数据库中")
            
        if match2_db is None:
            print(f"✓ 匹配{match2.match_id}已从数据库中删除")
        else:
            print(f"✗ 匹配{match2.match_id}仍在数据库中")
        
        # 检查其他用户的数据库记录
        user2_db = await Database.find_one("users", {"_id": user2_id})
        user3_db = await Database.find_one("users", {"_id": user3_id})
        
        print(f"数据库中用户2的match_ids: {user2_db.get('match_ids', [])}")
        print(f"数据库中用户3的match_ids: {user3_db.get('match_ids', [])}")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await Database.close()

if __name__ == "__main__":
    asyncio.run(test_deactivate_user())