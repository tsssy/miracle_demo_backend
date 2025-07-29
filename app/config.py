from pathlib import Path
import os
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[1]

load_dotenv()


class Settings:
    # 项目基本信息
    PROJECT_NAME: str = "NewLoveLushUserService"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # MongoDB配置
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "miracle_demo")
    MONGODB_USERNAME: str = os.getenv("MONGODB_USERNAME", "root")
    MONGODB_PASSWORD: str = os.getenv("MONGODB_PASSWORD", "Awr20020311")
    MONGODB_AUTH_SOURCE: str = os.getenv("MONGODB_AUTH_SOURCE", "admin")

    # JWT配置 (为了保持结构完整性，即使当前未使用)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 默认30分钟

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 