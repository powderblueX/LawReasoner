from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# 密码哈希上下文配置（与 config.py 中的算法配置联动）
pwd_context = CryptContext(schemes=[settings.PASSWORD_HASHING_ALGORITHM], # 使用的哈希算法
                           deprecated="auto" # 自动标记旧算法为弃用
                           )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希值是否匹配
    参数：
      - plain_password: 用户输入的明文密码
      - hashed_password: 数据库存储的哈希值
    返回：验证结果（True/False）
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希值
    用途：用户注册或修改密码时调用
    示例：get_password_hash("123456") -> "$2b$12$xxxx..."
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """生成 JWT 访问令牌
    参数：
      - subject: 令牌主题（通常为用户唯一标识）
      - expires_delta: 自定义有效期（默认使用配置中的时间）
    返回：编码后的 JWT 字符串
    """
    # 计算过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # 构建 JWT 负载（Payload）
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # 编码令牌（使用配置中的密钥和算法）
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt 