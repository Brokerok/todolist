from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from . import services
from .forms import ProjectForm
from .models import Project


class OwnerScopedMixin(LoginRequiredMixin):
    """Restrict the queryset to objects owned by the current user."""

    def get_queryset(self):
        return self.model.objects.for_user(self.request.user)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "tasks/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.for_user(self.request.user).prefetch_related("tasks")


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    http_method_names = ["post"]

    def form_valid(self, form):
        self.object = services.create_project(
            owner=self.request.user,
            name=form.cleaned_data["name"],
        )
        if self.request.htmx:
            return render(
                self.request,
                "tasks/_project_card.html",
                {"project": self.object},
            )
        return HttpResponseRedirect(reverse_lazy("tasks:project_list"))

    def form_invalid(self, form):
        if self.request.htmx:
            return render(
                self.request,
                "tasks/_project_create_form.html",
                {"form": form},
                status=400,
            )
        return HttpResponseRedirect(reverse_lazy("tasks:project_list"))


class ProjectUpdateView(OwnerScopedMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "tasks/_project_edit_form.html"
    http_method_names = ["get", "post"]

    def form_valid(self, form):
        self.object = services.rename_project(
            project=self.object,
            name=form.cleaned_data["name"],
        )
        if self.request.htmx:
            return render(
                self.request,
                "tasks/_project_header.html",
                {"project": self.object},
            )
        return HttpResponseRedirect(reverse_lazy("tasks:project_list"))

    def form_invalid(self, form):
        if self.request.htmx:
            return render(
                self.request,
                "tasks/_project_edit_form.html",
                {"form": form, "project": self.object},
                status=400,
            )
        return HttpResponseRedirect(reverse_lazy("tasks:project_list"))


class ProjectHeaderView(OwnerScopedMixin, UpdateView):
    """Return the read-only header row (used to cancel inline editing)."""

    model = Project
    fields: list[str] = []
    template_name = "tasks/_project_header.html"
    http_method_names = ["get"]


class ProjectDeleteView(OwnerScopedMixin, DeleteView):
    model = Project
    success_url = reverse_lazy("tasks:project_list")
    http_method_names = ["post", "delete"]

    def form_valid(self, form):
        services.delete_project(project=self.object)
        if self.request.htmx:
            return HttpResponse(status=200)
        return HttpResponseRedirect(self.success_url)
