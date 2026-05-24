"""Business logic for the tasks app.

Views delegate any state-mutating operation here so that:
- views stay thin and easy to test;
- the same logic can be reused from management commands, tests, or future APIs.
"""

from __future__ import annotations

from datetime import date

from django.db.models import Max
from django.utils import timezone

from .models import Project, Task

_UNSET: object = object()


def _next_project_order(user) -> int:
    last = Project.objects.for_user(user).aggregate(Max("order"))["order__max"]
    return (last or 0) + 1


def _next_task_order(project: Project) -> int:
    last = project.tasks.aggregate(Max("order"))["order__max"]
    return (last or 0) + 1


def create_project(*, owner, name: str) -> Project:
    return Project.objects.create(
        owner=owner,
        name=name,
        order=_next_project_order(owner),
    )


def rename_project(*, project: Project, name: str) -> Project:
    project.name = name
    project.save(update_fields=["name", "updated_at"])
    return project


def delete_project(*, project: Project) -> None:
    project.delete()


def create_task(*, project: Project, name: str, deadline: date | None = None) -> Task:
    return Task.objects.create(
        project=project,
        name=name,
        deadline=deadline,
        order=_next_task_order(project),
    )


def update_task(
    *,
    task: Task,
    name: str | object = _UNSET,
    deadline: date | None | object = _UNSET,
    status: str | object = _UNSET,
) -> Task:
    """Update only the fields explicitly passed in (None is a real value)."""
    update_fields: list[str] = ["updated_at"]
    if name is not _UNSET:
        task.name = name  # type: ignore[assignment]
        update_fields.append("name")
    if deadline is not _UNSET:
        task.deadline = deadline  # type: ignore[assignment]
        update_fields.append("deadline")
    if status is not _UNSET:
        task.status = status  # type: ignore[assignment]
        update_fields.append("status")
        task.completed_at = timezone.now() if status == Task.Status.DONE else None
        update_fields.append("completed_at")
    task.save(update_fields=update_fields)
    return task


def toggle_task_done(*, task: Task) -> Task:
    if task.status == Task.Status.DONE:
        task.status = Task.Status.TODO
        task.completed_at = None
    else:
        task.status = Task.Status.DONE
        task.completed_at = timezone.now()
    task.save(update_fields=["status", "completed_at", "updated_at"])
    return task


def delete_task(*, task: Task) -> None:
    task.delete()
