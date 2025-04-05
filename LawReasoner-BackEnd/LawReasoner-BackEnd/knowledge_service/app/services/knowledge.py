import numpy as np
import pickle
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.config import settings
from app.models.knowledge import LawArticle, CaseReference, LegalConcept
from app.schemas.knowledge import (
    LawArticleCreate,
    CaseReferenceCreate,
    LegalConceptCreate
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入sentence_transformers，如果不存在则提供mock实现
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    
    def get_embedding(text: str) -> bytes:
        """获取文本的向量嵌入"""
        embedding = model.encode(text)
        return pickle.dumps(embedding)
    
    def compare_embeddings(embedding1: bytes, embedding2: bytes) -> float:
        """比较两个嵌入向量的相似度"""
        vec1 = pickle.loads(embedding1)
        vec2 = pickle.loads(embedding2)
        # 计算余弦相似度
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
    
except ImportError:
    logger.warning("sentence_transformers未安装，使用模拟嵌入")
    
    def get_embedding(text: str) -> bytes:
        """模拟嵌入函数"""
        # 返回一个随机向量作为模拟嵌入
        mock_embedding = np.random.rand(settings.EMBEDDING_DIMENSION)
        return pickle.dumps(mock_embedding)
    
    def compare_embeddings(embedding1: bytes, embedding2: bytes) -> float:
        """模拟相似度比较函数"""
        # 返回一个0.3到0.9之间的随机相似度
        return 0.3 + np.random.random() * 0.6


def create_law_article_with_embedding(db: Session, law_article_in: LawArticleCreate) -> LawArticle:
    """创建法条并生成嵌入向量"""
    embedding = get_embedding(law_article_in.content)
    
    db_law_article = LawArticle(
        **law_article_in.dict(),
        embedding=embedding
    )
    db.add(db_law_article)
    db.commit()
    db.refresh(db_law_article)
    return db_law_article


def create_case_reference_with_embedding(db: Session, case_reference_in: CaseReferenceCreate) -> CaseReference:
    """创建案例参考并生成嵌入向量"""
    # 结合标题和内容生成更好的嵌入
    embedding_text = f"{case_reference_in.title}. {case_reference_in.content[:1000]}"
    embedding = get_embedding(embedding_text)
    
    db_case_reference = CaseReference(
        **case_reference_in.dict(),
        embedding=embedding
    )
    db.add(db_case_reference)
    db.commit()
    db.refresh(db_case_reference)
    return db_case_reference


def create_legal_concept_with_embedding(db: Session, legal_concept_in: LegalConceptCreate) -> LegalConcept:
    """创建法律概念并生成嵌入向量"""
    # 结合名称和定义生成嵌入
    embedding_text = f"{legal_concept_in.name}: {legal_concept_in.definition}"
    embedding = get_embedding(embedding_text)
    
    db_legal_concept = LegalConcept(
        **legal_concept_in.dict(),
        embedding=embedding
    )
    db.add(db_legal_concept)
    db.commit()
    db.refresh(db_legal_concept)
    return db_legal_concept


def search_law_articles(db: Session, query: str, limit: int = 10) -> List[LawArticle]:
    """搜索相关法条"""
    query_embedding = get_embedding(query)
    
    # 获取所有法条
    all_law_articles = db.query(LawArticle).all()
    
    # 计算相似度并排序
    results_with_scores = []
    for article in all_law_articles:
        if article.embedding:
            similarity = compare_embeddings(query_embedding, article.embedding)
            results_with_scores.append((article, similarity))
    
    # 按相似度降序排序
    results_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 返回前limit个结果
    return [article for article, _ in results_with_scores[:limit]]


def search_case_references(db: Session, query: str, limit: int = 10) -> List[CaseReference]:
    """搜索相关案例"""
    query_embedding = get_embedding(query)
    
    # 获取所有案例
    all_cases = db.query(CaseReference).all()
    
    # 计算相似度并排序
    results_with_scores = []
    for case in all_cases:
        if case.embedding:
            similarity = compare_embeddings(query_embedding, case.embedding)
            results_with_scores.append((case, similarity))
    
    # 按相似度降序排序
    results_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 返回前limit个结果
    return [case for case, _ in results_with_scores[:limit]]


def search_legal_concepts(db: Session, query: str, limit: int = 10) -> List[LegalConcept]:
    """搜索相关法律概念"""
    query_embedding = get_embedding(query)
    
    # 获取所有法律概念
    all_concepts = db.query(LegalConcept).all()
    
    # 计算相似度并排序
    results_with_scores = []
    for concept in all_concepts:
        if concept.embedding:
            similarity = compare_embeddings(query_embedding, concept.embedding)
            results_with_scores.append((concept, similarity))
    
    # 按相似度降序排序
    results_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 返回前limit个结果
    return [concept for concept, _ in results_with_scores[:limit]] 