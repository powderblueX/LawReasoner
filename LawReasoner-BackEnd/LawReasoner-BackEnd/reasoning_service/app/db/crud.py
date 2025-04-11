from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from app.models.chat import ChatSession, ChatMessage

def create_chat_session(db: Session, user_id: int, title: str = "新对话") -> ChatSession:
    """创建新的聊天会话"""
    db_session = ChatSession(user_id=user_id, title=title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_chat_session(db: Session, session_id: int) -> Optional[ChatSession]:
    """获取指定ID的聊天会话"""
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def get_user_chat_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ChatSession]:
    """获取用户的所有聊天会话，按更新时间降序排列"""
    return db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit).all()

def update_chat_session_title(db: Session, session_id: int, title: str) -> Optional[ChatSession]:
    """更新聊天会话标题"""
    db_session = get_chat_session(db, session_id)
    if db_session:
        db_session.title = title
        db_session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
    return db_session

def update_chat_session_time(db: Session, session_id: int) -> None:
    """更新聊天会话的时间戳"""
    db_session = get_chat_session(db, session_id)
    if db_session:
        db_session.updated_at = datetime.utcnow()
        db.commit()

def create_chat_message(
    db: Session, user_id: int, content: str, response: str = None, session_id: Optional[int] = None
) -> ChatMessage:
    """
    创建新的聊天消息
    如果未提供session_id，将自动创建新会话
    """
    # 如果没有提供会话ID，创建新会话
    if not session_id:
        # 以用户消息的前10个字符作为标题
        title = content[:10] if len(content) > 10 else content
        db_session = create_chat_session(db, user_id, title)
        session_id = db_session.id
    else:
        # 更新现有会话的时间戳
        update_chat_session_time(db, session_id)
    
    # 创建消息
    db_message = ChatMessage(
        session_id=session_id,
        user_id=user_id,
        content=content,
        response=response
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_messages(db: Session, session_id: int) -> List[ChatMessage]:
    """获取会话中的所有消息，按创建时间升序排列"""
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

def update_chat_message_response(db: Session, message_id: int, response: str) -> Optional[ChatMessage]:
    """更新聊天消息的回应"""
    db_message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if db_message:
        db_message.response = response
        db.commit()
        db.refresh(db_message)
    return db_message 