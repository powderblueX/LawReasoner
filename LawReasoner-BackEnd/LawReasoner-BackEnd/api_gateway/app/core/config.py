import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    """
    系统核心配置类（基于Pydantic的BaseSettings）
    特点：
      1. 自动从环境变量或.env文件加载配置
      2. 支持类型验证和默认值
      3. 可通过类方法添加自定义验证逻辑
    """

    # >>>>>>>>>>>>>>> 基础配置 <<<<<<<<<<<<<<<<
    API_V1_STR: str = "/api/v1"
    # API接口前缀，用于Swagger文档路由等
    # 示例：http://localhost:8000/api/v1/docs

    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 安全密钥（默认生成随机值）
    # 用途：
    #   - JWT令牌签名
    #   - CSRF保护
    #   - 加密敏感数据
    # 生产环境应通过环境变量覆盖（避免使用默认值）
    
    PROJECT_NAME: str = "法理智推系统"
    # 项目名称（用于文档展示和日志标识）


    # >>>>>>>>>>>>>>> JWT配置 <<<<<<<<<<<<<<<<
    # 60分钟 * 24小时 * 8天 = 8天
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # Token过期时间（分钟）
    # 计算公式：60分钟 * 24小时 * 8天 = 11520分钟


    # >>>>>>>>>>>>>>> CORS跨域配置 <<<<<<<<<<<<<<<<
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    # 允许的跨域请求来源列表
    # 类型：AnyHttpUrl确保必须是合法URL格式
    # 示例：["http://localhost:3000", "https://your-frontend.com"]


    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """
        CORS来源预处理验证器
        功能：将字符串形式的配置自动转换为列表
        示例：
          输入 "http://a.com,http://b.com" => ["http://a.com", "http://b.com"]
          输入 ["http://a.com"] => 保持不变
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


    # >>>>>>>>>>>>>>> 微服务通信配置 <<<<<<<<<<<<<<<<
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    # 认证服务地址（开发环境默认值）
    # Docker Compose中应替换为服务名：http://auth_service:8001

    REASONING_SERVICE_URL: str = "http://localhost:8002"
    # 推理服务地址

    KNOWLEDGE_SERVICE_URL: str = "http://localhost:8003"
    # 知识库服务地址

    CONTRACT_SERVICE_URL: str = "http://localhost:8004"
    

    class Config:
        """
        Pydantic配置子类
        文档：https://pydantic-docs.helpmanual.io/usage/settings/
        """
        case_sensitive = True
        # 环境变量名区分大小写

        env_file = ".env"
        # 从.env文件加载配置（可选）
        # 优先级：环境变量 > .env文件 > 类默认值

# 全局配置实例
settings = Settings() 