from fastapi import APIRouter

from app.api.routers import access, blockers, chat, escalation, plan, progress, tasks, users


api_router = APIRouter()
api_router.include_router(users.router, tags=["users"])
api_router.include_router(access.router, tags=["access"])
api_router.include_router(plan.router, tags=["plan"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(blockers.router, tags=["blockers"])
api_router.include_router(tasks.router, tags=["tasks"])
api_router.include_router(progress.router, tags=["progress"])
api_router.include_router(escalation.router, tags=["escalation"])
