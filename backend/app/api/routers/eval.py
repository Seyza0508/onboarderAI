from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_db, require_role
from app.db.models import ClassificationEvaluation, RecommendationEvaluation, RetrievalEvaluation
from app.eval.classification_eval import run_classification_eval
from app.eval.recommendation_eval import run_recommendation_eval
from app.eval.retrieval_eval import run_retrieval_eval


router = APIRouter(prefix="/eval")


class RetrievalEvalRequest(BaseModel):
    query: str
    expected_docs: list[str]


class ClassificationEvalRequest(BaseModel):
    blocker_text: str
    expected_type: str


class RecommendationEvalRequest(BaseModel):
    context_json: dict
    expected_action: str


@router.post("/retrieval/run", status_code=status.HTTP_200_OK)
def eval_retrieval(
    payload: RetrievalEvalRequest,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_role("admin", "manager")),
) -> dict:
    row = run_retrieval_eval(db=db, query=payload.query, expected_docs=payload.expected_docs)
    return {"id": row.id, "score": row.score}


@router.post("/classification/run", status_code=status.HTTP_200_OK)
def eval_classification(
    payload: ClassificationEvalRequest,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_role("admin", "manager")),
) -> dict:
    row = run_classification_eval(db=db, blocker_text=payload.blocker_text, expected_type=payload.expected_type)
    return {"id": row.id, "score": row.score, "predicted_type": row.predicted_type}


@router.post("/recommendation/run", status_code=status.HTTP_200_OK)
def eval_recommendation(
    payload: RecommendationEvalRequest,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_role("admin", "manager")),
) -> dict:
    row = run_recommendation_eval(db=db, context=payload.context_json, expected_action=payload.expected_action)
    return {"id": row.id, "score": row.score, "predicted_action": row.predicted_action}


@router.get("/summary", status_code=status.HTTP_200_OK)
def eval_summary(
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_auth_context),
) -> dict:
    retrieval_avg = db.scalar(select(func.avg(RetrievalEvaluation.score))) or 0.0
    classification_avg = db.scalar(select(func.avg(ClassificationEvaluation.score))) or 0.0
    recommendation_avg = db.scalar(select(func.avg(RecommendationEvaluation.score))) or 0.0
    return {
        "retrieval_average": retrieval_avg,
        "classification_average": classification_avg,
        "recommendation_average": recommendation_avg,
    }
