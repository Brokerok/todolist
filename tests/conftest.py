import pytest

from tests.factories import ProjectFactory, TaskFactory, UserFactory


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def other_user(db):
    return UserFactory()


@pytest.fixture
def project(db, user):
    return ProjectFactory(owner=user)


@pytest.fixture
def task(db, project):
    return TaskFactory(project=project)


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def other_auth_client(client, other_user):
    client.force_login(other_user)
    return client
