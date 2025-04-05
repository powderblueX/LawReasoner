from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

# 导入共享认证库
import sys
import os
# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from common_db.auth_utils import decode_access_token

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.crud.user import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")

def get_db() -> Generator:
    """获取数据库会话"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """获取当前用户"""
    try:
        # 使用共享认证库解析JWT令牌
        payload = decode_access_token(token)
        
        # 获取用户ID
        user_id: int = int(payload.get("sub"))
        
        # 获取用户信息
        user = get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"无法验证凭据: {str(e)}",
        )
    
    return user 