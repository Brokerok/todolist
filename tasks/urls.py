from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="project_list"),
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
]
