import pytest

from tasks.models import Project, Task
from tests.factories import ProjectFactory, TaskFactory, UserFactory


@pytest.mark.django_db
class TestProject:
    def test_str_returns_name(self):
        project = ProjectFactory(name="My TODO list")
        assert str(project) == "My TODO list"

    def test_for_user_filters_by_owner(self):
        owner = UserFactory()
        intruder = UserFactory()
        mine = ProjectFactory(owner=owner)
        ProjectFactory(owner=intruder)

        assert list(Project.objects.for_user(owner)) == [mine]

    def test_deleting_project_cascades_to_tasks(self):
        project = ProjectFactory()
        TaskFactory(project=project)
        TaskFactory(project=project)
        assert Task.objects.filter(project=project).count() == 2

        project.delete()
        assert Task.objects.filter(project_id=project.pk).count() == 0


@pytest.mark.django_db
class TestTask:
    def test_str_returns_name(self):
        task = TaskFactory(name="Buy milk")
        assert str(task) == "Buy milk"

    def test_is_done_property(self):
        task = TaskFactory(status=Task.Status.TODO)
        assert task.is_done is False

        task.status = Task.Status.DONE
        assert task.is_done is True

    def test_for_user_filters_by_project_owner(self):
        owner = UserFactory()
        intruder = UserFactory()
        mine = TaskFactory(project=ProjectFactory(owner=owner))
        TaskFactory(project=ProjectFactory(owner=intruder))

        assert list(Task.objects.for_user(owner)) == [mine]
