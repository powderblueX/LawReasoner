# 推理服务数据库表缺失问题及解决方案

## 问题描述

在启动推理服务时，当访问 `/api/v1/reasoning/sessions` 接口获取会话列表时，出现以下错误：

```
ERROR:chat_api:获取会话列表时发生错误: (sqlite3.OperationalError) no such table: chat_sessions
[SQL: SELECT chat_sessions.id AS chat_sessions_id, chat_sessions.user_id AS chat_sessions_user_id, 
chat_sessions.title AS chat_sessions_title, chat_sessions.created_at AS chat_sessions_created_at, 
chat_sessions.updated_at AS chat_sessions_updated_at FROM chat_sessions
WHERE chat_sessions.user_id = ? ORDER BY chat_sessions.updated_at DESC LIMIT ? OFFSET ?]
[parameters: (1, 100, 0)]
(Background on this error at: https://sqlalche.me/e/20/e3q8)
```

这表明数据库中缺少必要的 `chat_sessions` 表。

## 原因分析

1. 系统中存在多个 `Base` 定义和数据库连接逻辑，导致表创建可能在不同的数据库文件中进行：
   - `common_db/db_utils.py` 中定义了一个 `Base`
   - `reasoning_service/app/db/session.py` 中也定义了一个 `Base`

2. 初始化数据库表的代码没有正确执行，或者使用了错误的 `Base` 对象。

## 解决方案

### 1. 统一使用 common_db 中的 Base 和数据库连接

修改 `reasoning_service/app/db/session.py`：

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 导入共享的数据库工具
from common_db.db_utils import Base, engine, SessionLocal, get_db

# 注意：我们现在直接使用common_db中定义的Base、engine和SessionLocal
# 这样可以确保所有服务使用相同的数据库连接和模型定义
```

### 2. 更新数据库初始化代码

修改 `reasoning_service/app/db/init_db.py`：

```python
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
```

### 3. 在应用启动时确保调用初始化函数

修改 `reasoning_service/main.py`：

```python
# 将原来的代码
Base.metadata.create_all(bind=engine)
print("数据库表已更新")

# 替换为
init_db()
print("数据库表已初始化")
```

### 4. 创建独立的数据库初始化脚本

创建 `reasoning_service/init_database.py`：

```python
"""
手动初始化reasoning_service所需的数据库表
运行方式: python reasoning_service/init_database.py
"""
import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_database")

# 添加项目根目录到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(project_root)

# 导入所需的模块
from common_db.db_utils import engine, Base
from reasoning_service.app.models.chat import ChatSession, ChatMessage

def init_database():
    """初始化reasoning_service所需的数据库表"""
    logger.info("开始初始化reasoning_service数据库表...")
    
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    logger.info("数据库表创建完成")
    
    # 验证表是否创建成功
    from sqlalchemy import inspect
    inspector = inspect(engine)
    
    if "chat_sessions" in inspector.get_table_names():
        logger.info("成功: chat_sessions表已创建")
    else:
        logger.error("错误: chat_sessions表创建失败")
        
    if "chat_messages" in inspector.get_table_names():
        logger.info("成功: chat_messages表已创建")
    else:
        logger.error("错误: chat_messages表创建失败")

if __name__ == "__main__":
    logger.info("开始手动初始化数据库...")
    init_database()
    logger.info("初始化完成。")
```

### 5. 验证修复结果

手动运行初始化脚本后，数据库中已正确创建了 `chat_sessions` 和 `chat_messages` 表。使用以下命令查看数据库表结构：

```bash
sqlite3 common_db/shared_db.db .tables
```

```
chat_messages  chat_sessions  users
```

```bash
sqlite3 common_db/shared_db.db ".schema chat_sessions"
```

```sql
CREATE TABLE chat_sessions (
        id INTEGER NOT NULL,
        user_id INTEGER,
        title VARCHAR(255) NOT NULL,
        created_at DATETIME,
        updated_at DATETIME,
        PRIMARY KEY (id)
);
CREATE INDEX ix_chat_sessions_user_id ON chat_sessions (user_id);
CREATE INDEX ix_chat_sessions_id ON chat_sessions (id);
```

## 启动所有服务的脚本

为了方便同时启动所有服务，创建了 `start_all_services.py` 脚本，它会同时启动认证服务、用户资料服务和推理服务，并自动初始化数据库。

使用方法：

```bash
python start_all_services.py
```

## 问题总结

1. 确保所有微服务使用同一个共享的数据库连接和模型基类（Base）
2. 在初始化时确保正确导入和创建所有模型对应的表
3. 创建独立的数据库初始化脚本，便于手动执行和调试
4. 在服务启动时确保数据库表已正确创建 