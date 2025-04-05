import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str = "法理智推系统知识库服务"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 数据库配置
    SQLITE_DATABASE_URI: str = "sqlite:///./knowledge_service.db"
    
    # 知识库配置
    KNOWLEDGE_DIR: str = "./data/knowledge"
    MAX_SEARCH_RESULTS: int = 20
    
    # 向量检索配置
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"  # 或其他适合中文的模型
    EMBEDDING_DIMENSION: int = 384

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 