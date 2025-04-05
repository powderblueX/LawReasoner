from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base

# 导入所有模型以确保它们被注册到Base.metadata
# 注意：这一行必须在创建引擎之前，保证所有表都被加载
from app.models.user import User

# 创建SQLAlchemy引擎
engine = create_engine(
    settings.SQLITE_DATABASE_URI, # 从配置读取数据库URL
    connect_args={"check_same_thread": False}, # SQLite多线程支持
    echo=True  # 显示所有SQL语句
)

# 创建本地会话
SessionLocal = sessionmaker(
    autocommit=False, # 关闭自动提交
    autoflush=False, # 关闭自动flush
    bind=engine # 绑定到引擎
)
