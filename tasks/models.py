from django.conf import settings
from django.db import models


class ProjectQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(owner=user)


class Project(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ["order", "created_at"]
        indexes = [models.Index(fields=["owner", "order"])]

    def __str__(self) -> str:
        return self.name


class TaskQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(project__owner=user)


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To do"
        DONE = "done", "Done"

    name = models.CharField(max_length=200)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.TODO,
    )
    deadline = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    objects = TaskQuerySet.as_manager()

    class Meta:
        ordering = ["order", "created_at"]
        indexes = [models.Index(fields=["project", "order"])]

    def __str__(self) -> str:
        return self.name

    @property
    def is_done(self) -> bool:
        return self.status == self.Status.DONE
