import pytest
from django.urls import reverse

from tasks.models import Project, Task
from tests.factories import ProjectFactory


@pytest.mark.django_db
class TestProjectListView:
    def test_redirects_anonymous_to_login(self, client):
        response = client.get(reverse("tasks:project_list"))
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_shows_only_own_projects(self, auth_client, user, other_user):
        mine = ProjectFactory(owner=user, name="Mine")
        ProjectFactory(owner=other_user, name="Not mine")

        response = auth_client.get(reverse("tasks:project_list"))

        assert response.status_code == 200
        assert mine.name.encode() in response.content
        assert b"Not mine" not in response.content


@pytest.mark.django_db
class TestProjectCreateView:
    def test_creates_project_for_current_user(self, auth_client, user):
        response = auth_client.post(reverse("tasks:project_create"), {"name": "New"})

        assert response.status_code in {200, 302}
        assert Project.objects.filter(owner=user, name="New").exists()

    def test_htmx_response_returns_card_partial(self, auth_client, user):
        response = auth_client.post(
            reverse("tasks:project_create"),
            {"name": "HX"},
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 200
        assert b"project-card-" in response.content

    def test_invalid_name_returns_form_with_errors(self, auth_client):
        response = auth_client.post(
            reverse("tasks:project_create"),
            {"name": "   "},
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 400
        assert b"is-invalid" in response.content or b"Name cannot be empty" in response.content


@pytest.mark.django_db
class TestProjectUpdateView:
    def test_owner_can_rename(self, auth_client, project):
        response = auth_client.post(
            reverse("tasks:project_update", args=[project.pk]),
            {"name": "Renamed"},
        )
        assert response.status_code in {200, 302}
        project.refresh_from_db()
        assert project.name == "Renamed"

    def test_intruder_gets_404(self, other_auth_client, project):
        response = other_auth_client.post(
            reverse("tasks:project_update", args=[project.pk]),
            {"name": "Hacked"},
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestProjectDeleteView:
    def test_owner_can_delete(self, auth_client, project):
        response = auth_client.post(reverse("tasks:project_delete", args=[project.pk]))
        assert response.status_code in {200, 302}
        assert not Project.objects.filter(pk=project.pk).exists()

    def test_intruder_gets_404(self, other_auth_client, project):
        response = other_auth_client.post(reverse("tasks:project_delete", args=[project.pk]))
        assert response.status_code == 404
        assert Project.objects.filter(pk=project.pk).exists()


@pytest.mark.django_db
class TestTaskCreateView:
    def test_owner_can_create_task(self, auth_client, project):
        response = auth_client.post(
            reverse("tasks:task_create", args=[project.pk]),
            {"name": "Buy milk"},
        )
        assert response.status_code in {200, 302}
        assert Task.objects.filter(project=project, name="Buy milk").exists()

    def test_intruder_cannot_create_task_in_someone_elses_project(self, other_auth_client, project):
        response = other_auth_client.post(
            reverse("tasks:task_create", args=[project.pk]),
            {"name": "Hacked"},
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestTaskToggleView:
    def test_owner_can_toggle(self, auth_client, task):
        assert task.status == Task.Status.TODO

        response = auth_client.post(reverse("tasks:task_toggle", args=[task.pk]))
        assert response.status_code in {200, 302}

        task.refresh_from_db()
        assert task.status == Task.Status.DONE

    def test_intruder_gets_404(self, other_auth_client, task):
        response = other_auth_client.post(reverse("tasks:task_toggle", args=[task.pk]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestTaskDeleteView:
    def test_owner_can_delete(self, auth_client, task):
        response = auth_client.post(reverse("tasks:task_delete", args=[task.pk]))
        assert response.status_code in {200, 302}
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_intruder_cannot_delete(self, other_auth_client, task):
        response = other_auth_client.post(reverse("tasks:task_delete", args=[task.pk]))
        assert response.status_code == 404
        assert Task.objects.filter(pk=task.pk).exists()
