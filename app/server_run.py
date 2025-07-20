#Daniel 到此一游

import uvicorn
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import sys
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware # 导入 CORS 中间件
import json
import time

ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from app.api.v1.api import api_router
from app.config import settings
from app.core.database import Database
from app.utils.my_logger import MyLogger
from app.utils.singleton_status import SingletonStatusReporter

logger = MyLogger("server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时连接数据库
    logger.info("正在连接数据库...")
    try:
        await Database.connect()  # 恢复数据库连接
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise
    yield
    # 关闭时断开数据库连接
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
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)
logger.info(f"API路由已注册，前缀: {settings.API_V1_STR}")

@app.get("/")
async def root():
    logger.debug("访问根路径")
    return {"message": "Welcome to New LoveLush User Service API"}

if __name__ == "__main__":
    logger.info(f"启动服务器: {settings.PROJECT_NAME} v{settings.VERSION}")
    
    uvicorn_config = {
        "app": "app.server_run:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": False,
        "workers": 1,
        "ws": "none"  # Disable WebSocket support
    }
    
    try:
        uvicorn.run(**uvicorn_config)
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        sys.exit(1)