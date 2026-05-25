from datetime import date, timedelta

import pytest
from django.utils import timezone

from tasks import services
from tasks.models import Project, Task
from tests.factories import ProjectFactory, TaskFactory, UserFactory


@pytest.mark.django_db
class TestCreateProject:
    def test_assigns_owner_and_starts_order_at_one(self):
        owner = UserFactory()

        project = services.create_project(owner=owner, name="Inbox")

        assert project.owner == owner
        assert project.name == "Inbox"
        assert project.order == 1

    def test_increments_order_per_owner(self):
        owner = UserFactory()
        services.create_project(owner=owner, name="A")
        services.create_project(owner=owner, name="B")
        third = services.create_project(owner=owner, name="C")

        assert third.order == 3

    def test_order_is_scoped_per_owner(self):
        first_owner = UserFactory()
        services.create_project(owner=first_owner, name="A")

        second_owner = UserFactory()
        their_first = services.create_project(owner=second_owner, name="A")

        assert their_first.order == 1


@pytest.mark.django_db
class TestRenameProject:
    def test_changes_only_name_field(self):
        project = ProjectFactory(name="Old")
        services.rename_project(project=project, name="New")

        project.refresh_from_db()
        assert project.name == "New"


@pytest.mark.django_db
class TestDeleteProject:
    def test_removes_row(self):
        project = ProjectFactory()
        services.delete_project(project=project)

        assert not Project.objects.filter(pk=project.pk).exists()


@pytest.mark.django_db
class TestCreateTask:
    def test_creates_task_with_next_order(self):
        project = ProjectFactory()
        TaskFactory(project=project, order=1)
        TaskFactory(project=project, order=2)

        new_task = services.create_task(project=project, name="Third")

        assert new_task.order == 3
        assert new_task.project == project


@pytest.mark.django_db
class TestUpdateTask:
    def test_updates_name_only(self):
        task = TaskFactory(name="Old", status=Task.Status.TODO)

        services.update_task(task=task, name="New")

        task.refresh_from_db()
        assert task.name == "New"
        assert task.status == Task.Status.TODO

    def test_clears_completed_at_when_status_becomes_todo(self):
        task = TaskFactory(status=Task.Status.DONE)
        task.completed_at = timezone.now()
        task.save()

        services.update_task(task=task, status=Task.Status.TODO)

        task.refresh_from_db()
        assert task.completed_at is None
        assert task.status == Task.Status.TODO


@pytest.mark.django_db
class TestToggleTaskDone:
    def test_marks_done_and_stamps_completed_at(self):
        task = TaskFactory(status=Task.Status.TODO)

        services.toggle_task_done(task=task)

        task.refresh_from_db()
        assert task.status == Task.Status.DONE
        assert task.completed_at is not None

    def test_marks_undone_clears_completed_at(self):
        task = TaskFactory(status=Task.Status.DONE)
        services.toggle_task_done(task=task)  # done -> todo through current state

        task.refresh_from_db()
        assert task.status == Task.Status.TODO
        assert task.completed_at is None


@pytest.mark.django_db
class TestDeleteTask:
    def test_removes_row(self):
        task = TaskFactory()
        services.delete_task(task=task)

        assert not Task.objects.filter(pk=task.pk).exists()


@pytest.mark.django_db
class TestCreateTaskWithDeadline:
    def test_persists_deadline(self):
        project = ProjectFactory()
        in_three_days = date.today() + timedelta(days=3)

        task = services.create_task(project=project, name="Deadline", deadline=in_three_days)

        assert task.deadline == in_three_days


@pytest.mark.django_db
class TestReorderTasks:
    def test_persists_new_order(self):
        project = ProjectFactory()
        t1 = TaskFactory(project=project, order=1)
        t2 = TaskFactory(project=project, order=2)
        t3 = TaskFactory(project=project, order=3)

        services.reorder_tasks(project=project, ordered_ids=[t3.pk, t1.pk, t2.pk])

        for task in (t1, t2, t3):
            task.refresh_from_db()
        assert (t3.order, t1.order, t2.order) == (1, 2, 3)

    def test_ignores_ids_from_other_projects(self):
        project = ProjectFactory()
        own = TaskFactory(project=project, order=1)
        alien = TaskFactory(order=1)

        services.reorder_tasks(project=project, ordered_ids=[alien.pk, own.pk])

        own.refresh_from_db()
        alien.refresh_from_db()
        assert alien.order == 1
        assert own.order == 1
