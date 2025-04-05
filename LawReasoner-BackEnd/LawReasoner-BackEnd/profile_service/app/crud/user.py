from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import verify_password, get_password_hash
from app.models.user import User
from app.schemas.user import UserUpdate, PasswordUpdate

def get_user(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()

def update_user_info(db: Session, user: User, user_in: UserUpdate) -> Optional[User]:
    """更新用户基本信息"""
    update_data = user_in.dict(exclude_unset=True)
    
    # 检查用户名是否已存在
    if "username" in update_data and update_data["username"] != user.username:
        if get_user_by_username(db, update_data["username"]):
            return None
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_password(db: Session, user: User, password_in: PasswordUpdate) -> bool:
    """更新用户密码"""
    if not verify_password(password_in.current_password, user.hashed_password):
        return False
    
    user.hashed_password = get_password_hash(password_in.new_password)
    db.add(user)
    db.commit()
    return True 