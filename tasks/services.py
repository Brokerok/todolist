"""Business logic for the tasks app.

Views delegate any state-mutating operation here so that:
- views stay thin and easy to test;
- the same logic can be reused from management commands, tests, or future APIs.
"""

from __future__ import annotations

from django.db.models import Max

from .models import Project


def _next_project_order(user) -> int:
    last = Project.objects.for_user(user).aggregate(Max("order"))["order__max"]
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
