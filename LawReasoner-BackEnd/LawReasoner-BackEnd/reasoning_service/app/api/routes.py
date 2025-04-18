from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import asyncio
import hashlib

from app.db.session import get_db
from app.api.deps import get_current_user_id
from app.schemas.chat import ChatRequest, ChatSession, ChatMessage, ChatHistory, ChatSessionList, ApiResponse, UpdateTitleRequest
from app.db.crud import (
    create_chat_session, get_chat_session, get_user_chat_sessions,
    create_chat_message, get_chat_messages, update_chat_message_response,
    update_chat_session_title
)
from app.services.llm_service import llm_service

# 创建路由
router = APIRouter()

# 配置日志
logger = logging.getLogger("chat_api")
logger.setLevel(logging.INFO)

# 活跃请求缓存
active_requests = {}
active_requests_lock = asyncio.Lock()

# 用户请求计数器，用于节流
user_request_counters = {}
user_request_lock = asyncio.Lock()

# 后台任务：更新消息的回复
async def process_model_response(db: Session, message_id: int, user_input: str):
    """处理模型响应并更新数据库"""
    try:
        # 调用大模型生成回复
        response = await llm_service.generate_response(user_input)
        
        # 更新数据库中的消息响应
        update_chat_message_response(db, message_id, response)
        logger.info(f"已更新消息ID {message_id} 的响应")
    except Exception as e:
        logger.error(f"处理模型响应时发生错误: {str(e)}")
        # 更新为错误消息
        error_message = f"生成回复时发生错误: {str(e)}"
        update_chat_message_response(db, message_id, error_message)

# 生成请求指纹，用于去重
def generate_request_fingerprint(user_id: int, content: str) -> str:
    """根据用户ID和请求内容生成唯一请求指纹"""
    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
    return f"{user_id}:{content_hash}"

@router.post("/chat", status_code=status.HTTP_200_OK)
async def send_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    发送消息给大模型并获取响应
    
    将消息存储到数据库，同时在后台处理模型响应
    """
    # 生成请求指纹
    request_fingerprint = generate_request_fingerprint(current_user_id, request.content)
    logger.info(f"用户 {current_user_id} 发送消息: {request.content[:50]}..., 指纹: {request_fingerprint}")
    
    # 检查是否存在相同的请求正在处理中
    async with active_requests_lock:
        if request_fingerprint in active_requests:
            cached_response = active_requests[request_fingerprint]
            logger.info(f"发现重复请求，返回缓存结果 - 指纹: {request_fingerprint}")
            return cached_response
    
    try:
        # 创建消息记录，不含响应
        db_message = create_chat_message(
            db=db,
            user_id=current_user_id,
            content=request.content,
            session_id=request.session_id
        )
        
        # 获取会话ID（可能是新创建的）
        session_id = db_message.session_id
        logger.info(f"已创建消息记录，ID: {db_message.id}, 会话ID: {session_id}")
        
        # 尝试获取模型响应
        try:
            # 将此请求标记为处理中
            async with active_requests_lock:
                # 先添加一个临时响应，表示正在处理
                active_requests[request_fingerprint] = {
                    "code": 202,
                    "message": "请求处理中",
                    "data": {
                        "status": "processing",
                        "session_id": session_id
                    }
                }
            
            # 同步获取响应，而不是在后台任务中处理
            logger.info(f"开始请求LLM生成回复... 指纹: {request_fingerprint}")
            response = await llm_service.generate_response(request.content)
            logger.info(f"成功获取模型回复，长度: {len(response)}, 指纹: {request_fingerprint}")
            
            # 记录部分响应内容以便调试
            logger.info(f"模型回复内容片段: {response[:100]}...")
            
            # 更新消息响应
            update_chat_message_response(db, db_message.id, response)
            logger.info(f"已更新消息ID {db_message.id} 的响应")
            
            # 返回标准格式的成功响应
            response_obj = {
                "code": 200,
                "message": "成功获取回复",
                "data": {
                    "response": response,
                    "session_id": session_id  # 确保此字段一定存在
                }
            }
            
            # 更新请求缓存
            async with active_requests_lock:
                active_requests[request_fingerprint] = response_obj
                
                # 设置清理定时器，10分钟后清理缓存
                async def cleanup_request():
                    await asyncio.sleep(600)  # 10分钟
                    async with active_requests_lock:
                        if request_fingerprint in active_requests:
                            del active_requests[request_fingerprint]
                            logger.info(f"请求缓存已清理 - 指纹: {request_fingerprint}")
                
                # 启动清理任务
                asyncio.create_task(cleanup_request())
            
            # 打印完整的响应对象，帮助调试
            logger.info(f"返回成功响应，包含session_id: {session_id}")
            return response_obj
            
        except Exception as model_error:
            # 模型调用错误，记录日志并返回错误信息
            error_message = f"模型生成失败: {str(model_error)}"
            logger.error(error_message, exc_info=True)
            
            # 仍然更新消息记录，但存储错误信息
            error_response = f"[错误] {error_message}"
            update_chat_message_response(db, db_message.id, error_response)
            logger.info(f"已更新消息ID {db_message.id} 的错误响应")
            
            # 返回标准格式的错误响应
            error_response_obj = {
                "code": 500,
                "message": "模型生成失败",
                "data": {
                    "response": "很抱歉，模型暂时无法处理您的请求，请稍后再试。",
                    "session_id": session_id,
                    "detail": str(model_error)
                }
            }
            
            # 更新请求缓存
            async with active_requests_lock:
                # 保存错误响应，但设置较短的缓存时间
                active_requests[request_fingerprint] = error_response_obj
                
                # 设置清理定时器，1分钟后清理错误缓存
                async def cleanup_error_request():
                    await asyncio.sleep(60)  # 1分钟
                    async with active_requests_lock:
                        if request_fingerprint in active_requests:
                            del active_requests[request_fingerprint]
                            logger.info(f"错误请求缓存已清理 - 指纹: {request_fingerprint}")
                
                # 启动清理任务
                asyncio.create_task(cleanup_error_request())
            
            logger.info(f"返回错误响应，结构: {error_response_obj}")
            return error_response_obj
    
    except Exception as e:
        logger.error(f"处理消息时发生错误: {str(e)}", exc_info=True)
        
        # 返回标准格式的错误响应
        error_obj = {
            "code": 500,
            "message": f"处理消息失败: {str(e)}",
            "data": {
                "response": "服务器处理请求时发生错误，请稍后再试。",
                "detail": str(e)
            }
        }
        
        return error_obj

@router.get("/sessions", response_model=ChatSessionList)
async def get_sessions(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取用户的会话列表"""
    logger.info(f"用户 {current_user_id} 请求会话列表")
    
    try:
        # 获取会话列表
        db_sessions = get_user_chat_sessions(db, current_user_id)

        # 转换为响应格式
        sessions = []
        for session in db_sessions:
            # 获取最后一条消息作为预览
            messages = get_chat_messages(db, session.id)
            last_message = None
            if messages:
                last_message = messages[-1].content[:20] + "..." if len(messages[-1].content) > 20 else messages[-1].content
            
            sessions.append(ChatSession(
                id=session.id,
                title=session.title,
                updated_at=session.updated_at,
                last_message=last_message
            ))
        
        # 直接返回ChatSessionList对象，而不是字典
        return ChatSessionList(sessions=sessions)
    
    except Exception as e:
        logger.error(f"获取会话列表时发生错误: {str(e)}")
        # 修复：确保正确初始化ChatSessionList对象
        return ChatSessionList(
            code=500,
            message=f"获取会话列表失败: {str(e)}",
            sessions=[],  # 始终返回空列表而不是null
            data={"error": str(e)}  # 添加data字段
        )

@router.get("/sessions/{session_id}/messages", response_model=ChatHistory)
async def get_session_messages(
    session_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取会话中的所有消息"""
    logger.info(f"用户 {current_user_id} 请求会话 {session_id} 的消息")
    
    try:
        # 检查会话是否存在且属于当前用户
        session = get_chat_session(db, session_id)
        if not session or session.user_id != current_user_id:
            # 使用ChatHistory模型确保一致的返回结构
            return ChatHistory(
                code=404,
                message="会话不存在或无权访问",
                data={"error": "Not found or no permission"},
                messages=[]  # 返回空列表而不是null
            )
        
        # 获取会话中的所有消息
        db_messages = get_chat_messages(db, session_id)
        
        # 转换为响应格式
        messages = [
            ChatMessage(
                id=msg.id,
                content=msg.content,
                response=msg.response,
                created_at=msg.created_at
            )
            for msg in db_messages
        ]
        
        return ChatHistory(messages=messages)
    
    except Exception as e:
        logger.error(f"获取会话消息时发生错误: {str(e)}")
        print(f"获取会话消息时发生错误: {str(e)}")
        # 使用标准响应格式而不是HTTP异常
        # 关键：确保返回的结构与ChatHistory模型一致，即使有错误也包含messages字段
        return ChatHistory(
            code=500,
            message=f"获取会话消息失败: {str(e)}",
            data={"error": str(e)},
            messages=[]  # 始终返回空列表而不是null
        )

@router.get("/sessions/{session_id}/delete", response_model=ApiResponse)
async def delete_session(
    session_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """删除指定会话及其所有消息"""
    logger.info(f"用户 {current_user_id} 请求删除会话 {session_id}")
    
    try:
        # 检查会话是否存在且属于当前用户
        session = get_chat_session(db, session_id)
        if not session:
            return ApiResponse(
                code=404,
                message="会话不存在"
            )
        
        if session.user_id != current_user_id:
            return ApiResponse(
                code=403,
                message="无权删除此会话"
            )
        
        # 删除会话(级联删除所有消息)
        db.delete(session)
        db.commit()
        
        return ApiResponse(
            message="会话已成功删除"
        )
    
    except Exception as e:
        logger.error(f"删除会话时发生错误: {str(e)}")
        return ApiResponse(
            code=500,
            message=f"删除会话失败: {str(e)}"
        )

@router.get("/sessions/{session_id}/clear", response_model=ApiResponse)
async def clear_session_messages(
    session_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """清空指定会话的所有消息，但保留会话本身"""
    logger.info(f"用户 {current_user_id} 请求清空会话 {session_id} 的消息")
    
    try:
        # 检查会话是否存在且属于当前用户
        session = get_chat_session(db, session_id)
        if not session:
            return ApiResponse(
                code=404,
                message="会话不存在"
            )
        
        if session.user_id != current_user_id:
            return ApiResponse(
                code=403,
                message="无权清空此会话"
            )
        
        # 删除会话中的所有消息
        for message in session.messages:
            db.delete(message)
        
        # 更新会话标题
        session.title = "新会话"
        session.updated_at = datetime.utcnow()
        
        db.commit()
        
        return ApiResponse(
            message="会话消息已成功清空"
        )
    
    except Exception as e:
        logger.error(f"清空会话消息时发生错误: {str(e)}")
        return ApiResponse(
            code=500,
            message=f"清空会话消息失败: {str(e)}"
        )

@router.post("/sessions/{session_id}/title", response_model=ApiResponse)
async def update_session_title(
    session_id: int,
    request: UpdateTitleRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新会话标题"""
    logger.info(f"用户 {current_user_id} 请求更新会话 {session_id} 的标题为 '{request.title}'")
    
    try:
        # 检查会话是否存在且属于当前用户
        session = get_chat_session(db, session_id)
        if not session:
            return ApiResponse(
                code=404,
                message="会话不存在"
            )
        
        if session.user_id != current_user_id:
            return ApiResponse(
                code=403,
                message="无权修改此会话"
            )
        
        # 更新标题
        updated_session = update_chat_session_title(db, session_id, request.title)
        
        if updated_session:
            return ApiResponse(
                message="会话标题已成功更新"
            )
        else:
            return ApiResponse(
                code=500,
                message="更新会话标题失败"
            )
    
    except Exception as e:
        logger.error(f"更新会话标题时发生错误: {str(e)}")
        return ApiResponse(
            code=500,
            message=f"更新会话标题失败: {str(e)}"
        )
