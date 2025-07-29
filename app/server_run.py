#Daniel 到此一游

import uvicorn
from fastapi import FastAPI, Request, WebSocket
from contextlib import asynccontextmanager
import sys
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware # 导入 CORS 中间件
import json
import time
import asyncio
from fastapi.websockets import WebSocketDisconnect # 导入 WebSocketDisconnect

ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from app.api.v1.api import api_router
from app.ws import all_ws_routers
from app.config import settings
from app.core.database import Database
from app.utils.my_logger import MyLogger
from app.utils.singleton_status import SingletonStatusReporter
from app.services.https.UserManagement import UserManagement
from app.services.https.MatchManager import MatchManager
from app.services.https.ChatroomManager import ChatroomManager
from app.services.https.N8nWebhookManager import N8nWebhookManager
from app.services.https.DataIntegrity import DataIntegrity

logger = MyLogger("server")

# 全局变量用于控制自动保存任务
auto_save_task = None

async def auto_save_to_database():
    """
    每10秒自动保存所有单例实例到数据库的后台任务
    """
    global auto_save_task
    logger.info("启动自动保存任务，每10秒保存一次所有单例数据到数据库")
    
    while True:
        try:
            await asyncio.sleep(10)  # 等待10秒
            
            logger.info("🔄 开始执行自动保存...")
            start_time = time.time()
            
            # 执行数据完备性检查（在保存前清理无效数据）
            try:
                logger.info("🔍 开始数据完备性检查...")
                data_integrity = DataIntegrity()
                integrity_result = await data_integrity.run_integrity_check()
                
                if integrity_result["success"]:
                    logger.info(f"✅ 数据完备性检查完成: {integrity_result['checks_completed']}/{integrity_result['total_checks']} 项检查通过")
                else:
                    logger.warning(f"⚠️ 数据完备性检查部分失败: {integrity_result['checks_completed']}/{integrity_result['total_checks']} 项检查通过")
                    if integrity_result["errors"]:
                        for error in integrity_result["errors"]:
                            logger.warning(f"⚠️ 完备性检查错误: {error}")
            except Exception as e:
                logger.error(f"❌ 数据完备性检查失败: {e}")
            
            # 保存UserManagement数据
            try:
                user_manager = UserManagement()
                user_save_success = await user_manager.save_to_database()  # 保存所有用户
                if user_save_success:
                    logger.info("✅ UserManagement数据保存成功")
                else:
                    logger.warning("⚠️ UserManagement数据保存部分失败")
            except Exception as e:
                logger.error(f"❌ UserManagement数据保存失败: {e}")
            
            # 保存MatchManager数据
            try:
                match_manager = MatchManager()
                match_save_success = await match_manager.save_to_database()  # 保存所有匹配
                if match_save_success:
                    logger.info("✅ MatchManager数据保存成功")
                else:
                    logger.warning("⚠️ MatchManager数据保存部分失败")
            except Exception as e:
                logger.error(f"❌ MatchManager数据保存失败: {e}")
            
            # 保存ChatroomManager数据
            try:
                chatroom_manager = ChatroomManager()
                chatroom_save_success = await chatroom_manager.save_chatroom_history()  # 保存所有聊天室历史
                if chatroom_save_success:
                    logger.info("✅ ChatroomManager数据保存成功")
                else:
                    logger.warning("⚠️ ChatroomManager数据保存部分失败")
            except Exception as e:
                logger.error(f"❌ ChatroomManager数据保存失败: {e}")
            
            elapsed_time = time.time() - start_time
            logger.info(f"🔄 自动保存完成，耗时: {elapsed_time:.3f}秒")
            
        except asyncio.CancelledError:
            logger.info("自动保存任务被取消")
            break
        except Exception as e:
            logger.error(f"自动保存任务发生错误: {e}")
            # 发生错误时等待一段时间再继续
            await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global auto_save_task
    
    # 启动时连接数据库
    logger.info("正在连接数据库...")
    try:
        await Database.connect()  # 恢复数据库连接
        logger.info("数据库连接成功")
        
        # 初始化UserManagement缓存
        logger.info("正在初始化UserManagement缓存...")
        user_manager = UserManagement()
        await user_manager.initialize_from_database()
        logger.info("UserManagement缓存初始化完成")
        
        # 初始化MatchManager缓存
        logger.info("正在初始化MatchManager缓存...")
        match_manager = MatchManager()
        await match_manager.construct()
        logger.info("MatchManager缓存初始化完成")
        
        # 初始化ChatroomManager缓存
        logger.info("正在初始化ChatroomManager缓存...")
        chatroom_manager = ChatroomManager()
        construct_success = await chatroom_manager.construct()  # 从数据库加载聊天室数据
        
        # 检查初始化状态
        if construct_success:
            logger.info(f"ChatroomManager缓存初始化完成 - 加载了 {len(chatroom_manager.chatrooms)} 个聊天室")
            logger.info(f"ChatroomManager可用的聊天室ID: {list(chatroom_manager.chatrooms.keys())}")
        else:
            logger.error("ChatroomManager缓存初始化失败")
            
        logger.info("ChatroomManager缓存初始化完成")
        
        # 初始化N8nWebhookManager
        logger.info("正在初始化N8nWebhookManager...")
        n8n_webhook_manager = N8nWebhookManager()
        logger.info("N8nWebhookManager初始化完成")
        
        # 启动自动保存任务
        logger.info("正在启动自动保存后台任务...")
        auto_save_task = asyncio.create_task(auto_save_to_database())
        logger.info("自动保存后台任务已启动")
        
    except Exception as e:
        logger.error(f"数据库连接或初始化失败: {str(e)}")
        raise
    
    yield
    
    # 关闭时的清理工作
    logger.info("正在关闭服务...")
    
    # 取消自动保存任务
    if auto_save_task and not auto_save_task.done():
        logger.info("正在停止自动保存任务...")
        auto_save_task.cancel()
        try:
            await auto_save_task
        except asyncio.CancelledError:
            logger.info("自动保存任务已停止")
    
    # 执行最后一次保存
    logger.info("执行最后一次数据保存...")
    try:
        user_manager = UserManagement()
        await user_manager.save_to_database()
        logger.info("最终用户数据保存完成")
        
        match_manager = MatchManager()
        await match_manager.save_to_database()
        logger.info("最终匹配数据保存完成")
        
        chatroom_manager = ChatroomManager()
        await chatroom_manager.save_chatroom_history()
        logger.info("最终聊天室数据保存完成")
    except Exception as e:
        logger.error(f"最终数据保存失败: {e}")
    
    # 断开数据库连接
    logger.info("正在关闭数据库连接...")
    await Database.close()  # 恢复数据库关闭
    logger.info("数据库连接已关闭")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="New LoveLush User Service API",
    version=settings.VERSION,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "users",
            "description": "用户相关操作",
        },
        {
            "name": "matches",
            "description": "匹配相关操作",
        },
        {
            "name": "chatrooms",
            "description": "聊天室相关操作",
        }
    ]
)

# 全局请求和响应日志中间件
@app.middleware("http")
async def log_requests_and_responses(request: Request, call_next):
    # 生成请求ID
    request_id = f"req_{int(time.time() * 1000)}"
    
    # 记录请求开始
    logger.info(f"🔵 [{request_id}] ====== 收到新请求 ======")
    logger.info(f"🔵 [{request_id}] 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🔵 [{request_id}] 方法: {request.method}")
    logger.info(f"🔵 [{request_id}] URL: {request.url}")
    logger.info(f"🔵 [{request_id}] 路径: {request.url.path}")
    logger.info(f"🔵 [{request_id}] 客户端IP: {request.client.host if request.client else 'Unknown'}")
    
    # 记录请求前单例状态
    try:
        singleton_status_before = SingletonStatusReporter.get_status_summary()
        logger.info(f"🔵 [{request_id}] ====== 请求前单例状态 ======")
        logger.info(f"🔵 [{request_id}] {singleton_status_before}")
    except Exception as e:
        logger.error(f"🔵 [{request_id}] 获取单例状态失败: {e}")
    
    # 记录请求头
    logger.info(f"🔵 [{request_id}] ====== 请求头 ======")
    for header_name, header_value in request.headers.items():
        logger.info(f"🔵 [{request_id}] {header_name}: {header_value}")
    
    # 记录请求体（如果是POST/PUT/PATCH请求）
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                logger.info(f"🔵 [{request_id}] ====== 请求体 ======")
                logger.info(f"🔵 [{request_id}] 原始数据: {body}")
                try:
                    # 尝试解析JSON
                    json_body = json.loads(body)
                    logger.info(f"🔵 [{request_id}] JSON数据: {json.dumps(json_body, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    logger.info(f"🔵 [{request_id}] 非JSON数据: {body.decode('utf-8', errors='ignore')}")
            else:
                logger.info(f"🔵 [{request_id}] ====== 请求体: 空 ======")
        except Exception as e:
            logger.error(f"🔵 [{request_id}] 读取请求体失败: {e}")
    
    # 记录请求开始时间
    start_time = time.time()
    
    # 处理请求
    try:
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        logger.info(f"🟢 [{request_id}] ====== 响应信息 ======")
        logger.info(f"🟢 [{request_id}] 状态码: {response.status_code}")
        logger.info(f"🟢 [{request_id}] 处理时间: {process_time:.3f}秒")
        
        # 记录响应头
        logger.info(f"🟢 [{request_id}] ====== 响应头 ======")
        for header_name, header_value in response.headers.items():
            logger.info(f"🟢 [{request_id}] {header_name}: {header_value}")
        
        # 尝试记录响应体（如果是JSON响应）
        try:
            # 获取响应体
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # 重新创建响应对象（因为body_iterator只能读取一次）
            from fastapi.responses import Response
            new_response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            if response_body:
                logger.info(f"🟢 [{request_id}] ====== 响应体 ======")
                try:
                    # 尝试解析JSON
                    json_response = json.loads(response_body)
                    logger.info(f"🟢 [{request_id}] JSON响应: {json.dumps(json_response, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    logger.info(f"🟢 [{request_id}] 非JSON响应: {response_body.decode('utf-8', errors='ignore')}")
            else:
                logger.info(f"🟢 [{request_id}] ====== 响应体: 空 ======")
            
            # 记录响应后单例状态
            try:
                singleton_status_after = SingletonStatusReporter.get_status_summary()
                logger.info(f"🟢 [{request_id}] ====== 响应后单例状态 ======")
                logger.info(f"🟢 [{request_id}] {singleton_status_after}")
            except Exception as e:
                logger.error(f"🟢 [{request_id}] 获取响应后单例状态失败: {e}")
            
            logger.info(f"🟢 [{request_id}] ====== 请求完成 ======")
            return new_response
            
        except Exception as e:
            logger.error(f"🟢 [{request_id}] 读取响应体失败: {e}")
            
            # 记录响应后单例状态 (错误情况)
            try:
                singleton_status_after = SingletonStatusReporter.get_status_summary()
                logger.info(f"🟢 [{request_id}] ====== 响应后单例状态 (异常) ======")
                logger.info(f"🟢 [{request_id}] {singleton_status_after}")
            except Exception as status_e:
                logger.error(f"🟢 [{request_id}] 获取响应后单例状态失败: {status_e}")
                
            logger.info(f"🟢 [{request_id}] ====== 请求完成 ======")
            return response
            
    except Exception as e:
        # 记录异常
        process_time = time.time() - start_time
        logger.error(f"🔴 [{request_id}] ====== 请求异常 ======")
        logger.error(f"🔴 [{request_id}] 异常信息: {str(e)}")
        logger.error(f"🔴 [{request_id}] 处理时间: {process_time:.3f}秒")
        logger.error(f"🔴 [{request_id}] ====== 请求失败 ======")
        raise

# 注册HTTP API路由
app.include_router(api_router, prefix="/api/v1")
logger.info(f"HTTP API路由已注册")

# 批量注册WebSocket路由
for ws_router in all_ws_routers:
    app.include_router(ws_router)
logger.info(f"WebSocket路由已注册")

# 添加 CORS 中间件，只允许特定来源
cors_origins = [
    "https://cupid-yukio-frontend.vercel.app",  # 生产环境前端地址
    "https://cupid-yukio-frontend-test.vercel.app",
    "http://localhost:5173",  # 本地开发环境前端地址
    "http://127.0.0.1:5173",  # 本地IP地址
]

logger.info(f"CORS允许的域名: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源头
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

@app.get("/")
async def root():
    logger.debug("访问根路径")
    return {"message": "Welcome to New LoveLush User Service API"}

if __name__ == "__main__":
    logger.info(f"启动服务器: {settings.PROJECT_NAME} v{settings.VERSION}")
    
    uvicorn_config = {
        "app": "app.server_run:app",
        "host": "0.0.0.0",
        "port": 8000,  # 生产环境使用8000端口
        "reload": False,
        "workers": 1
    }
    
    try:
        uvicorn.run(**uvicorn_config)
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        sys.exit(1)