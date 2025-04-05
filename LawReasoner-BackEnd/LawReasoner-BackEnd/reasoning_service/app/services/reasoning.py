import json
import httpx
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from app.core.config import settings
from app.models.case import Case, AnalysisResult

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_knowledge_from_service(query: str, knowledge_type: str) -> Dict[str, Any]:
    """从知识库服务获取知识"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.KNOWLEDGE_SERVICE_URL}/api/v1/knowledge/query",
                json={"query": query, "type": knowledge_type}
            )
            return response.json()
    except Exception as e:
        logger.error(f"从知识库服务获取知识时出错: {e}")
        return {"error": str(e)}


async def analyze_case(db: Session, case_id: int, analysis_types: List[str]) -> None:
    """分析案例（异步后台任务）"""
    try:
        # 获取案例
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            logger.error(f"案例不存在，ID: {case_id}")
            return
        
        # 执行各种分析
        for analysis_type in analysis_types:
            if analysis_type == "law_recommendation":
                await analyze_law_recommendation(db, case)
            elif analysis_type == "similar_cases":
                await analyze_similar_cases(db, case)
            elif analysis_type == "legal_reasoning":
                await analyze_legal_reasoning(db, case)
        
        # 更新案例状态为已完成
        case.status = "analyzed"
        db.add(case)
        db.commit()
        
    except Exception as e:
        logger.error(f"分析案例时发生错误: {e}")
        # 更新案例状态为错误
        case = db.query(Case).filter(Case.id == case_id).first()
        if case:
            case.status = "error"
            db.add(case)
            db.commit()


async def analyze_law_recommendation(db: Session, case: Case) -> None:
    """法条推荐分析"""
    try:
        # 从知识库服务获取相关法条
        knowledge_response = await get_knowledge_from_service(
            query=case.content,
            knowledge_type="law_articles"
        )
        
        # 创建分析结果
        result = AnalysisResult(
            case_id=case.id,
            result_type="law_recommendation",
            content=json.dumps(knowledge_response, ensure_ascii=False),
            confidence=0.85  # 示例置信度
        )
        
        db.add(result)
        db.commit()
        
    except Exception as e:
        logger.error(f"法条推荐分析出错: {e}")
        raise


async def analyze_similar_cases(db: Session, case: Case) -> None:
    """相似案例分析"""
    try:
        # 从知识库服务获取相似案例
        knowledge_response = await get_knowledge_from_service(
            query=case.content,
            knowledge_type="similar_cases"
        )
        
        # 创建分析结果
        result = AnalysisResult(
            case_id=case.id,
            result_type="similar_cases",
            content=json.dumps(knowledge_response, ensure_ascii=False),
            confidence=0.80  # 示例置信度
        )
        
        db.add(result)
        db.commit()
        
    except Exception as e:
        logger.error(f"相似案例分析出错: {e}")
        raise


async def analyze_legal_reasoning(db: Session, case: Case) -> None:
    """法律推理分析"""
    try:
        # 模拟法律推理过程
        # 在实际应用中，这里可能需要更复杂的推理引擎
        reasoning_result = {
            "facts": extract_facts(case.content),
            "applicable_laws": ["《中华人民共和国民法典》第X条", "《中华人民共和国合同法》第Y条"],
            "reasoning_steps": [
                "基于案件事实，当事人之间存在合同关系",
                "根据《合同法》相关规定，当事人应当履行合同义务",
                "当事人一方未履行义务，构成违约"
            ],
            "conclusion": "被告应当承担违约责任，赔偿原告经济损失"
        }
        
        # 创建分析结果
        result = AnalysisResult(
            case_id=case.id,
            result_type="legal_reasoning",
            content=json.dumps(reasoning_result, ensure_ascii=False),
            confidence=0.75  # 示例置信度
        )
        
        db.add(result)
        db.commit()
        
    except Exception as e:
        logger.error(f"法律推理分析出错: {e}")
        raise


def extract_facts(case_content: str) -> List[str]:
    """从案例内容中提取事实（简化版）"""
    # 这里是一个简化的事实提取逻辑，实际应用中可能需要更复杂的NLP处理
    facts = []
    lines = case_content.split('\n')
    
    # 简单识别包含"事实"或"情况"的段落
    for line in lines:
        if "事实" in line or "情况" in line or "诉称" in line:
            facts.append(line.strip())
    
    # 如果没有找到任何事实，返回前几行作为事实
    if not facts and len(lines) > 5:
        facts = [line.strip() for line in lines[1:5] if line.strip()]
    
    return facts 