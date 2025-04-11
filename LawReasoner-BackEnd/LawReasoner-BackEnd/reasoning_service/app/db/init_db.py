"""
初始化数据库表
"""
import logging
from common_db.db_utils import engine, Base

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")

def init_db():
    """初始化reasoning_service的数据库表"""
    logger.info("开始创建reasoning_service数据库表...")
    
    # 确保导入了所有模型，以便SQLAlchemy可以创建表
    # 导入必须放在函数内部，以避免循环导入
    from app.models.chat import ChatSession, ChatMessage
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    logger.info("数据库表创建完成")

if __name__ == "__main__":
    logger.info("初始化数据库...")
    init_db()
    logger.info("初始化完成。") 