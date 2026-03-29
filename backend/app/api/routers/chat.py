from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_db, get_user_in_org
from app.db.models import AnswerLog, Interaction, LlmProvider
from app.db.schemas import ChatRequest, ChatResponse
from app.rag.ingestion import build_index
from app.services.chat_service import answer_onboarding_question


router = APIRouter()


@router.post("/users/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_with_user(
    user_id: int,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> ChatResponse:
    user = get_user_in_org(user_id=user_id, ctx=ctx, db=db)

    # Ensure the retrieval index exists before answering.
    build_index(force_rebuild=False)
    provider = db.scalar(
        select(LlmProvider).where(LlmProvider.organization_id == ctx.organization_id, LlmProvider.is_default.is_(True))
    )
    provider_name = provider.provider_name if provider else "mock"
    model_name = provider.model_name if provider else "mock-v1"

    response_text, sources, confidence, model_used = answer_onboarding_question(
        user=user,
        question=payload.message,
        provider_name=provider_name,
        model_name=model_name,
    )

    interaction = Interaction(
        organization_id=ctx.organization_id,
        user_id=user_id,
        interaction_type="chat",
        user_message=payload.message,
        assistant_summary=response_text,
    )
    db.add(interaction)
    db.add(
        AnswerLog(
            user_id=user_id,
            query=payload.message,
            retrieved_sources=", ".join(sources),
            model_used=model_used,
            grounded_confidence=confidence,
        )
    )
    db.commit()

    return ChatResponse(user_id=user_id, response=response_text, sources=sources)


@router.post("/users/{user_id}/chat/answer", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_answer(
    user_id: int,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> ChatResponse:
    return chat_with_user(user_id=user_id, payload=payload, db=db, ctx=ctx)
