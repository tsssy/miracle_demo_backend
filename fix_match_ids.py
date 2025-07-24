#!/usr/bin/env python3
"""
修复用户match_ids并重新设置测试环境
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Database
from app.services.https.UserManagement import UserManagement
from app.services.https.MatchManager import MatchManager


async def fix_user_match_ids():
    """修复用户的match_ids"""
    print("🔧 修复用户match_ids")
    print("=" * 40)
    
    try:
        # 初始化数据库连接
        await Database.connect()
        
        # 初始化服务
        user_manager = UserManagement()
        await user_manager.initialize_from_database()
        
        match_manager = MatchManager()
        await match_manager.construct()
        
        # 获取测试用户
        test_user_ids = [99001, 99002, 99003, 99004]
        
        # 查找涉及测试用户的所有匹配
        matches_in_db = await Database.find("matches", {
            "$or": [
                {"user_id_1": {"$in": test_user_ids}},
                {"user_id_2": {"$in": test_user_ids}}
            ]
        })
        
        print(f"发现 {len(matches_in_db)} 个涉及测试用户的匹配")
        
        # 重建用户的match_ids
        user_match_mapping = {}
        for user_id in test_user_ids:
            user_match_mapping[user_id] = []
        
        for match in matches_in_db:
            match_id = match['_id']
            user1_id = match['user_id_1']
            user2_id = match['user_id_2']
            
            if user1_id in test_user_ids:
                user_match_mapping[user1_id].append(match_id)
            if user2_id in test_user_ids:
                user_match_mapping[user2_id].append(match_id)
            
            print(f"   匹配 {match_id}: {user1_id} ↔ {user2_id}")
        
        # 更新用户的match_ids (内存和数据库)
        print("\n🔄 更新用户match_ids:")
        for user_id, match_ids in user_match_mapping.items():
            user = user_manager.get_user_instance(user_id)
            if user:
                # 更新内存
                user.match_ids = list(set(match_ids))  # 去重
                print(f"   用户 {user_id}: 更新为 {user.match_ids}")
                
                # 更新数据库
                await Database.update_one(
                    "users",
                    {"_id": user_id},
                    {"$set": {"match_ids": user.match_ids}}
                )
                print(f"   ✅ 用户 {user_id} 数据库已更新")
        
        print("\n✅ match_ids修复完成!")
        
        # 验证修复结果
        print("\n🔍 验证修复结果:")
        for user_id in test_user_ids:
            user = user_manager.get_user_instance(user_id)
            if user:
                db_user = await Database.find_one("users", {"_id": user_id})
                memory_match_ids = set(user.match_ids)
                db_match_ids = set(db_user.get('match_ids', []))
                
                if memory_match_ids == db_match_ids:
                    print(f"   ✅ 用户 {user_id}: match_ids = {user.match_ids}")
                else:
                    print(f"   ❌ 用户 {user_id}: 仍然不一致")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    await fix_user_match_ids()


if __name__ == "__main__":
    asyncio.run(main())