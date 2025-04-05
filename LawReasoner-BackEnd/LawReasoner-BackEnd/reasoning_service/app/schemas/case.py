from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class AnalysisResultBase(BaseModel):
    result_type: str
    content: str
    confidence: float


class AnalysisResultCreate(AnalysisResultBase):
    pass


class AnalysisResult(AnalysisResultBase):
    id: int
    case_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class CaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: str
    status: Optional[str] = "draft"


class CaseCreate(CaseBase):
    pass


class CaseUpdate(CaseBase):
    title: Optional[str] = None
    content: Optional[str] = None


class Case(CaseBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    analysis_results: List[AnalysisResult] = []

    class Config:
        orm_mode = True


class CaseAnalysisRequest(BaseModel):
    """分析请求模型"""
    case_id: int
    analysis_types: List[str] = ["law_recommendation", "similar_cases", "legal_reasoning"] 