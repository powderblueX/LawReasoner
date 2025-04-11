from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, Response, StreamingResponse
import httpx
from app.core.config import settings
import logging
import json
from typing import Dict

from app.api import deps

# 创建API路由实例，用于组织所有接口
api_router = APIRouter()
logger = logging.getLogger(__name__)

# ------------------------- 基础接口 -------------------------
@api_router.get("/health")
async def health_check():
    """健康检查接口
    用途：用于服务探活或负载均衡检测
    返回示例：{"status": "ok"}
    """
    return {"status": "ok", "message": "API gateway service is running"}


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

# 统一响应格式的包装函数
def wrap_response(data, message="操作成功", code=200):
    """将微服务的响应包装成统一的格式
    格式: {code: 200, data: ..., message: ""}
    """
    return {
        "code": code,
        "data": data,
        "message": message
    }

# 处理错误响应的包装函数
def wrap_error(message="操作失败", code=500, detail=None):
    """将错误包装成统一的格式
    格式: {code: 非200数值, data: null, message: "错误信息"}
    """
    return {
        "code": code,
        "data": detail,  # 可能为null或包含详细错误信息
        "message": message
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
        
        # 从响应中获取数据
        try:
            content = response.json()
            
            # 认证服务可能已经是期望的格式，不需要额外包装
            # 检查响应是否已经符合 {code, data, message} 格式
            if isinstance(content, dict) and all(k in content for k in ["code", "data", "message"]):
                # 已经是标准格式，直接返回
                return JSONResponse(content=content, status_code=response.status_code)
            else:
                # 包装为标准格式
                wrapped_content = wrap_response(
                    data=content,
                    message="操作成功",
                    code=200 if response.status_code < 400 else response.status_code
                )
                return JSONResponse(content=wrapped_content, status_code=200)  # 统一返回200
                
        except Exception:
            # 如果不是JSON响应，返回原始内容
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )


# 用户资料服务代理
@api_router.api_route("/profile/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def profile_proxy(path: str, request: Request):
    """用户资料服务代理
    功能：将/profile开头的请求转发到用户资料微服务
    注意：实际转发前可添加鉴权逻辑（如验证JWT）
    """
    print(f"收到用户资料服务请求，路径: {path}, 方法: {request.method}")
    target_url = f"{settings.PROFILE_SERVICE_URL}/api/v1/profile/{path}"
    print(f"转发到目标URL: {target_url}")
    
    try:
        # 获取并打印认证头（调试用）
        headers = dict(request.headers)
        auth_header = headers.get("authorization", "无认证头")
        # 打印认证头，但只显示前10个字符（避免泄露完整token）
        print(f"认证头: {auth_header[:15]}...")
        
        if "authorization" not in headers:
            print("警告：请求中没有认证头")
        
        async with httpx.AsyncClient() as client:
            # 获取请求体和参数
            body = await request.body() if request.method in ["POST", "PUT"] else None
            params = dict(request.query_params)
            
            # 打印完整请求信息（调试用）
            print(f"请求方法: {request.method}")
            print(f"请求参数: {params}")
            print(f"请求体长度: {len(body) if body else 0} 字节")
            
            # 发送请求到目标服务
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=params,
                timeout=30.0  # 增加超时时间
            )
            
            # 打印响应信息
            print(f"用户资料服务响应状态码: {response.status_code}")
            
            # 尝试解析JSON响应
            try:
                content = response.json()
                # 简化输出，避免大型响应日志
                if isinstance(content, dict) and "detail" in content:
                    print(f"用户资料服务响应详情: {content['detail']}")
                else:
                    print(f"用户资料服务响应: 成功 (长度: {len(str(content))})")
                
                # 检查响应是否已经符合 {code, data, message} 格式
                if isinstance(content, dict) and all(k in content for k in ["code", "data", "message"]):
                    # 已经是标准格式，直接返回
                    return JSONResponse(content=content, status_code=200)
                else:
                    # 包装为标准格式
                    wrapped_content = wrap_response(
                        data=content,
                        message="操作成功",
                        code=200 if response.status_code < 400 else response.status_code
                    )
                    return JSONResponse(content=wrapped_content, status_code=200)  # 统一返回200
                
            except Exception as parse_error:
                print(f"解析响应内容失败 (非JSON格式): {str(parse_error)}")
                # 返回原始内容，但添加CORS头
                response_obj = Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
                # 添加CORS头
                response_obj.headers["Access-Control-Allow-Credentials"] = "true"
                if settings.BACKEND_CORS_ORIGINS:
                    response_obj.headers["Access-Control-Allow-Origin"] = settings.BACKEND_CORS_ORIGINS[0]
                
                return response_obj
            
    except httpx.RequestError as e:
        error_msg = f"连接用户资料服务失败: {str(e)}"
        print(f"错误: {error_msg}")
        
        # 创建错误响应但带有CORS头
        return JSONResponse(
            content={
                "code": 500,
                "message": f"服务暂时不可用，请稍后再试。(错误: {str(e)[:100]})",
                "data": None
            },
            status_code=200,  # 统一返回200，错误信息在content中
            headers={
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Origin": settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except Exception as e:
        error_msg = f"转发用户资料服务请求时出错: {str(e)}"
        print(f"错误: {error_msg}")
        
        # 创建错误响应但带有CORS头
        return JSONResponse(
            content={
                "code": 500,
                "message": f"服务暂时不可用，请稍后再试。(错误: {str(e)[:100]})",
                "data": None
            },
            status_code=200,  # 统一返回200，错误信息在content中
            headers={
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Origin": settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )


# 推理服务代理
@api_router.api_route("/reasoning/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], include_in_schema=False)
async def reasoning_proxy(
    request: Request,
    path: str,
    current_user: Dict = Depends(deps.get_current_user_optional),
):
    """
    推理服务代理路由函数 - 将请求转发到推理微服务
    
    Args:
        request: 原始请求对象
        path: 请求路径参数（URL中/reasoning/后的所有内容）
        current_user: 当前用户信息（可选）
    
    Returns:
        来自推理服务的响应，经过统一格式化
    """
    try:
        logger.info(f"Proxying request to reasoning service: {path}")
        logger.debug(f"Request method: {request.method}")
        
        # 构建目标URL
        target_url = f"{settings.REASONING_SERVICE_URL}/{path}"
        
        # 获取请求头（包括授权信息）
        headers = {}
        for name, value in request.headers.items():
            if name.lower() != "host":
                headers[name] = value

        # 提取认证信息并传递
        if current_user:
            headers["X-User-ID"] = str(current_user.get("id", ""))
            headers["X-Username"] = str(current_user.get("username", ""))
            logger.debug(f"Forwarding user info: {current_user.get('username')}")
        
        # 获取请求参数
        params = dict(request.query_params)
        
        # 获取请求体
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.body()
            if body:
                try:
                    # 尝试解析JSON
                    body = json.loads(body)
                except:
                    # 如果不是JSON，保持原样
                    pass
        
        # 转发请求到推理服务
        timeout = httpx.Timeout(10.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=params,
                json=body if isinstance(body, (dict, list)) else None,
                content=body if not isinstance(body, (dict, list)) and body else None,
            )
            
            # 构建响应
            logger.info(f"Reasoning service response status: {response.status_code}")
            
            # 对于流式响应，直接返回
            if request.url.path.endswith('/chat') and "text/event-stream" in response.headers.get("content-type", ""):
                return StreamingResponse(
                    content=response.aiter_bytes(),
                    status_code=response.status_code,
                    headers={
                        **dict(response.headers),
                        # 添加CORS头
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization"
                    }
                )
            
            try:
                # 尝试解析JSON响应
                response_data = response.json()
                
                # 检查是否已经是标准格式 {code, message, data, ...}
                if isinstance(response_data, dict) and "code" in response_data and "message" in response_data:
                    # 已经是标准格式，保留所有原始字段
                    content = response_data
                else:
                    # 包装为标准格式
                    content = {
                        "code": 200 if 200 <= response.status_code < 300 else response.status_code,
                        "message": "Success" if 200 <= response.status_code < 300 else "Error",
                        "data": response_data
                    }
            except:
                # 非JSON响应处理
                content = {
                    "code": 200 if 200 <= response.status_code < 300 else response.status_code,
                    "message": "Success" if 200 <= response.status_code < 300 else "Error",
                    "data": response.text
                }
            
            # 返回响应（保留原始状态码和头信息）
            return JSONResponse(
                content=content,
                status_code=200,  # 始终返回200，实际状态在content中
                headers={
                    **dict(response.headers),
                    # 添加CORS头
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
    
    except Exception as e:
        logger.error(f"Error proxying request to reasoning service: {str(e)}")
        # 构建错误响应
        return JSONResponse(
            content={
                "code": 500,
                "message": f"服务暂时不可用，请稍后再试。(错误: {str(e)[:100]})",
                "data": None
            },
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )


# 合同服务代理
@api_router.api_route("/contract/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], include_in_schema=False)
async def contract_proxy(
    request: Request,
    path: str,
    current_user: Dict = Depends(deps.get_current_user_optional),
):
    """
    合同服务代理路由函数 - 将请求转发到合同微服务
    
    Args:
        request: 原始请求对象
        path: 请求路径参数（URL中/contract/后的所有内容）
        current_user: 当前用户信息（可选）
    
    Returns:
        来自合同服务的响应，经过统一格式化
    """
    try:
        logger.info(f"Proxying request to contract service: {path}")
        logger.debug(f"Request method: {request.method}")
        
        # 构建目标URL
        target_url = f"{settings.CONTRACT_SERVICE_URL}/{path}"
        
        # 获取请求头（包括授权信息）
        headers = {}
        for name, value in request.headers.items():
            if name.lower() != "host":
                headers[name] = value

        # 提取认证信息并传递
        if current_user:
            headers["X-User-ID"] = str(current_user.get("id", ""))
            headers["X-Username"] = str(current_user.get("username", ""))
            logger.debug(f"Forwarding user info: {current_user.get('username')}")
        
        # 获取请求参数
        params = dict(request.query_params)
        
        # 获取请求体
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.body()
            if body:
                try:
                    # 尝试解析JSON
                    body = json.loads(body)
                except:
                    # 如果不是JSON，保持原样
                    pass
        
        # 转发请求到合同服务
        timeout = httpx.Timeout(10.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=params,
                json=body if isinstance(body, (dict, list)) else None,
                content=body if not isinstance(body, (dict, list)) and body else None,
            )
            
            # 构建响应
            logger.info(f"Contract service response status: {response.status_code}")
            
            # 对于流式响应，直接返回
            if "text/event-stream" in response.headers.get("content-type", ""):
                return StreamingResponse(
                    content=response.aiter_bytes(),
                    status_code=response.status_code,
                    headers={
                        **dict(response.headers),
                        # 添加CORS头
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization"
                    }
                )
            
            try:
                # 尝试解析JSON响应
                response_data = response.json()
                
                # 检查是否已经是标准格式 {code, message, data, ...}
                if isinstance(response_data, dict) and "code" in response_data and "message" in response_data:
                    # 已经是标准格式，保留所有原始字段
                    content = response_data
                else:
                    # 包装为标准格式
                    content = {
                        "code": 200 if 200 <= response.status_code < 300 else response.status_code,
                        "message": "Success" if 200 <= response.status_code < 300 else "Error",
                        "data": response_data
                    }
            except:
                # 非JSON响应处理
                content = {
                    "code": 200 if 200 <= response.status_code < 300 else response.status_code,
                    "message": "Success" if 200 <= response.status_code < 300 else "Error",
                    "data": response.text
                }
            
            # 返回响应（保留原始状态码和头信息）
            return JSONResponse(
                content=content,
                status_code=200,  # 始终返回200，实际状态在content中
                headers={
                    **dict(response.headers),
                    # 添加CORS头
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
    
    except Exception as e:
        logger.error(f"Error proxying request to contract service: {str(e)}")
        # 构建错误响应
        return JSONResponse(
            content={
                "code": 500,
                "message": f"服务暂时不可用，请稍后再试。(错误: {str(e)[:100]})",
                "data": None
            },
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

