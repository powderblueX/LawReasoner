from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from common_db.db_utils import Base

class ChatSession(Base):
    """聊天会话模型"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String(255), nullable=False, default="新对话")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系：一个会话有多个消息
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), index=True)
    user_id = Column(Integer, index=True)
    content = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系：一个消息属于一个会话
    session = relationship("ChatSession", back_populates="messages") 