from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx
from app.core.config import settings

# 创建API路由实例，用于组织所有接口
api_router = APIRouter()

# ------------------------- 基础接口 -------------------------
@api_router.get("/health")
async def health_check():
    """健康检查接口
    用途：用于服务探活或负载均衡检测
    返回示例：{"status": "ok"}
    """
    return {"status": "ok"}


@api_router.get("/")
async def root():
    """根接口
    功能：提供API基本信息
    返回数据：
        - message: 系统名称
        - version: API版本号
        - docs: Swagger文档地址（从配置动态获取）
    """
    return {
        "message": "法理智推系统API网关",
        "version": "0.1.0",
        "docs": f"{settings.API_V1_STR}/docs"
    }

# ------------------------- 微服务代理接口 -------------------------
# 认证服务代理
@api_router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(path: str, request: Request):
    """认证服务代理
    功能：将/auth开头的请求转发到认证微服务
    实现逻辑：
        1. 动态拼接目标URL（从配置获取AUTH_SERVICE_URL）
        2. 使用httpx异步转发原始请求
        3. 将响应原样返回给客户端
    参数：
        - path: URL路径的通配符（如"auth/login"中的"login"）
        - request: 原始请求对象（自动注入）
    """
    async with httpx.AsyncClient() as client:
        # 拼接目标地址，例如：http://auth_service:8001/api/v1/login
        url = f"{settings.AUTH_SERVICE_URL}/api/v1/{path}"
        # 转换FastAPI Request为httpx请求
        headers = dict(request.headers)
        body = await request.body() if request.method in ["POST", "PUT"] else None
        
        # 转发请求（保留方法、头、参数、体）
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=dict(request.query_params)
        )
        # 将响应包装为FastAPI的JSONResponse
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )


# 推理服务代理
@api_router.api_route("/reasoning/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def reasoning_proxy(path: str, request: Request):
    """推理服务代理
    功能：将/reasoning开头的请求转发到推理微服务
    注意：实际转发前可添加鉴权逻辑（如验证JWT）
    """
    async with httpx.AsyncClient() as client:
        url = f"{settings.REASONING_SERVICE_URL}/api/v1/{path}"
        body = await request.body() if request.method in ["POST", "PUT"] else None
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=body,
            params=dict(request.query_params)
        )
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )


# 知识库服务代理
@api_router.api_route("/knowledge/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def knowledge_proxy(path: str, request: Request): 
    """知识库服务代理
    特点：
        - 支持所有HTTP方法
        - {path:path}可匹配含斜杠的子路径（如/knowledge/law/articles/123）
    """
    async with httpx.AsyncClient() as client:
        url = f"{settings.KNOWLEDGE_SERVICE_URL}/api/v1/{path}"
        body = await request.body() if request.method in ["POST", "PUT"] else None
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=body,
            params=dict(request.query_params)
        )
        # 直接返回原始响应内容（避免二次JSON解析）
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        ) 

# 合同服务代理
@api_router.api_route("/contract/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def contract_proxy(path: str, request: Request):
    """合同服务代理
    功能：将/contract开头的请求转发到合同微服务
    """
    async with httpx.AsyncClient() as client:
        url = f"{settings.CONTRACT_SERVICE_URL}/api/v1/{path}"
        body = await request.body() if request.method in ["POST", "PUT"] else None
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=body,
            params=dict(request.query_params)
        )
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
