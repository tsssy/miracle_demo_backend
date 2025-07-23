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

# 假数据模板
MALE_NAMES = [
    "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
    "郑十一", "王十二", "冯十三", "陈十四", "褚十五", "卫十六",
    "蒋十七", "沈十八", "韩十九", "杨二十", "朱二一", "秦二二"
]

FEMALE_NAMES = [
    "小红", "小美", "小丽", "小芳", "小燕", "小花", "小雨", "小雪",
    "小月", "小星", "小云", "小凤", "小琳", "小婷", "小敏", "小慧",
    "小静", "小娟", "小萍", "小霞", "小娜", "小莉", "小梅", "小兰"
]

PERSONALITY_TRAITS = [
    "性格开朗，喜欢运动和旅行，热爱生活",
    "温柔体贴，喜欢读书和音乐，追求内心的平静",
    "活泼可爱，爱好摄影和美食，享受生活的美好",
    "成熟稳重，工作认真负责，有强烈的责任感",
    "幽默风趣，善于沟通，喜欢交朋友",
    "内向安静，喜欢独处思考，热爱艺术",
    "积极向上，充满正能量，喜欢挑战自己",
    "温暖善良，关心他人，有爱心和同情心",
    "聪明睿智，思维敏捷，喜欢学习新知识",
    "浪漫主义者，相信真爱，追求完美的感情",
    "独立自主，有自己的想法和追求，不随波逐流",
    "乐观开朗，总是能看到事情好的一面，给人正能量",
    "细心体贴，善于观察他人的需求，很会照顾人",
    "有责任心，说到做到，值得信赖",
    "有上进心，不断学习进步，追求更好的自己"
]

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
            "gender": 1,  # 男性
            "age": random.randint(18, 35),
            "target_gender": 2,  # 男性寻找女性
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
            "gender": 2,  # 女性
            "age": random.randint(18, 35),
            "target_gender": 1,  # 女性寻找男性
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
            male_count = sum(1 for user in users_data if user["gender"] == 1)
            female_count = sum(1 for user in users_data if user["gender"] == 2)
            print(f"男性用户: {male_count}, 女性用户: {female_count}")
            
            # 显示前几个用户的信息作为示例
            print("\n=== 用户示例 ===")
            for i, user in enumerate(users_data[:5]):
                gender_str = "男" if user["gender"] == 1 else "女"
                target_gender_str = "女" if user["target_gender"] == 2 else "男"
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