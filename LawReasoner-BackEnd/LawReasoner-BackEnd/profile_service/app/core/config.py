import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, validator

class Settings(BaseSettings):
    """
    系统核心配置类（继承自 Pydantic 的 BaseSettings）
    """
    # API配置
    API_V1_STR: str = "/api/v1"
    # 使用与auth_service完全相同的简化密钥
    SECRET_KEY: str = "simple-shared-secret-key-123456"
    PROJECT_NAME: str = "法理智推系统个人中心服务"
    
    # 数据库配置
    SQLITE_DATABASE_URI: str = "sqlite:///../common_db/shared_db.db"  # 使用共享数据库
    
    # JWT配置
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天，与auth_service保持一致
    
    # 跨域配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:5173"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 