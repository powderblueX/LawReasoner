from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import datetime

from app.api import deps
from app.crud.user import get_user, update_user_info, update_user_password
from app.models.user import User
from app.schemas.user import UserInfo, UserUpdate, PasswordUpdate

api_router = APIRouter()

@api_router.get("/profile/info")
async def get_user_info(
    current_user: User = Depends(deps.get_current_user)
):
    """获取用户个人信息
    安全逻辑：
      - 通过JWT令牌自动验证用户身份
      - 仅返回已登录用户自身信息
    错误处理：
      - 认证失败：由deps.get_current_user抛出HTTP异常
    """
    try:
        # 转换为字典并格式化字段
        user_data = {
            "username": current_user.username,
            "email": current_user.email,
            "register_date": current_user.created_at.isoformat() if hasattr(current_user, 'created_at') and current_user.created_at else datetime.datetime.now().isoformat(),
            "role": "user"
        }
        
        return {
            "code": 200,
            "message": "获取用户信息成功",
            "data": user_data
        }
    except Exception as e:
        return {
            "code": 500,
            "message": "获取用户信息失败"
        }

@api_router.post("/profile/update")
async def update_profile(
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """更新用户基本信息"""
    updated_user = update_user_info(db, current_user, user_in)
    if not updated_user:
        return {
            "code": 409,
            "message": "用户名已存在，请重新输入"
        }
    
    # 格式化响应数据
    user_data = {
        "username": updated_user.username,
        "email": updated_user.email,
        "register_date": updated_user.created_at.isoformat() if hasattr(updated_user, 'created_at') and updated_user.created_at else datetime.datetime.now().isoformat(),
        "role": "user"
    }
    
    return {
        "code": 200,
        "message": "账户信息已更新",
        "data": user_data
    }

@api_router.post("/profile/password")
async def update_password(
    password_in: PasswordUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """更新用户密码"""
    if not update_user_password(db, current_user, password_in):
        # 返回更明确的错误信息和自定义错误代码
        return {
            "code": 400,
            "message": "当前密码不正确，请重新输入"
        }
    return {
        "code": 200,
        "message": "密码更新成功"
    }

@api_router.post("/logout")
async def logout():
    """退出登录"""
    return {
        "code": 200,
        "message": "退出成功"
    } 