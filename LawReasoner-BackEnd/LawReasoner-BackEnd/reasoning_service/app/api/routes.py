from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from sqlalchemy.orm import Session
from typing import List, Any
import httpx

from app.api import deps
from app.core.config import settings
from app.db.session import get_db
from app.models.case import Case as CaseModel
from app.schemas.case import Case, CaseCreate, CaseUpdate, CaseAnalysisRequest, AnalysisResult
from app.services.reasoning import analyze_case

api_router = APIRouter()


@api_router.post("/cases/", response_model=Case)
def create_case(
    case_in: CaseCreate,
    current_user_id: int = Body(...),
    db: Session = Depends(get_db)
):
    """创建新案例"""
    db_case = CaseModel(
        **case_in.dict(),
        created_by=current_user_id
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


@api_router.get("/cases/", response_model=List[Case])
def read_cases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取案例列表"""
    cases = db.query(CaseModel).offset(skip).limit(limit).all()
    return cases


@api_router.get("/cases/{case_id}", response_model=Case)
def read_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    """获取单个案例详情"""
    db_case = db.query(CaseModel).filter(CaseModel.id == case_id).first()
    if db_case is None:
        raise HTTPException(status_code=404, detail="案例不存在")
    return db_case


@api_router.put("/cases/{case_id}", response_model=Case)
def update_case(
    case_id: int,
    case_in: CaseUpdate,
    db: Session = Depends(get_db)
):
    """更新案例"""
    db_case = db.query(CaseModel).filter(CaseModel.id == case_id).first()
    if db_case is None:
        raise HTTPException(status_code=404, detail="案例不存在")
    
    update_data = case_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_case, field, value)
    
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


@api_router.delete("/cases/{case_id}", response_model=dict)
def delete_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    """删除案例"""
    db_case = db.query(CaseModel).filter(CaseModel.id == case_id).first()
    if db_case is None:
        raise HTTPException(status_code=404, detail="案例不存在")
    
    db.delete(db_case)
    db.commit()
    return {"message": "案例已成功删除"}


@api_router.post("/cases/analyze", response_model=dict)
async def analyze_case_endpoint(
    analysis_request: CaseAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """分析案例（异步）"""
    db_case = db.query(CaseModel).filter(CaseModel.id == analysis_request.case_id).first()
    if db_case is None:
        raise HTTPException(status_code=404, detail="案例不存在")
    
    # 更新案例状态为分析中
    db_case.status = "analyzing"
    db.add(db_case)
    db.commit()
    
    # 在后台任务中执行分析
    background_tasks.add_task(
        analyze_case,
        db=db,
        case_id=analysis_request.case_id,
        analysis_types=analysis_request.analysis_types
    )
    
    return {
        "message": "案例分析已开始，请稍后查看结果",
        "case_id": analysis_request.case_id
    }


@api_router.get("/cases/{case_id}/analysis", response_model=List[AnalysisResult])
def get_case_analysis_results(
    case_id: int,
    db: Session = Depends(get_db)
):
    """获取案例分析结果"""
    db_case = db.query(CaseModel).filter(CaseModel.id == case_id).first()
    if db_case is None:
        raise HTTPException(status_code=404, detail="案例不存在")
    
    return db_case.analysis_results 