from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="project_list"),
    # Projects
    path("projects/", views.ProjectCreateView.as_view(), name="project_create"),
    path(
        "projects/<int:pk>/edit/",
        views.ProjectUpdateView.as_view(),
        name="project_update",
    ),
    path(
        "projects/<int:pk>/header/",
        views.ProjectHeaderView.as_view(),
        name="project_header",
    ),
    path(
        "projects/<int:pk>/delete/",
        views.ProjectDeleteView.as_view(),
        name="project_delete",
    ),
    # Tasks
    path(
        "projects/<int:project_id>/tasks/",
        views.TaskCreateView.as_view(),
        name="task_create",
    ),
    path(
        "projects/<int:project_id>/tasks/reorder/",
        views.TaskReorderView.as_view(),
        name="task_reorder",
    ),
    path("tasks/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<int:pk>/row/", views.TaskRowView.as_view(), name="task_row"),
    path(
        "tasks/<int:pk>/toggle/",
        views.TaskToggleDoneView.as_view(),
        name="task_toggle",
    ),
    path("tasks/<int:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
]
