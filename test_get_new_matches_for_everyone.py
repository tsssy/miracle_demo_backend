#!/usr/bin/env python3
"""
测试 get_new_matches_for_everyone 接口的详细测试脚本

功能：
1. 生成测试用户数据
2. 测试单个女性用户匹配
3. 测试所有女性用户批量匹配
4. 测试错误情况（男性用户、不存在的用户等）
5. 验证匹配结果的完整性

作者：Assistant
日期：2024-01-15
"""

import asyncio
import httpx
import json
import sys
import time
from pathlib import Path
from typing import Dict, List

# 添加项目根目录到Python路径
ROOT_PATH = Path(__file__).resolve().parents[0]
sys.path.append(str(ROOT_PATH))

from app.core.database import Database
from app.services.https.UserManagement import UserManagement
from app.services.https.MatchManager import MatchManager

# 测试配置
API_BASE_URL = "http://localhost:8001/api/v1"  # 🔧 MODIFIED: 指向本地测试服务器
TEST_TIMEOUT = 60  # 测试超时时间（秒）

class TestGetNewMatchesForEveryone:
    """get_new_matches_for_everyone 接口测试类"""
    
    def __init__(self):
        self.test_users = []  # 测试用户ID列表
        self.female_users = []  # 女性用户ID列表
        self.male_users = []  # 男性用户ID列表
        self.created_matches = []  # 创建的匹配ID列表
        
    def log(self, level: str, message: str):
        """统一日志输出"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        level_emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }
        emoji = level_emoji.get(level, "📝")
        print(f"[{timestamp}] {emoji} [{level}] {message}")
    
    async def setup_test_environment(self):
        """设置测试环境"""
        self.log("INFO", "🔧 开始设置测试环境...")
        
        try:
            # 连接数据库
            self.log("INFO", "连接数据库...")
            await Database.connect()
            self.log("SUCCESS", "数据库连接成功")
            
            # 初始化用户管理器
            self.log("INFO", "初始化UserManagement...")
            user_manager = UserManagement()
            await user_manager.initialize_from_database()
            self.log("SUCCESS", f"UserManagement初始化完成，当前用户数: {len(user_manager.user_list)}")
            
            # 初始化匹配管理器
            self.log("INFO", "初始化MatchManager...")
            match_manager = MatchManager()
            await match_manager.construct()
            self.log("SUCCESS", f"MatchManager初始化完成，当前匹配数: {len(match_manager.match_list)}")
            
            self.log("SUCCESS", "测试环境设置完成")
            return True
            
        except Exception as e:
            self.log("ERROR", f"设置测试环境失败: {e}")
            return False
    
    async def generate_test_users(self, num_users: int = 10):
        """生成测试用户"""
        self.log("INFO", f"🧑‍🤝‍🧑 开始生成 {num_users} 个测试用户...")
        
        try:
            # 运行generate_fake_users脚本
            from generate_fake_users import generate_fake_users
            await generate_fake_users(num_users)
            
            # 重新初始化用户管理器以加载新用户
            user_manager = UserManagement()
            await user_manager.initialize_from_database()
            
            # 获取最新生成的用户（假设ID从1000000开始）
            self.test_users = []
            self.female_users = []
            self.male_users = []
            
            for user_id, user in user_manager.user_list.items():
                if user_id >= 1000000:  # 新生成的用户
                    self.test_users.append(user_id)
                    if user.gender == 1:  # 女性
                        self.female_users.append(user_id)
                    elif user.gender == 2:  # 男性
                        self.male_users.append(user_id)
            
            self.log("SUCCESS", f"测试用户生成完成")
            self.log("INFO", f"总用户数: {len(self.test_users)}")
            self.log("INFO", f"女性用户数: {len(self.female_users)} - {self.female_users[:5]}{'...' if len(self.female_users) > 5 else ''}")
            self.log("INFO", f"男性用户数: {len(self.male_users)} - {self.male_users[:5]}{'...' if len(self.male_users) > 5 else ''}")
            
            return True
            
        except Exception as e:
            self.log("ERROR", f"生成测试用户失败: {e}")
            return False
    
    async def test_api_call(self, endpoint: str, data: Dict = None, method: str = "POST") -> Dict:
        """测试API调用"""
        url = f"{API_BASE_URL}/{endpoint}"
        
        try:
            self.log("DEBUG", f"🌐 API调用: {method} {url}")
            if data:
                self.log("DEBUG", f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                if method == "POST":
                    response = await client.post(url, json=data)
                elif method == "GET":
                    response = await client.get(url, params=data)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response_data = response.json()
                
                self.log("DEBUG", f"响应状态: {response.status_code}")
                self.log("DEBUG", f"响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                return {
                    "status_code": response.status_code,
                    "data": response_data,
                    "success": response.status_code == 200
                }
                
        except Exception as e:
            self.log("ERROR", f"API调用失败: {e}")
            return {
                "status_code": 500,
                "data": {"detail": str(e)},
                "success": False
            }
    
    async def test_single_female_user_match(self):
        """测试单个女性用户匹配"""
        self.log("INFO", "👩 测试单个女性用户匹配...")
        
        if not self.female_users:
            self.log("WARNING", "没有女性用户可供测试")
            return False
        
        test_female_id = self.female_users[0]
        self.log("INFO", f"选择女性用户ID: {test_female_id}")
        
        # 测试详细消息模式
        result = await self.test_api_call("MatchManager/get_new_matches_for_everyone", {
            "user_id": test_female_id,
            "print_message": True
        })
        
        if result["success"]:
            self.log("SUCCESS", f"单个女性用户匹配成功")
            response_data = result["data"]
            self.log("INFO", f"匹配结果: success={response_data.get('success')}")
            self.log("INFO", f"匹配消息预览: {response_data.get('message', '')[:200]}...")
            
            # 验证匹配是否真的创建了
            await self.verify_matches_created()
            return True
        else:
            self.log("ERROR", f"单个女性用户匹配失败: {result['data']}")
            return False
    
    async def test_batch_female_users_match(self):
        """测试批量女性用户匹配"""
        self.log("INFO", "👭 测试所有女性用户批量匹配...")
        
        # 测试简单消息模式
        result = await self.test_api_call("MatchManager/get_new_matches_for_everyone", {
            "print_message": False
        })
        
        if result["success"]:
            self.log("SUCCESS", f"批量女性用户匹配成功")
            response_data = result["data"]
            self.log("INFO", f"匹配结果: success={response_data.get('success')}")
            self.log("INFO", f"匹配消息: {response_data.get('message', '')}")
            
            # 验证匹配是否真的创建了
            await self.verify_matches_created()
            return True
        else:
            self.log("ERROR", f"批量女性用户匹配失败: {result['data']}")
            return False
    
    async def test_male_user_error(self):
        """测试男性用户错误情况"""
        self.log("INFO", "👨 测试男性用户错误情况...")
        
        if not self.male_users:
            self.log("WARNING", "没有男性用户可供测试")
            return False
        
        test_male_id = self.male_users[0]
        self.log("INFO", f"选择男性用户ID: {test_male_id}")
        
        result = await self.test_api_call("MatchManager/get_new_matches_for_everyone", {
            "user_id": test_male_id,
            "print_message": True
        })
        
        response_data = result["data"]
        if result["success"] and not response_data.get("success", True):
            expected_error = "错误：只能给女性用户匹配"
            if expected_error in response_data.get("message", ""):
                self.log("SUCCESS", f"男性用户错误测试通过: {response_data.get('message')}")
                return True
            else:
                self.log("ERROR", f"男性用户错误消息不符合预期: {response_data.get('message')}")
                return False
        else:
            self.log("ERROR", f"男性用户应该返回错误，但返回了成功: {response_data}")
            return False
    
    async def test_non_existent_user_error(self):
        """测试不存在用户错误情况"""
        self.log("INFO", "👻 测试不存在用户错误情况...")
        
        fake_user_id = 9999999  # 不存在的用户ID
        self.log("INFO", f"使用不存在的用户ID: {fake_user_id}")
        
        result = await self.test_api_call("MatchManager/get_new_matches_for_everyone", {
            "user_id": fake_user_id,
            "print_message": True
        })
        
        response_data = result["data"]
        if result["success"] and not response_data.get("success", True):
            expected_error = "错误：指定的用户不存在"
            if expected_error in response_data.get("message", ""):
                self.log("SUCCESS", f"不存在用户错误测试通过: {response_data.get('message')}")
                return True
            else:
                self.log("ERROR", f"不存在用户错误消息不符合预期: {response_data.get('message')}")
                return False
        else:
            self.log("ERROR", f"不存在用户应该返回错误，但返回了: {response_data}")
            return False
    
    async def verify_matches_created(self):
        """验证匹配是否真的创建了"""
        self.log("INFO", "🔍 验证匹配创建情况...")
        
        try:
            match_manager = MatchManager()
            initial_count = len(match_manager.match_list)
            
            # 重新从数据库加载匹配
            await match_manager.construct()
            final_count = len(match_manager.match_list)
            
            self.log("INFO", f"匹配数量变化: {initial_count} → {final_count}")
            
            # 获取最新的匹配记录
            latest_matches = []
            for match_id, match in match_manager.match_list.items():
                if match_id not in self.created_matches:
                    latest_matches.append(match)
                    self.created_matches.append(match_id)
            
            if latest_matches:
                self.log("SUCCESS", f"发现 {len(latest_matches)} 个新匹配")
                for i, match in enumerate(latest_matches[:3]):  # 只显示前3个
                    user_manager = UserManagement()
                    female_user = user_manager.get_user_instance(match.user_id_1)
                    male_user = user_manager.get_user_instance(match.user_id_2)
                    
                    self.log("INFO", f"匹配 {i+1}: {female_user.telegram_user_name if female_user else match.user_id_1} ↔ {male_user.telegram_user_name if male_user else match.user_id_2}")
                    self.log("INFO", f"  分数: {match.match_score}, 时间: {match.match_time}")
            
            return True
            
        except Exception as e:
            self.log("ERROR", f"验证匹配创建失败: {e}")
            return False
    
    async def cleanup_test_data(self):
        """清理测试数据"""
        self.log("INFO", "🧹 清理测试数据...")
        
        try:
            # 删除测试用户
            if self.test_users:
                delete_count = await Database.delete_many("users", {"_id": {"$in": self.test_users}})
                self.log("INFO", f"删除 {delete_count} 个测试用户")
            
            # 删除创建的匹配
            if self.created_matches:
                delete_count = await Database.delete_many("matches", {"_id": {"$in": self.created_matches}})
                self.log("INFO", f"删除 {delete_count} 个测试匹配")
            
            self.log("SUCCESS", "测试数据清理完成")
            return True
            
        except Exception as e:
            self.log("ERROR", f"清理测试数据失败: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        self.log("INFO", "🚀 开始运行 get_new_matches_for_everyone 接口测试")
        
        start_time = time.time()
        test_results = {}
        
        try:
            # 设置测试环境
            if not await self.setup_test_environment():
                self.log("ERROR", "测试环境设置失败，终止测试")
                return False
            
            # 生成测试用户
            if not await self.generate_test_users(10):
                self.log("ERROR", "生成测试用户失败，终止测试")
                return False
            
            # 测试1: 单个女性用户匹配
            self.log("INFO", "\n" + "="*50)
            self.log("INFO", "测试1: 单个女性用户匹配")
            test_results["single_female"] = await self.test_single_female_user_match()
            
            # 测试2: 批量女性用户匹配
            self.log("INFO", "\n" + "="*50)
            self.log("INFO", "测试2: 批量女性用户匹配")
            test_results["batch_female"] = await self.test_batch_female_users_match()
            
            # 测试3: 男性用户错误
            self.log("INFO", "\n" + "="*50)
            self.log("INFO", "测试3: 男性用户错误处理")
            test_results["male_user_error"] = await self.test_male_user_error()
            
            # 测试4: 不存在用户错误
            self.log("INFO", "\n" + "="*50)
            self.log("INFO", "测试4: 不存在用户错误处理")
            test_results["non_existent_user"] = await self.test_non_existent_user_error()
            
            # 测试结果汇总
            self.log("INFO", "\n" + "="*50)
            self.log("INFO", "测试结果汇总")
            passed_tests = sum(1 for result in test_results.values() if result)
            total_tests = len(test_results)
            
            for test_name, result in test_results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                self.log("INFO", f"{test_name}: {status}")
            
            elapsed_time = time.time() - start_time
            self.log("INFO", f"测试完成，耗时: {elapsed_time:.2f}秒")
            self.log("INFO", f"测试通过率: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
            
            if passed_tests == total_tests:
                self.log("SUCCESS", "🎉 所有测试通过！")
                return True
            else:
                self.log("WARNING", f"⚠️ {total_tests - passed_tests} 个测试失败")
                return False
                
        except Exception as e:
            self.log("ERROR", f"测试过程中发生异常: {e}")
            return False
        
        finally:
            # 清理测试数据
            await self.cleanup_test_data()
            
            # 关闭数据库连接
            await Database.close()
            self.log("INFO", "数据库连接已关闭")

async def main():
    """主函数"""
    print("=" * 80)
    print("🧪 get_new_matches_for_everyone 接口测试脚本")
    print("=" * 80)
    
    tester = TestGetNewMatchesForEveryone()
    success = await tester.run_all_tests()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 测试完成：所有测试通过")
        exit_code = 0
    else:
        print("❌ 测试完成：存在失败的测试")
        exit_code = 1
    
    print("=" * 80)
    return exit_code

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 