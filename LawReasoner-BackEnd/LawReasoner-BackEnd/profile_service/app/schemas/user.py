from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    """用户基础模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class UserInfo(UserBase):
    """用户信息响应模型"""
    id: int
    register_date: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        orm_mode = True
        fields = {
            'created_at': 'register_date'
        }

class UserUpdate(UserBase):
    """用户信息更新模型"""
    pass

class PasswordUpdate(BaseModel):
    """密码更新模型"""
    current_password: str
    new_password: str

class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        orm_mode = True 