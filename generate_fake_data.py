#!/usr/bin/env python3
"""
测试数据生成器
生成符合UserManagement和MatchManager数据结构的假数据并插入到MongoDB
"""

import asyncio
import random
import time
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 添加项目根目录到路径
ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from app.core.database import Database
from app.config import settings

# 假数据模板
MALE_NAMES = [
    "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
    "郑十一", "王十二", "冯十三", "陈十四", "褚十五", "卫十六",
    "蒋十七", "沈十八", "韩十九", "杨二十"
]

FEMALE_NAMES = [
    "小红", "小美", "小丽", "小芳", "小燕", "小花", "小雨", "小雪",
    "小月", "小星", "小云", "小凤", "小琳", "小婷", "小敏", "小慧",
    "小静", "小娟", "小萍", "小霞"
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
    "浪漫主义者，相信真爱，追求完美的感情"
]

MATCH_REASONS = [
    "你们都喜欢旅行和探索新事物",
    "性格互补，一个外向一个内向，很有默契",
    "都热爱音乐，可能会有很多共同话题",
    "年龄相近，人生阶段相似，容易理解彼此",
    "都喜欢运动健身，可以一起保持健康生活",
    "兴趣爱好相似，都喜欢读书和思考",
    "工作领域相关，可能会有职业上的共鸣",
    "都比较成熟稳重，适合长期发展",
    "性格都很温和，相处应该会很和谐",
    "都有积极的人生态度，能够互相鼓励"
]

async def generate_fake_users(num_users=50):
    """生成假用户数据"""
    print(f"开始生成 {num_users} 个假用户...")
    
    users_data = []
    user_id_start = 1000000  # 从1000000开始生成user_id
    
    for i in range(num_users):
        # 随机选择性别 (1=男, 2=女)
        gender = random.choice([1, 2])
        
        # 根据性别选择姓名
        if gender == 1:
            name = random.choice(MALE_NAMES) + str(random.randint(1, 999))
            target_gender = 2  # 男性寻找女性
        else:
            name = random.choice(FEMALE_NAMES) + str(random.randint(1, 999))
            target_gender = 1  # 女性寻找男性
        
        user_id = user_id_start + i
        
        user_data = {
            "_id": user_id,  # 使用user_id作为MongoDB的_id
            "telegram_user_name": f"@{name.lower()}",
            "gender": gender,
            "age": random.randint(18, 35),
            "target_gender": target_gender,
            "user_personality_summary": random.choice(PERSONALITY_TRAITS),
            "match_ids": [],  # 初始为空，后续生成匹配时会填充
            "blocked_user_ids": []
        }
        
        users_data.append(user_data)
    
    # 批量插入到数据库
    try:
        # 清空现有用户数据（可选）
        delete_count = await Database.delete_many("users", {})
        print(f"清空了 {delete_count} 个现有用户")
        
        # 插入新的假用户数据
        inserted_ids = await Database.insert_many("users", users_data)
        print(f"成功插入 {len(inserted_ids)} 个假用户到数据库")
        
        return users_data
        
    except Exception as e:
        print(f"插入用户数据失败: {e}")
        return []

async def generate_fake_matches(users_data, num_matches=20):
    """生成假匹配数据"""
    print(f"开始生成 {num_matches} 个假匹配...")
    
    if len(users_data) < 2:
        print("用户数据不足，无法生成匹配")
        return []
    
    # 按性别分组用户
    male_users = [user for user in users_data if user["gender"] == 1]
    female_users = [user for user in users_data if user["gender"] == 2]
    
    if not male_users or not female_users:
        print("缺少男性或女性用户，无法生成匹配")
        return []
    
    print(f"可用用户: 男性 {len(male_users)} 个，女性 {len(female_users)} 个")
    
    matches_data = []
    match_id_start = int(time.time() * 1000000)  # 使用时间戳生成match_id
    used_pairs = set()  # 记录已使用的配对，避免重复
    
    attempts = 0
    max_attempts = num_matches * 3  # 最多尝试次数，避免无限循环
    
    for i in range(num_matches):
        if attempts >= max_attempts:
            print(f"达到最大尝试次数，停止生成匹配。已生成 {len(matches_data)} 个匹配")
            break
            
        attempts += 1
        
        # 随机选择一个女性用户来配对男性用户
        female_user = random.choice(female_users)
        male_user = random.choice(male_users)
        
        # 创建配对标识符（女性ID, 男性ID）
        pair_id = (female_user["_id"], male_user["_id"])
        
        # 检查是否已经配对过
        if pair_id in used_pairs:
            i -= 1  # 重新尝试这个索引
            continue
        
        used_pairs.add(pair_id)
        
        match_id = match_id_start + len(matches_data)  # 使用已生成的匹配数量作为索引
        
        # 生成随机的UTC时间字符串（过去30天内）
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23) 
        minutes_ago = random.randint(0, 59)
        seconds_ago = random.randint(0, 59)
        
        # 计算过去的时间
        past_time = datetime.now(timezone.utc) - timedelta(
            days=days_ago, 
            hours=hours_ago, 
            minutes=minutes_ago, 
            seconds=seconds_ago
        )
        match_time_str = past_time.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        match_data = {
            "_id": match_id,  # 使用match_id作为MongoDB的_id主键
            "user_id_1": female_user["_id"],  # 女性用户ID
            "user_id_2": male_user["_id"],    # 男性用户ID
            "description_to_user_1": random.choice(MATCH_REASONS),
            "description_to_user_2": random.choice(MATCH_REASONS),
            "is_liked": random.choice([True, False]),
            "match_score": random.randint(60, 95),
            "mutual_game_scores": {},  # 初始为空
            "chatroom_id": None,
            "match_time": match_time_str
        }
        
        matches_data.append(match_data)
        
        # 更新用户的match_ids
        if match_id not in female_user.get("match_ids", []):
            female_user.setdefault("match_ids", []).append(match_id)
        if match_id not in male_user.get("match_ids", []):
            male_user.setdefault("match_ids", []).append(match_id)
    
    try:
        # 清空现有匹配数据（可选）
        delete_count = await Database.delete_many("matches", {})
        print(f"清空了 {delete_count} 个现有匹配")
        
        # 插入新的假匹配数据
        if matches_data:
            inserted_ids = await Database.insert_many("matches", matches_data)
            print(f"成功插入 {len(inserted_ids)} 个假匹配到数据库")
            
            # 更新用户的match_ids
            for user in users_data:
                if user.get("match_ids"):
                    await Database.update_one(
                        "users",
                        {"_id": user["_id"]},
                        {"$set": {"match_ids": user["match_ids"]}}
                    )
            print("成功更新用户的匹配ID列表")
        
        return matches_data
        
    except Exception as e:
        print(f"插入匹配数据失败: {e}")
        return []

async def main():
    """主函数"""
    print("=== 假数据生成器启动 ===")
    
    try:
        # 连接数据库
        print("正在连接数据库...")
        await Database.connect()
        print("数据库连接成功")
        
        # 生成假用户数据
        users_data = await generate_fake_users(num_users=30)
        
        if users_data:
            # 生成假匹配数据
            matches_data = await generate_fake_matches(users_data, num_matches=15)
            
            print("\n=== 数据生成完成 ===")
            print(f"总用户数: {len(users_data)}")
            print(f"总匹配数: {len(matches_data)}")
            
            # 统计性别分布
            male_count = sum(1 for user in users_data if user["gender"] == 1)
            female_count = sum(1 for user in users_data if user["gender"] == 2)
            print(f"男性用户: {male_count}, 女性用户: {female_count}")
            
            # 统计匹配状态
            liked_matches = sum(1 for match in matches_data if match["is_liked"])
            print(f"已点赞匹配: {liked_matches}, 未点赞匹配: {len(matches_data) - liked_matches}")
        
    except Exception as e:
        print(f"生成假数据时发生错误: {e}")
        
    finally:
        # 关闭数据库连接
        await Database.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    asyncio.run(main())