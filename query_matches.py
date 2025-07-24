#!/usr/bin/env python3
"""
直接查询数据库中的匹配记录
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Database


async def query_matches():
    """查询数据库中的匹配记录"""
    print("🔍 查询数据库中的匹配记录")
    print("=" * 50)
    
    try:
        # 初始化数据库连接
        await Database.connect()
        
        # 查询所有匹配
        all_matches = await Database.find("matches")
        print(f"数据库中总共有 {len(all_matches)} 个匹配")
        
        # 查找涉及99001的匹配
        matches_99001 = await Database.find("matches", {
            "$or": [
                {"user_id_1": 99001},
                {"user_id_2": 99001}
            ]
        })
        print(f"\n涉及用户99001的匹配: {len(matches_99001)} 个")
        for match in matches_99001:
            print(f"   匹配 {match['_id']}: {match['user_id_1']} ↔ {match['user_id_2']}")
            print(f"   创建时间: {match.get('match_time', 'Unknown')}")
            print(f"   聊天室ID: {match.get('chatroom_id', 'None')}")
        
        # 查找特定ID的匹配
        specific_matches = [1753120284506091, 1753120284506092]
        print(f"\n查找特定匹配ID:")
        for match_id in specific_matches:
            match = await Database.find_one("matches", {"_id": match_id})
            if match:
                print(f"   ✅ 匹配 {match_id}: {match['user_id_1']} ↔ {match['user_id_2']}")
            else:
                print(f"   ❌ 匹配 {match_id}: 未找到")
        
        # 查询涉及所有测试用户的匹配
        test_user_ids = [99001, 99002, 99003, 99004]
        test_matches = await Database.find("matches", {
            "$or": [
                {"user_id_1": {"$in": test_user_ids}},
                {"user_id_2": {"$in": test_user_ids}}
            ]
        })
        print(f"\n涉及所有测试用户的匹配: {len(test_matches)} 个")
        for match in test_matches:
            print(f"   匹配 {match['_id']}: {match['user_id_1']} ↔ {match['user_id_2']}")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    await query_matches()


if __name__ == "__main__":
    asyncio.run(main())