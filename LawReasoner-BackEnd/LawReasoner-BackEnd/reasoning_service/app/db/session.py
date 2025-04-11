from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 导入共享的数据库工具
from common_db.db_utils import Base, engine, SessionLocal, get_db

# 注意：我们现在直接使用common_db中定义的Base、engine和SessionLocal
# 这样可以确保所有服务使用相同的数据库连接和模型定义

# 保留get_db函数的导入，但实际内容来自common_db
