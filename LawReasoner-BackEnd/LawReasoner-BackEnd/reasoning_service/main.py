from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.api import api_router
from app.core.config import settings
from common_db.db_utils import Base, engine
from app.db.init_db import init_db

# 加载环境变量
load_dotenv()

# 调试信息
print("===== 推理服务启动 =====")
print(f"数据库连接: {settings.DATABASE_URL}")
print(f"JWT密钥: {settings.SECRET_KEY[:10]}...")
print(f"CORS配置: {settings.BACKEND_CORS_ORIGINS}")
print(f"模型配置: 使用本地模型={settings.USE_LOCAL_MODEL}, 模型路径={settings.LOCAL_MODEL_PATH}")
print(f"远程模型URL: {settings.REMOTE_MODEL_URL}")

# 调用初始化函数创建数据库表
init_db()
print("数据库表已初始化")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="法理智推系统推理服务",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含所有API路由
app.include_router(api_router, prefix=settings.API_V1_STR)
print(f"API路由注册完成，前缀: {settings.API_V1_STR}")

# 输出具体路由信息，便于调试
for route in app.routes:
    if hasattr(route, "path"):
        print(f"已注册路由: {route.path}")


if __name__ == "__main__":
    print(f"启动推理服务，监听端口: 8004")
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
