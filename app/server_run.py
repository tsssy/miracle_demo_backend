import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from app.api.v1.api import api_router
from app.config import settings
from app.core.database import Database
from app.utils.my_logger import MyLogger

logger = MyLogger("server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时连接数据库
    logger.info("正在连接数据库...")
    try:
        # await Database.connect()  # 暂时注释掉数据库连接
        logger.info("数据库连接已跳过或成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise
    yield
    # 关闭时断开数据库连接
    logger.info("正在关闭数据库连接...")
    # await Database.close()  # 暂时注释掉数据库关闭
    logger.info("数据库连接已关闭或跳过")


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
        "reload": True,
        "workers": 1
    }
    
    try:
        uvicorn.run(**uvicorn_config)
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        sys.exit(1) 