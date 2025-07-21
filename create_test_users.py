#!/usr/bin/env python3
"""
创建WebSocket测试用户的脚本
"""
import httpx
import asyncio

BASE_URL = "http://localhost:8000/api/v1/users"

async def create_test_users():
    print("Creating test users for WebSocket testing...")
    
    # 创建测试用户数据
    test_users = [
        {"telegram_id": 10001, "gender": "female", "endpoint": "female_users"},
        {"telegram_id": 10002, "gender": "male", "endpoint": "male_users", "mode": 1},
        {"telegram_id": 10003, "gender": "female", "endpoint": "female_users"},
        {"telegram_id": 10004, "gender": "male", "endpoint": "male_users", "mode": 1},
    ]
    
    async with httpx.AsyncClient() as client:
        for user_data in test_users:
            endpoint = user_data.pop("endpoint")
            gender = user_data.pop("gender")
            
            try:
                print(f"Creating {gender} user with telegram_id: {user_data['telegram_id']}")
                response = await client.post(f"{BASE_URL}/{endpoint}", json=user_data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"✅ Successfully created user: {result.get('user_id', user_data['telegram_id'])}")
                    else:
                        print(f"❌ Failed to create user: {result}")
                else:
                    print(f"❌ HTTP Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error creating user {user_data['telegram_id']}: {e}")
    
    print("\n🎉 Test user creation completed!")
    print("Available user IDs for WebSocket testing:")
    print("- 10001 (female)")
    print("- 10002 (male)")  
    print("- 10003 (female)")
    print("- 10004 (male)")
    print("\nYou can now use these user IDs in the WebSocket test page.")

if __name__ == "__main__":
    asyncio.run(create_test_users())