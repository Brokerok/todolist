from datetime import date, timedelta

import pytest

from tasks.forms import ProjectForm, QuickTaskForm, TaskForm
from tasks.models import Task


@pytest.mark.django_db
class TestProjectForm:
    def test_strips_surrounding_whitespace(self):
        form = ProjectForm(data={"name": "  Inbox  "})
        assert form.is_valid()
        assert form.cleaned_data["name"] == "Inbox"

    def test_rejects_whitespace_only_name(self):
        form = ProjectForm(data={"name": "   "})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_rejects_empty_name(self):
        form = ProjectForm(data={"name": ""})
        assert not form.is_valid()


@pytest.mark.django_db
class TestTaskForm:
    def test_rejects_past_deadline(self):
        yesterday = date.today() - timedelta(days=1)
        form = TaskForm(
            data={"name": "Late", "deadline": yesterday.isoformat(), "status": Task.Status.TODO}
        )
        assert not form.is_valid()
        assert "deadline" in form.errors

    def test_accepts_today_as_deadline(self):
        form = TaskForm(
            data={"name": "Today", "deadline": date.today().isoformat(), "status": Task.Status.TODO}
        )
        assert form.is_valid(), form.errors


@pytest.mark.django_db
class TestQuickTaskForm:
    def test_rejects_whitespace_only_name(self):
        form = QuickTaskForm(data={"name": "   "})
        assert not form.is_valid()
