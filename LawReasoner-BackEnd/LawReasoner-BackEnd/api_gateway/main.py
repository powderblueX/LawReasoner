from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request

from app.api.routes import api_router # 主路由文件
from app.core.config import settings # 系统配置

# 调试信息
print("===== API网关启动 =====")
print(f"认证服务URL: {settings.AUTH_SERVICE_URL}")
print(f"个人资料服务URL: {settings.PROFILE_SERVICE_URL}")
print(f"推理服务URL: {settings.REASONING_SERVICE_URL}")
print(f"CORS配置: {settings.BACKEND_CORS_ORIGINS}")

# ------------------------- FastAPI应用初始化 -------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="法理智推系统API网关",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
"""
FastAPI实例化关键参数说明：
- title/docs标签页显示的标题
- description/API文档的详细描述
- version/API版本（遵循语义化版本）
- openapi_url/自定义OpenAPI schema路径（默认在/docs可见）
"""

# ------------------------- CORS跨域配置 -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS, # 允许的源列表（从配置读取）
    allow_credentials=True, # 允许携带Cookie
    allow_methods=["*"], # 允许所有HTTP方法
    allow_headers=["*"], # 允许所有请求头
    expose_headers=["*"], # 允许前端访问的响应头
    max_age=86400, # 预检请求缓存时间（秒）
)
"""
CORS策略说明：
1. allow_origins: 生产环境应严格指定前端地址（如["https://your-domain.com"]）
2. allow_credentials: 为True时前端才能接收Set-Cookie
3. expose_headers: 允许前端访问的响应头部
4. max_age: 预检请求缓存时间，降低OPTIONS请求次数
"""

# 自定义OPTIONS预检请求处理器
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """处理所有OPTIONS预检请求，返回正确的CORS头"""
    response = JSONResponse(content={"detail": "OK"})
    
    # 设置CORS响应头
    origin = request.headers.get("origin", "")
    
    if origin:
        if "*" in settings.BACKEND_CORS_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = "*"
        elif origin in settings.BACKEND_CORS_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
        elif settings.BACKEND_CORS_ORIGINS:
            # 默认使用第一个配置的源
            response.headers["Access-Control-Allow-Origin"] = settings.BACKEND_CORS_ORIGINS[0]
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "86400"
    
    return response

# ------------------------- 路由注册 -------------------------
app.include_router(api_router, prefix=settings.API_V1_STR)
print(f"API路由注册完成，前缀: {settings.API_V1_STR}")
print(f"认证转发路由: {settings.API_V1_STR}/auth/*")
print(f"资料转发路由: {settings.API_V1_STR}/profile/*")
print(f"推理转发路由: {settings.API_V1_STR}/reasoning/*")
"""
路由挂载说明：
- api_router: 来自routes.py的所有路由
- prefix: 为所有路由添加前缀（如/api/v1/auth/login）
效果：
  原路由 /health => 实际访问路径 /api/v1/health
"""

# ------------------------- 开发服务器启动 -------------------------
if __name__ == "__main__":
    print(f"启动API网关，监听端口: 8000")
    uvicorn.run(
        "main:app",     # 模块路径:FastAPI实例（main.py中的app）
        host="0.0.0.0", # 监听所有网络接口
        port=8000,      # 端口（与docker-compose.yml一致）
        reload=True     # 开发模式：代码修改自动重启
    )
"""
uvicorn.run参数说明：
- host="0.0.0.0": 允许外部访问（默认localhost只能本机访问）
- TODO: reload: 仅用于开发，生产环境应关闭
"""
