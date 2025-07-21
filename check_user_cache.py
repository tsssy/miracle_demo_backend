#!/usr/bin/env python3
"""
检查UserManagement缓存中的用户ID
"""
import asyncio
import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from app.core.database import Database
from app.services.https.UserManagement import UserManagement

async def check_user_cache():
    print("检查UserManagement缓存中的用户...")
    
    try:
        # 连接数据库
        await Database.connect()
        print("✅ 数据库连接成功")
        
        # 初始化UserManagement
        user_manager = UserManagement()
        await user_manager.initialize_from_database()
        print("✅ UserManagement初始化完成")
        
        # 检查缓存内容
        print(f"\n📊 缓存统计:")
        print(f"总用户数: {len(user_manager.user_list)}")
        print(f"男性用户数: {len(user_manager.male_user_list)}")
        print(f"女性用户数: {len(user_manager.female_user_list)}")
        
        print(f"\n👥 所有用户ID列表:")
        for user_id in sorted(user_manager.user_list.keys()):
            user = user_manager.user_list[user_id]
            print(f"- {user_id} (性别: {user.gender}, 用户名: {user.telegram_user_name})")
        
        # 特别检查1000000这个ID
        print(f"\n🔍 检查用户ID 1000000:")
        user_1000000 = user_manager.get_user_instance(1000000)
        if user_1000000:
            print(f"✅ 用户1000000存在: {user_1000000.telegram_user_name}, 性别: {user_1000000.gender}")
        else:
            print("❌ 用户1000000不存在")
            
        # 检查字符串版本
        user_1000000_str = user_manager.get_user_instance("1000000")
        if user_1000000_str:
            print(f"✅ 用户'1000000'(字符串)存在: {user_1000000_str.telegram_user_name}")
        else:
            print("❌ 用户'1000000'(字符串)不存在")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        await Database.close()

if __name__ == "__main__":
    asyncio.run(check_user_cache())