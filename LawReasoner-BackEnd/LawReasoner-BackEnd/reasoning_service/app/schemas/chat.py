from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime

# 请求模型
class ChatRequest(BaseModel):
    """聊天请求模型"""
    content: str
    session_id: Optional[int] = None


# 响应模型
class ChatMessage(BaseModel):
    """聊天消息"""
    id: int
    content: str
    response: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSession(BaseModel):
    """聊天会话"""
    id: int
    title: str
    updated_at: datetime
    last_message: Optional[str] = None

    class Config:
        from_attributes = True


class ChatHistory(BaseModel):
    """聊天历史"""
    code: int = 200
    message: str = "成功获取会话消息"
    data: Optional[Any] = None
    messages: List[ChatMessage]

    class Config:
        from_attributes = True


class ChatSessionList(BaseModel):
    """聊天会话列表"""
    code: int = 200
    message: str = "成功获取会话列表"
    data: Optional[Dict] = None
    sessions: List[ChatSession]

    class Config:
        from_attributes = True

    @property
    def response_dict(self):
        """返回包含完整结构的响应字典"""
        return {
            "code": self.code,
            "message": self.message,
            "data": {
                "sessions": [session.dict() for session in self.sessions]
            }
        }


# 通用API响应模型
class ApiResponse(BaseModel):
    """通用API响应模型"""
    code: int = 200
    message: str = "操作成功"
    data: Optional[Any] = None

    class Config:
        from_attributes = True


# 更新标题请求模型
class UpdateTitleRequest(BaseModel):
    """更新会话标题请求模型"""
    title: str 