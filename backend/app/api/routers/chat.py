from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Interaction, User
from app.db.schemas import ChatRequest, ChatResponse


router = APIRouter()


@router.post("/users/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_with_user(user_id: int, payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    response_text = (
        f"Hi {user.name}, I logged your onboarding question and will use your role ({user.role}) and "
        f"team ({user.team}) context to guide next actions."
    )
    sources = ["engineering_onboarding_handbook.md", "who_to_contact.md"]

    interaction = Interaction(
        user_id=user_id,
        interaction_type="chat",
        user_message=payload.message,
        assistant_summary=response_text,
    )
    db.add(interaction)
    db.commit()

    return ChatResponse(user_id=user_id, response=response_text, sources=sources)
