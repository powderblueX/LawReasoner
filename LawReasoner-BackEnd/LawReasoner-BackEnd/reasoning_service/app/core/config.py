import os
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseSettings, AnyHttpUrl, validator
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    """项目配置"""
    # API配置
    PROJECT_NAME: str = "法理智推系统推理服务"
    API_V1_STR: str = "/api/v1"
    
    # 安全配置 - 使用与其他服务相同的密钥
    SECRET_KEY: str = "simple-shared-secret-key-123456"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:5173"]
    
    # 验证CORS配置
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///../common_db/shared_db.db"  # 使用共享数据库
    
    # 模型配置
    USE_LOCAL_MODEL: bool = os.environ.get("USE_LOCAL_MODEL", "False").lower() in ("true", "1", "t")
    LOCAL_MODEL_PATH: str = os.environ.get("LOCAL_MODEL_PATH", "model-7B")
    # 提供多个备用URL
    REMOTE_MODEL_URL: str = os.environ.get(
        "REMOTE_MODEL_URL", 
        "https://concrete-informed-iguana.ngrok-free.app/deepseek"  # 主要端点
    )
    # 备用URL列表，如果主URL失败可以尝试
    REMOTE_MODEL_FALLBACK_URLS: List[str] = [
        "https://concrete-informed-iguana.ngrok-free.app/deepseek"
    ]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# 创建全局设置对象
settings = Settings()
