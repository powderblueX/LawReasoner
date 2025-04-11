from fastapi import APIRouter
from app.api.routes import router as chat_router

# 创建主路由
api_router = APIRouter()

# 包含所有子路由
# 使用"/reasoning"前缀，与API网关的路由结构匹配
api_router.include_router(chat_router, prefix="/reasoning", tags=["reasoning"]) 