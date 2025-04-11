from sqlalchemy.orm import Session
from ..models.chat import ChatSession, ChatMessage
from ..schemas.chat import ChatSessionListItem
from datetime import datetime
from sqlalchemy import desc
from typing import List, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chat_service")

class ChatService:
    """聊天服务"""
    
    @staticmethod
    def create_message(
        db: Session, 
        user_id: int, 
        content: str, 
        response: str, 
        session_id: Optional[str] = None
    ) -> Tuple[ChatMessage, bool]:
        """
        创建新消息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            content: 用户消息内容
            response: 模型响应内容
            session_id: 会话ID（如果为None则创建新会话）
            
        Returns:
            Tuple[ChatMessage, bool]: 消息对象和是否新创建会话的标志
        """
        is_new_session = False
        
        # 如果未提供会话ID，创建新会话
        if not session_id:
            # 使用消息内容前10个字符作为会话标题
            title = content[:10] if len(content) > 10 else content
            session = ChatSession.create_new(user_id=user_id, title=title)
            db.add(session)
            db.flush()
            session_id = session.id
            is_new_session = True
            logger.info(f"为用户 {user_id} 创建新会话: {session_id}")
        else:
            # 更新现有会话的时间戳
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).first()
            
            if not session:
                logger.warning(f"找不到会话 {session_id} 或用户无权访问，创建新会话")
                # 会话不存在或不属于该用户，创建新会话
                title = content[:10] if len(content) > 10 else content
                session = ChatSession.create_new(user_id=user_id, title=title)
                db.add(session)
                db.flush()
                session_id = session.id
                is_new_session = True
            else:
                session.updated_at = datetime.utcnow()
                
        # 创建消息
        message = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            content=content,
            response=response
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        logger.info(f"已为用户 {user_id} 在会话 {session_id} 中创建消息")
        return message, is_new_session
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: int) -> List[ChatSessionListItem]:
        """
        获取用户的所有会话
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            List[ChatSessionListItem]: 会话列表，按最后更新时间倒序排列
        """
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(desc(ChatSession.updated_at)).all()
        
        result = []
        for session in sessions:
            # 获取最后一条消息的时间
            last_message = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(desc(ChatMessage.created_at)).first()
            
            last_message_time = last_message.created_at if last_message else session.updated_at
            
            result.append(ChatSessionListItem(
                id=session.id,
                title=session.title,
                last_message_time=last_message_time
            ))
        
        logger.info(f"用户 {user_id} 获取到 {len(result)} 个会话")
        return result
    
    @staticmethod
    def get_session_messages(db: Session, session_id: str, user_id: int):
        """
        获取会话的所有消息
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            Tuple[ChatSession, List[ChatMessage]]: 会话和消息列表
        """
        # 检查会话是否存在且属于该用户
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
        
        if not session:
            logger.warning(f"找不到会话 {session_id} 或用户 {user_id} 无权访问")
            return None, []
        
        # 获取会话中的所有消息
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
        
        logger.info(f"用户 {user_id} 获取会话 {session_id} 的 {len(messages)} 条消息")
        return session, messages 