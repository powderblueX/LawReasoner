from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from app.api.routes import api_router
from app.core.config import settings

from app.db.base import Base
from app.db.session import engine

# 调试信息
print("===== 认证服务启动 =====")
print(f"数据库连接: {settings.SQLITE_DATABASE_URI}")
print(f"JWT密钥: {settings.SECRET_KEY[:10]}...")
print(f"CORS配置: {settings.BACKEND_CORS_ORIGINS}")

# 检查数据库文件是否存在
db_file = settings.SQLITE_DATABASE_URI.replace("sqlite:///", "")
if db_file.startswith("../"):
    db_file = os.path.join(os.path.dirname(__file__), db_file)
    
print(f"数据库文件路径: {db_file}")
if os.path.exists(db_file):
    print(f"数据库文件存在，大小: {os.path.getsize(db_file) / 1024:.2f} KB")
else:
    print(f"警告: 数据库文件不存在，将尝试创建")

# 创建数据库表
Base.metadata.create_all(bind=engine)
print("数据库表已更新")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="法理智推系统认证服务",
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
print(f"登录路由: {settings.API_V1_STR}/login")

if __name__ == "__main__":
    print(f"启动认证服务，监听端口: 8001")
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True) 