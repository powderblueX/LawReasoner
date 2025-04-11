from typing import Generator, Dict, Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging

# 导入共享认证库
import sys
import os
# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from common_db.auth_utils import decode_access_token

# 添加导入用户模型和查询函数
from app.db.session import get_db
from app.core.config import settings

# 尝试导入用户模型，如果不存在则使用简化版用户ID
try:
    from auth_service.app.models.user import User
    from auth_service.app.crud.user import get_user as auth_get_user
    HAS_USER_MODEL = True
except ImportError:
    HAS_USER_MODEL = False

# 配置日志
logger = logging.getLogger("api_deps")
logger.setLevel(logging.INFO)

# 使用OAuth2PasswordBearer认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")

def get_current_user_id(
    token: str = Depends(oauth2_scheme)
) -> int:
    """从令牌中获取当前用户ID"""
    try:
        # 添加调试日志
        logger.info(f"收到认证令牌: {token[:10]}...")
        
        # 使用共享认证库解析JWT令牌
        payload = decode_access_token(token)
        logger.info(f"解码后的令牌负载: {payload}")
        
        # 获取用户ID
        user_id: int = int(payload.get("sub"))
        if not user_id:
            raise ValueError("令牌中缺少用户ID")
        
        logger.info(f"成功获取用户ID: {user_id}")
        return user_id
    except Exception as e:
        logger.error(f"解析用户ID失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"无法验证凭据: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 添加与profile_service类似的get_current_user函数
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取当前用户或用户ID
    
    如果可以导入User模型，则返回完整的用户对象
    否则返回用户ID
    """
    try:
        # 使用共享认证库解析JWT令牌
        payload = decode_access_token(token)
        
        # 获取用户ID
        user_id: int = int(payload.get("sub"))
        if not user_id:
            raise ValueError("令牌中缺少用户ID")
        
        # 如果有用户模型，尝试获取用户对象
        if HAS_USER_MODEL:
            user = auth_get_user(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在",
                )
            return user
        else:
            # 如果没有用户模型，直接返回用户ID
            return user_id
            
    except Exception as e:
        logger.error(f"获取用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"无法验证凭据: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
