from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


TaskStatus = Literal["not_started", "in_progress", "blocked", "complete"]
AccessStatus = Literal["not_requested", "pending", "granted", "denied"]
BlockerType = Literal["access", "environment", "documentation", "dependency", "ownership"]
BlockerSeverity = Literal["low", "medium", "high", "critical"]
BlockerStatus = Literal["open", "in_review", "resolved"]
InteractionType = Literal["intake", "chat", "plan", "blocker", "escalation", "progress"]


class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    team: str
    level: str
    manager_name: str
    start_date: date


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: str
    team: str
    level: str
    manager_name: str
    start_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailRead(UserRead):
    access_statuses: list["UserAccessRead"] = []


class UserAccessCreate(BaseModel):
    tool_name: str
    status: AccessStatus
    notes: str | None = None


class UserAccessRead(BaseModel):
    id: int
    user_id: int
    tool_name: str
    status: AccessStatus
    notes: str | None = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanGenerateResponse(BaseModel):
    user_id: int
    generated_task_count: int
    message: str


class TaskRead(BaseModel):
    id: int
    user_id: int
    task_name: str
    category: str
    status: TaskStatus
    priority: str
    depends_on_task_id: int | None = None
    doc_reference: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    status: TaskStatus | None = None
    notes: str | None = None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    user_id: int
    response: str
    sources: list[str]


class BlockerCreate(BaseModel):
    task_id: int | None = None
    description: str
    blocker_type: BlockerType
    severity: BlockerSeverity = "medium"
    status: BlockerStatus = "open"
    recommended_action: str | None = None
    escalation_needed: bool = False


class BlockerRead(BaseModel):
    id: int
    user_id: int
    task_id: int | None = None
    blocker_type: BlockerType
    description: str
    severity: BlockerSeverity
    status: BlockerStatus
    recommended_action: str | None = None
    escalation_needed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProgressResponse(BaseModel):
    user_id: int
    total_tasks: int
    completed_tasks: int
    blocked_tasks: int
    pending_tasks: int
    current_blocker: BlockerRead | None
    recommended_next_action: str | None


class EscalationDraftRequest(BaseModel):
    blocker_id: int | None = None
    channel: Literal["slack", "email"] = "slack"


class EscalationDraftResponse(BaseModel):
    user_id: int
    blocker_id: int | None
    channel: Literal["slack", "email"]
    draft_message: str


class InteractionCreate(BaseModel):
    user_id: int
    interaction_type: InteractionType
    user_message: str
    assistant_summary: str
