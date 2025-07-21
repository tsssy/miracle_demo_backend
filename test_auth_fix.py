#!/usr/bin/env python3
"""
测试认证修复
"""
import asyncio
import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from app.core.database import Database
from app.services.https.UserManagement import UserManagement

async def test_authentication_fix():
    print("测试认证修复...")
    
    try:
        # 连接数据库并初始化UserManagement
        await Database.connect()
        user_manager = UserManagement()
        await user_manager.initialize_from_database()
        
        # 模拟WebSocket认证逻辑
        test_cases = ["1000000", 1000000, "1000001", "nonexistent"]
        
        for user_id_input in test_cases:
            print(f"\n🧪 测试用户ID: {user_id_input} (类型: {type(user_id_input)})")
            
            try:
                # 这是修复后的逻辑
                user_id_int = int(user_id_input)
                user_instance = user_manager.get_user_instance(user_id_int)
                
                if user_instance:
                    print(f"✅ 认证成功: {user_instance.telegram_user_name}")
                else:
                    print(f"❌ 认证失败: 用户不存在")
                    
            except (ValueError, TypeError) as e:
                # 如果无法转换为整数，尝试直接使用原值
                print(f"⚠️ 无法转换为整数: {e}")
                user_instance = user_manager.get_user_instance(user_id_input)
                if user_instance:
                    print(f"✅ 认证成功(原值): {user_instance.telegram_user_name}")
                else:
                    print(f"❌ 认证失败: 用户不存在")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        await Database.close()

if __name__ == "__main__":
    asyncio.run(test_authentication_fix())