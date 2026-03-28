from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Task
from app.db.schemas import TaskRead, TaskUpdate


router = APIRouter()


@router.patch("/tasks/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if payload.status is not None:
        task.status = payload.status
    if payload.notes is not None:
        task.notes = payload.notes

    db.commit()
    db.refresh(task)
    return task
