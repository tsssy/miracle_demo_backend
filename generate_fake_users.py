#!/usr/bin/env python3
"""
用户数据生成器
生成30个用户，男女数量平均，符合UserManagement数据结构并插入到MongoDB
"""

import asyncio
import random
import sys
from pathlib import Path

# 添加项目根目录到路径
ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from app.core.database import Database
from app.config import settings

# 常见的Telegram男性用户名
MALE_NAMES = [
    "alex_king", "john_doe", "michael99", "david_smith", "chris_jay", "tommy_lee", "kevin_chen", "jason_wu",
    "daniel_brown", "eric_walker", "peter_pan", "samuel_liu", "leo_martin", "bruce_wayne", "tony_stark",
    "jackson_007", "harry_potter", "bobby_ray", "steven_zhang", "matt_clark"
]

# 常见的Telegram女性用户名
FEMALE_NAMES = [
    "sophia_rose", "emma_watson", "olivia_liu", "ava_smith", "mia_jones", "isabella_chen", "amelia_clark",
    "charlotte_xu", "lucy_love", "grace_lee", "zoe_moon", "lily_white", "hannah_sun", "natalie_star",
    "ella_green", "scarlett_fox", "victoria_king", "chloe_queen", "sarah_hope", "ruby_sky"
]

# 英文版性格特征，每条为半段落
PERSONALITY_TRAITS = [
    "Outgoing and adventurous, I love exploring new places and meeting new people. My passion for sports and travel keeps me energetic and open-minded.",
    "Gentle and thoughtful, I enjoy reading and listening to music in my free time. I value inner peace and meaningful conversations with close friends.",
    "Cheerful and creative, I have a passion for photography and discovering delicious food. Life is about enjoying every beautiful moment and sharing joy with others.",
    "Mature and responsible, I take my work seriously and always strive to do my best. My strong sense of duty drives me to support those around me.",
    "Humorous and sociable, I love making people laugh and building connections. Communication is my strength, and I cherish every friendship.",
    "Introverted and calm, I find inspiration in solitude and art. My quiet nature allows me to observe the world deeply and appreciate its subtle beauty.",
    "Positive and motivated, I embrace challenges and constantly seek self-improvement. My optimism helps me overcome obstacles and inspire others.",
    "Warm-hearted and compassionate, I care deeply about others and enjoy helping those in need. Kindness and empathy are at the core of who I am.",
    "Intelligent and curious, I am always eager to learn new things and expand my horizons. My quick thinking helps me adapt to any situation.",
    "A romantic at heart, I believe in true love and strive for meaningful relationships. I am always searching for beauty and perfection in life.",
    "Independent and determined, I have my own dreams and ambitions. I am not afraid to stand out and pursue what I truly believe in.",
    "Optimistic and cheerful, I always look on the bright side and bring positive energy to those around me. Life is too short to dwell on negativity.",
    "Attentive and caring, I am sensitive to the needs of others and enjoy making people feel comfortable. My nurturing nature makes me a reliable friend.",
    "Trustworthy and dependable, I keep my promises and value honesty. People can always count on me in times of need.",
    "Ambitious and hardworking, I am dedicated to personal growth and achieving my goals. I believe in continuous learning and striving for excellence."
]

# 性别常量定义
GENDER_FEMALE = 1  # 女
GENDER_MALE = 2    # 男

async def generate_fake_users(num_users=30):
    """生成假用户数据，确保男女数量平均"""
    print(f"开始生成 {num_users} 个假用户（男女各 {num_users//2} 个）...")
    
    users_data = []
    user_id_start = 1000000  # 从1000000开始生成user_id
    
    # 确保男女数量平均
    male_count = num_users // 2
    female_count = num_users // 2
    
    # 生成男性用户
    for i in range(male_count):
        user_id = user_id_start + i
        name = random.choice(MALE_NAMES) + str(random.randint(1, 999))
        
        user_data = {
            "_id": user_id,  # 使用user_id作为MongoDB的_id
            "telegram_user_name": f"@{name.lower()}",
            "gender": GENDER_MALE,  # 男性
            "age": random.randint(18, 35),
            "target_gender": GENDER_FEMALE,  # 男性寻找女性
            "user_personality_summary": random.choice(PERSONALITY_TRAITS),
            "match_ids": [],  # 初始为空，后续生成匹配时会填充
            "blocked_user_ids": []
        }
        
        users_data.append(user_data)
    
    # 生成女性用户
    for i in range(female_count):
        user_id = user_id_start + male_count + i
        name = random.choice(FEMALE_NAMES) + str(random.randint(1, 999))
        
        user_data = {
            "_id": user_id,  # 使用user_id作为MongoDB的_id
            "telegram_user_name": f"@{name.lower()}",
            "gender": GENDER_FEMALE,  # 女性
            "age": random.randint(18, 35),
            "target_gender": GENDER_MALE,  # 女性寻找男性
            "user_personality_summary": random.choice(PERSONALITY_TRAITS),
            "match_ids": [],  # 初始为空，后续生成匹配时会填充
            "blocked_user_ids": []
        }
        
        users_data.append(user_data)
    
    # 打乱用户顺序，避免男女用户ID连续
    random.shuffle(users_data)
    
    # 批量插入到数据库
    try:
        # 清空现有用户数据
        delete_count = await Database.delete_many("users", {})
        print(f"清空了 {delete_count} 个现有用户")
        
        # 插入新的假用户数据
        inserted_ids = await Database.insert_many("users", users_data)
        print(f"成功插入 {len(inserted_ids)} 个假用户到数据库")
        
        return users_data
        
    except Exception as e:
        print(f"插入用户数据失败: {e}")
        return []

async def main():
    """主函数"""
    print("=== 用户数据生成器启动 ===")
    
    try:
        # 连接数据库
        print("正在连接数据库...")
        await Database.connect()
        print("数据库连接成功")
        
        # 生成假用户数据
        users_data = await generate_fake_users(num_users=30)
        
        if users_data:
            print("\n=== 用户数据生成完成 ===")
            print(f"总用户数: {len(users_data)}")
            
            # 统计性别分布
            male_count = sum(1 for user in users_data if user["gender"] == GENDER_MALE)
            female_count = sum(1 for user in users_data if user["gender"] == GENDER_FEMALE)
            print(f"男性用户: {male_count}, 女性用户: {female_count}")
            
            # 显示前几个用户的信息作为示例
            print("\n=== 用户示例 ===")
            for i, user in enumerate(users_data[:5]):
                gender_str = "男" if user["gender"] == GENDER_MALE else "女"
                target_gender_str = "女" if user["target_gender"] == GENDER_FEMALE else "男"
                print(f"用户 {i+1}: ID={user['_id']}, 用户名={user['telegram_user_name']}, "
                      f"性别={gender_str}, 年龄={user['age']}, 目标性别={target_gender_str}")
        
    except Exception as e:
        print(f"生成用户数据时发生错误: {e}")
        
    finally:
        # 关闭数据库连接
        await Database.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    asyncio.run(main()) 