from pydantic import AnyHttpUrl, BaseSettings, validator
from typing import Any, Dict, List, Optional, Union

class Settings(BaseSettings):
    BASE_URL: str = "http://concrete-informed-iguana.ngrok-free.app"
    PROJECT_NAME: str = "合同服务"
    API_V1_STR: str = "/api/v1"
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:5173"]

settings = Settings()