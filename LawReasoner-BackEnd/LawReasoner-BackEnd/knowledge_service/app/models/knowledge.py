from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class LawArticle(Base):
    """法条信息"""
    __tablename__ = "law_articles"

    id = Column(Integer, primary_key=True, index=True)
    law_name = Column(String(255), index=True, nullable=False)  # 法律名称
    article_number = Column(String(50), index=True, nullable=False)  # 条款编号
    content = Column(Text, nullable=False)  # 条款内容
    category = Column(String(100), index=True)  # 分类
    embedding = Column(LargeBinary, nullable=True)  # 向量嵌入
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CaseReference(Base):
    """案例参考"""
    __tablename__ = "case_references"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)  # 案例标题
    case_number = Column(String(100), index=True, nullable=False)  # 案号
    court = Column(String(100), index=True)  # 法院
    content = Column(Text, nullable=False)  # 案例内容
    judgment = Column(Text)  # 裁判结果
    category = Column(String(100), index=True)  # 分类
    embedding = Column(LargeBinary, nullable=True)  # 向量嵌入
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LegalConcept(Base):
    """法律概念"""
    __tablename__ = "legal_concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False, unique=True)  # 概念名称
    definition = Column(Text, nullable=False)  # 定义
    related_laws = Column(Text)  # 相关法条
    examples = Column(Text)  # 实例说明
    embedding = Column(LargeBinary, nullable=True)  # 向量嵌入
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 