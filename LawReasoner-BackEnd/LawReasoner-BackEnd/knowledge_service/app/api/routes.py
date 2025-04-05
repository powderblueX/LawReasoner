from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api import deps
from app.db.session import get_db
from app.models.knowledge import LawArticle as LawArticleModel
from app.models.knowledge import CaseReference as CaseReferenceModel
from app.models.knowledge import LegalConcept as LegalConceptModel
from app.schemas.knowledge import (
    LawArticle, LawArticleCreate,
    CaseReference, CaseReferenceCreate,
    LegalConcept, LegalConceptCreate,
    KnowledgeQuery, SearchResult
)
from app.services.knowledge import (
    search_law_articles,
    search_case_references,
    search_legal_concepts,
    create_law_article_with_embedding,
    create_case_reference_with_embedding,
    create_legal_concept_with_embedding
)

api_router = APIRouter()


@api_router.post("/knowledge/query", response_model=SearchResult)
async def query_knowledge(
    query: KnowledgeQuery,
    db: Session = Depends(get_db)
):
    """查询知识库"""
    result = SearchResult()
    
    if query.type == "law_articles" or query.type == "all":
        result.law_articles = search_law_articles(db, query.query, limit=query.limit)
    
    if query.type == "similar_cases" or query.type == "all":
        result.similar_cases = search_case_references(db, query.query, limit=query.limit)
    
    if query.type == "legal_concepts" or query.type == "all":
        result.legal_concepts = search_legal_concepts(db, query.query, limit=query.limit)
    
    return result


@api_router.post("/law-articles/", response_model=LawArticle)
def create_law_article(
    law_article: LawArticleCreate,
    db: Session = Depends(get_db)
):
    """创建法条"""
    return create_law_article_with_embedding(db, law_article)


@api_router.get("/law-articles/", response_model=List[LawArticle])
def read_law_articles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有法条"""
    law_articles = db.query(LawArticleModel).offset(skip).limit(limit).all()
    return law_articles


@api_router.get("/law-articles/{article_id}", response_model=LawArticle)
def read_law_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """获取单个法条"""
    law_article = db.query(LawArticleModel).filter(LawArticleModel.id == article_id).first()
    if law_article is None:
        raise HTTPException(status_code=404, detail="法条不存在")
    return law_article


@api_router.post("/case-references/", response_model=CaseReference)
def create_case_reference(
    case_reference: CaseReferenceCreate,
    db: Session = Depends(get_db)
):
    """创建案例参考"""
    return create_case_reference_with_embedding(db, case_reference)


@api_router.get("/case-references/", response_model=List[CaseReference])
def read_case_references(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有案例参考"""
    case_references = db.query(CaseReferenceModel).offset(skip).limit(limit).all()
    return case_references


@api_router.get("/case-references/{case_ref_id}", response_model=CaseReference)
def read_case_reference(
    case_ref_id: int,
    db: Session = Depends(get_db)
):
    """获取单个案例参考"""
    case_reference = db.query(CaseReferenceModel).filter(CaseReferenceModel.id == case_ref_id).first()
    if case_reference is None:
        raise HTTPException(status_code=404, detail="案例参考不存在")
    return case_reference


@api_router.post("/legal-concepts/", response_model=LegalConcept)
def create_legal_concept(
    legal_concept: LegalConceptCreate,
    db: Session = Depends(get_db)
):
    """创建法律概念"""
    return create_legal_concept_with_embedding(db, legal_concept)


@api_router.get("/legal-concepts/", response_model=List[LegalConcept])
def read_legal_concepts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有法律概念"""
    legal_concepts = db.query(LegalConceptModel).offset(skip).limit(limit).all()
    return legal_concepts


@api_router.get("/legal-concepts/{concept_id}", response_model=LegalConcept)
def read_legal_concept(
    concept_id: int,
    db: Session = Depends(get_db)
):
    """获取单个法律概念"""
    legal_concept = db.query(LegalConceptModel).filter(LegalConceptModel.id == concept_id).first()
    if legal_concept is None:
        raise HTTPException(status_code=404, detail="法律概念不存在")
    return legal_concept 