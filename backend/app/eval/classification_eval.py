from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import ClassificationEvaluation
from app.services.blocker_service import classify_blocker


def run_classification_eval(db: Session, blocker_text: str, expected_type: str) -> ClassificationEvaluation:
    decision = classify_blocker(description=blocker_text, severity="medium")
    score = 1.0 if decision.blocker_type == expected_type else 0.0
    row = ClassificationEvaluation(
        blocker_text=blocker_text,
        expected_type=expected_type,
        predicted_type=decision.blocker_type,
        score=score,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
