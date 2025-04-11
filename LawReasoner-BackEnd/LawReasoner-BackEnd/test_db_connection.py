"""
测试数据库连接和初始化
用法: python test_db_connection.py
"""
import os
import sys
import logging
from sqlalchemy import inspect

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_db")

def main():
    """测试数据库连接和初始化"""
    logger.info("=== 开始测试数据库连接 ===")
    
    # 1. 检查common_db目录
    common_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "common_db")
    logger.info(f"检查common_db目录: {common_db_path}")
    
    if not os.path.exists(common_db_path):
        logger.error(f"错误: common_db目录不存在! 正在创建...")
        os.makedirs(common_db_path, exist_ok=True)
        logger.info(f"已创建common_db目录: {common_db_path}")
    else:
        logger.info("common_db目录存在")
    
    # 2. 导入数据库工具
    try:
        # 确保common_db包可以被导入
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from common_db.db_utils import engine, Base, init_db
        
        logger.info("成功导入数据库工具")
        
        # 3. 测试数据库连接
        try:
            # 检查数据库连接
            connection = engine.connect()
            logger.info("数据库连接成功!")
            connection.close()
            
            # 4. 初始化数据库
            init_db()
            
            # 5. 检查表是否创建
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"数据库中的表: {tables}")
            
            return True
            
        except Exception as e:
            logger.error(f"数据库连接或初始化失败: {str(e)}")
            return False
            
    except ImportError as e:
        logger.error(f"导入数据库工具失败: {str(e)}")
        return False

if __name__ == "__main__":
    if main():
        logger.info("=== 数据库连接测试成功 ===")
        sys.exit(0)
    else:
        logger.error("=== 数据库连接测试失败 ===")
        sys.exit(1) 