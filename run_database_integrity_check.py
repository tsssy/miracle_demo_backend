#!/usr/bin/env python3
"""
数据库完备性检查脚本
这是一个独立的脚本，用于对数据库进行完整的数据完备性检查和清理
注意：这是一个高复杂度操作，会直接操作数据库，请谨慎使用
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH))

from app.core.database import Database
from app.services.https.DataIntegrity import DataIntegrity
from app.utils.my_logger import MyLogger

# 创建日志记录器
logger = MyLogger("DatabaseIntegrityCheck")

async def main():
    """
    主函数：执行数据库级别的完备性检查
    """
    try:
        print("=" * 80)
        print("🔍 数据库完备性检查脚本启动")
        print("=" * 80)
        print("⚠️  警告：这是一个高复杂度操作，会直接操作数据库")
        print("⚠️  请确保您了解此操作的影响，并已备份重要数据")
        print("=" * 80)
        
        # 用户确认
        confirm = input("是否继续执行数据库完备性检查？(输入 'yes' 继续): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return
        
        start_time = time.time()
        
        # 连接数据库
        print("\n🔌 正在连接数据库...")
        logger.info("正在连接数据库...")
        await Database.connect()
        print("✅ 数据库连接成功")
        logger.info("数据库连接成功")
        
        # 创建数据完备性检查器实例
        print("\n🛠️ 初始化数据完备性检查器...")
        logger.info("初始化数据完备性检查器...")
        data_integrity = DataIntegrity()
        print("✅ 数据完备性检查器初始化完成")
        
        # 执行数据库级别检查
        print("\n🔍 开始数据库级别完备性检查...")
        print("⏳ 这可能需要一些时间，请耐心等待...")
        logger.info("开始执行数据库级别完备性检查...")
        
        # 运行检查
        result = await data_integrity.run_database_only_integrity_check()
        
        # 计算执行时间
        elapsed_time = time.time() - start_time
        
        # 输出结果
        print("\n" + "=" * 80)
        print("📊 数据库完备性检查结果")
        print("=" * 80)
        
        if result["success"]:
            print("✅ 检查状态: 成功")
        else:
            print("❌ 检查状态: 部分失败")
        
        print(f"📈 完成检查: {result['checks_completed']}/{result['total_checks']} 项")
        print(f"⏱️  执行时间: {elapsed_time:.2f} 秒")
        
        # 数据清理统计
        print("\n📊 数据清理统计:")
        print("  🗑️  删除记录:")
        print(f"    • 删除的 Matches: {result['deleted_records']['matches']}")
        print(f"    • 删除的 Users: {result['deleted_records']['users']}")
        print(f"    • 删除的 Chatrooms: {result['deleted_records']['chatrooms']}")
        print(f"    • 删除的 Messages: {result['deleted_records']['messages']}")
        
        print("  🔄 更新记录:")
        print(f"    • 补充match_id的 Users: {result['updated_records']['users']}")
        print(f"    • 更新message_ids的 Chatrooms: {result['updated_records']['chatrooms']}")
        
        total_deleted = sum(result['deleted_records'].values())
        total_updated = sum(result['updated_records'].values())
        total_operations = total_deleted + total_updated
        print(f"  📊 总计操作数: {total_operations} (删除: {total_deleted}, 更新: {total_updated})")
        
        # 错误信息
        if result["errors"]:
            print("\n❌ 检查过程中的错误:")
            for error in result["errors"]:
                print(f"  • {error}")
        
        # 成功消息
        if result["success"] and total_operations == 0:
            print("\n🎉 数据库数据完备性良好，无需清理！")
        elif result["success"]:
            print(f"\n🎉 数据库完备性检查完成，已清理 {total_operations} 项不一致数据！")
        else:
            print("\n⚠️ 数据库完备性检查部分完成，请检查错误信息")
        
        # 日志记录结果
        logger.info(f"数据库完备性检查完成 - 成功: {result['success']}, "
                   f"检查项: {result['checks_completed']}/{result['total_checks']}, "
                   f"操作数: {total_operations}(删除: {total_deleted}, 更新: {total_updated}), 耗时: {elapsed_time:.2f}秒")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        logger.warning("用户中断了数据库完备性检查")
    except Exception as e:
        print(f"\n❌ 脚本执行失败: {str(e)}")
        logger.error(f"数据库完备性检查脚本执行失败: {e}")
        sys.exit(1)
    finally:
        # 关闭数据库连接
        try:
            print("\n🔌 正在关闭数据库连接...")
            await Database.close()
            print("✅ 数据库连接已关闭")
            logger.info("数据库连接已关闭")
        except Exception as e:
            print(f"⚠️ 关闭数据库连接时发生错误: {e}")
            logger.warning(f"关闭数据库连接时发生错误: {e}")
        
        print("\n" + "=" * 80)
        print("🏁 数据库完备性检查脚本结束")
        print("=" * 80)

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main()) 