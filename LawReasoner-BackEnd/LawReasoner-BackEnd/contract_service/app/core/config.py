from pydantic import AnyHttpUrl, BaseSettings, validator
from typing import Any, Dict, List, Optional, Union

class Settings(BaseSettings):
    BASE_URL: str = "http://concrete-informed-iguana.ngrok-free.app"
    PROJECT_NAME: str = "合同服务"
    API_V1_STR: str = "/api/v1"
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://122.51.69.223", "http://47.117.153.17"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

settings = Settings()