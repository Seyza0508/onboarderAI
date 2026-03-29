from fastapi import APIRouter

from app.api.routers import (
    access,
    auth,
    blockers,
    chat,
    escalation,
    eval,
    manager_dashboard,
    organizations,
    plan,
    progress,
    risk,
    tasks,
    users,
    workflows,
)


api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(organizations.router, tags=["organizations"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(access.router, tags=["access"])
api_router.include_router(plan.router, tags=["plan"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(blockers.router, tags=["blockers"])
api_router.include_router(tasks.router, tags=["tasks"])
api_router.include_router(progress.router, tags=["progress"])
api_router.include_router(escalation.router, tags=["escalation"])
api_router.include_router(workflows.router, tags=["workflows"])
api_router.include_router(manager_dashboard.router, tags=["manager-dashboard"])
api_router.include_router(risk.router, tags=["risk"])
api_router.include_router(eval.router, tags=["evaluation"])
