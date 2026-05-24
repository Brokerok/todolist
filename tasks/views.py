from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class ProjectListView(LoginRequiredMixin, TemplateView):
    """Placeholder: real CRUD comes in the next iteration."""

    template_name = "tasks/project_list.html"
