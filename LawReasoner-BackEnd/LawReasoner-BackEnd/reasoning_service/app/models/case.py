from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Case(Base):
    """案例模型"""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)  # 案例正文
    status = Column(String(50), default="draft")  # 状态：草稿、分析中、已分析等
    created_by = Column(Integer, nullable=False)  # 创建者用户ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联分析结果
    analysis_results = relationship("AnalysisResult", back_populates="case", cascade="all, delete-orphan")


class AnalysisResult(Base):
    """分析结果模型"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    result_type = Column(String(50))  # 分析类型：法条推荐、案例相似度、法律推理等
    content = Column(Text)  # 分析结果内容，JSON格式
    confidence = Column(Float)  # 置信度
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联案例
    case = relationship("Case", back_populates="analysis_results") 