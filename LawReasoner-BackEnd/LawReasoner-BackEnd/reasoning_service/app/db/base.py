# 从session导入Base
from app.db.session import Base
 
# 导入所有模型，以确保Alembic可以创建迁移
from app.models.chat import ChatSession, ChatMessage 