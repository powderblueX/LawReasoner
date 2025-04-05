from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class LawArticleBase(BaseModel):
    law_name: str
    article_number: str
    content: str
    category: Optional[str] = None


class LawArticleCreate(LawArticleBase):
    pass


class LawArticle(LawArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CaseReferenceBase(BaseModel):
    title: str
    case_number: str
    court: Optional[str] = None
    content: str
    judgment: Optional[str] = None
    category: Optional[str] = None


class CaseReferenceCreate(CaseReferenceBase):
    pass


class CaseReference(CaseReferenceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LegalConceptBase(BaseModel):
    name: str
    definition: str
    related_laws: Optional[str] = None
    examples: Optional[str] = None


class LegalConceptCreate(LegalConceptBase):
    pass


class LegalConcept(LegalConceptBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class KnowledgeQuery(BaseModel):
    """知识查询请求"""
    query: str
    type: str  # 查询类型：law_articles, similar_cases, legal_concepts, all
    limit: Optional[int] = 10


class SearchResult(BaseModel):
    """搜索结果"""
    law_articles: Optional[List[LawArticle]] = []
    similar_cases: Optional[List[CaseReference]] = []
    legal_concepts: Optional[List[LegalConcept]] = [] 