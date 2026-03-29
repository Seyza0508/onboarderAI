from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import RecommendationEvaluation
from app.services.blocker_service import classify_blocker


def run_recommendation_eval(db: Session, context: dict, expected_action: str) -> RecommendationEvaluation:
    description = str(context.get("description", "blocked waiting for dependency"))
    severity = str(context.get("severity", "medium"))
    decision = classify_blocker(description=description, severity=severity)
    predicted_action = decision.recommended_action
    score = 1.0 if expected_action.lower() in predicted_action.lower() else 0.0
    row = RecommendationEvaluation(
        context_json=context,
        expected_action=expected_action,
        predicted_action=predicted_action,
        score=score,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
