#!/usr/bin/env python3
"""
验证用户的match_ids是否正确
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Database
from app.services.https.UserManagement import UserManagement


async def verify_user_match_ids():
    """验证用户的match_ids"""
    print("🔍 验证用户的match_ids")
    print("=" * 40)
    
    try:
        # 初始化数据库连接
        await Database.connect()
        
        # 初始化UserManagement
        user_manager = UserManagement()
        await user_manager.initialize_from_database()
        
        # 检查测试用户的match_ids
        test_user_ids = [99001, 99002, 99003, 99004]
        
        print("📋 内存中的用户match_ids:")
        for user_id in test_user_ids:
            user = user_manager.get_user_instance(user_id)
            if user:
                print(f"   用户 {user_id} ({user.telegram_user_name}): match_ids = {user.match_ids}")
            else:
                print(f"   用户 {user_id}: 未找到")
        
        print("\n📋 数据库中的用户match_ids:")
        users_in_db = await Database.find("users", {"_id": {"$in": test_user_ids}})
        for user in users_in_db:
            match_ids = user.get('match_ids', [])
            print(f"   用户 {user['_id']} ({user['telegram_user_name']}): match_ids = {match_ids}")
        
        # 检查匹配数据
        print("\n📋 匹配数据:")
        matches_in_db = await Database.find("matches", {
            "$or": [
                {"user_id_1": {"$in": test_user_ids}},
                {"user_id_2": {"$in": test_user_ids}}
            ]
        })
        for match in matches_in_db:
            print(f"   匹配 {match['_id']}: {match['user_id_1']} ↔ {match['user_id_2']}")
        
        # 分析不一致的情况
        print("\n🔍 分析结果:")
        for user_id in test_user_ids:
            user = user_manager.get_user_instance(user_id)
            if user:
                memory_match_ids = set(user.match_ids)
                
                # 找到数据库中的用户数据
                db_user = next((u for u in users_in_db if u['_id'] == user_id), None)
                if db_user:
                    db_match_ids = set(db_user.get('match_ids', []))
                    
                    if memory_match_ids == db_match_ids:
                        print(f"   ✅ 用户 {user_id}: 内存和数据库一致")
                    else:
                        print(f"   ❌ 用户 {user_id}: 不一致")
                        print(f"      内存: {memory_match_ids}")
                        print(f"      数据库: {db_match_ids}")
                        print(f"      缺失: {db_match_ids - memory_match_ids}")
                        print(f"      多余: {memory_match_ids - db_match_ids}")
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    await verify_user_match_ids()


if __name__ == "__main__":
    asyncio.run(main())