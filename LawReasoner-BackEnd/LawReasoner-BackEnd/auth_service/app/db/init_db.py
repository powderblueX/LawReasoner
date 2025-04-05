from sqlalchemy.orm import Session
from sqlalchemy import text

from app.crud.user import create_user, get_user_by_email
from app.schemas.user import UserCreate
from app.db.base import Base  # 从base.py导入Base
from app.db.session import engine, SessionLocal
from app.core.config import settings


# 创建表
def init_db(db: Session) -> None:
    """
    初始化数据库函数
    功能：
      1. 创建所有数据表
      2. 插入初始管理员用户（如果不存在）
    """
    # 确保数据表存在
    Base.metadata.create_all(bind=engine)
    print("✅ 数据表结构已创建/更新")

    # 使用新会话操作（确保事务隔离）
    new_db = SessionLocal()
    try:
        admin_email = "2784892686@qq.com"
        admin = get_user_by_email(new_db, email=admin_email)
        
        if not admin:
            user_in = UserCreate(
                email=admin_email,
                username="admin",
                password="Powderblue437",
                full_name="系统管理员",
                is_active=True,
            )
            admin_user = create_user(new_db, user_in)
            admin_user.is_superuser = True
            new_db.add(admin_user)
            new_db.commit()
            print("🆗 管理员用户创建成功")
        else:
            print("⏩ 管理员用户已存在")
    finally:
        new_db.close()