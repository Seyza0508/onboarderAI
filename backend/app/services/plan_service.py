from sqlalchemy.orm import Session

from app.data_access.structured_loader import find_matching_templates
from app.db.models import Task, User


def generate_tasks_for_user(user: User, db: Session) -> list[Task]:
    """Build personalized onboarding tasks from structured templates.

    Matches templates by user.role + user.team, creates Task rows,
    and resolves depends_on_task_name into depends_on_task_id after
    the initial flush.
    """
    templates = find_matching_templates(role=user.role, team=user.team)
    if not templates:
        return _generate_fallback_tasks(user, db)

    all_tasks: list[Task] = []
    for template in templates:
        name_to_task: dict[str, Task] = {}
        pending_deps: list[tuple[Task, str]] = []

        for task_def in template["tasks"]:
            task = Task(
                user_id=user.id,
                task_name=task_def["task_name"],
                category=task_def["category"],
                status="not_started",
                priority=task_def["priority"],
                doc_reference=task_def.get("doc_reference"),
            )
            db.add(task)
            name_to_task[task_def["task_name"]] = task

            dep_name = task_def.get("depends_on_task_name")
            if dep_name:
                pending_deps.append((task, dep_name))

        db.flush()

        for task, dep_name in pending_deps:
            dep_task = name_to_task.get(dep_name)
            if dep_task:
                task.depends_on_task_id = dep_task.id

        all_tasks.extend(name_to_task.values())

    return all_tasks


def _generate_fallback_tasks(user: User, db: Session) -> list[Task]:
    """Generic onboarding tasks when no matching template exists."""
    fallback = [
        Task(
            user_id=user.id,
            task_name="Activate VPN and verify internal wiki access",
            category="access",
            status="not_started",
            priority="high",
            doc_reference="vpn_setup_guide.md",
        ),
        Task(
            user_id=user.id,
            task_name="Review engineering onboarding handbook",
            category="architecture",
            status="not_started",
            priority="medium",
            doc_reference="engineering_onboarding_handbook.md",
        ),
        Task(
            user_id=user.id,
            task_name="Get GitHub organization access",
            category="access",
            status="not_started",
            priority="high",
            doc_reference="github_access_guide.md",
        ),
    ]
    db.add_all(fallback)
    db.flush()
    return fallback
