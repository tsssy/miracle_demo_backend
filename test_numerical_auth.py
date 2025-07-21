#!/usr/bin/env python3
"""
测试更新后的认证逻辑
"""
import asyncio
import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from app.core.database import Database
from app.services.https.UserManagement import UserManagement

async def test_numerical_auth():
    print("测试数字检查认证逻辑...")
    
    try:
        # 连接数据库并初始化UserManagement
        await Database.connect()
        user_manager = UserManagement()
        await user_manager.initialize_from_database()
        
        # 测试用例：各种不同类型的用户ID输入
        test_cases = [
            ("1000000", "全数字字符串"),
            ("1000001", "全数字字符串"),
            (1000000, "整数"),
            ("abc123", "包含字母的字符串"),
            ("user_test", "非数字字符串"),
            ("0", "零"),
            ("-1000000", "负数字符串"),
            ("", "空字符串")
        ]
        
        for user_id_input, description in test_cases:
            print(f"\n🧪 测试用户ID: '{user_id_input}' ({description})")
            
            # 模拟认证逻辑
            if isinstance(user_id_input, str) and user_id_input.isdigit():
                user_id_for_lookup = int(user_id_input)
                print(f"   📝 是全数字，转换为int: {user_id_for_lookup}")
            else:
                user_id_for_lookup = user_id_input
                print(f"   📝 不是全数字，保持原样: {user_id_for_lookup} (类型: {type(user_id_for_lookup)})")
            
            user_instance = user_manager.get_user_instance(user_id_for_lookup)
            
            if user_instance:
                print(f"   ✅ 认证成功: {user_instance.telegram_user_name}")
            else:
                print(f"   ❌ 认证失败: 用户不存在")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        await Database.close()

if __name__ == "__main__":
    asyncio.run(test_numerical_auth())