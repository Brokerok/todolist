from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from . import services
from .forms import ProjectForm, QuickTaskForm, TaskForm
from .models import Project, Task


class OwnerScopedMixin(LoginRequiredMixin):
    """Restrict the queryset to objects owned by the current user."""

    def get_queryset(self):
        return self.model.objects.for_user(self.request.user)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


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


class ProjectHeaderView(OwnerScopedMixin, DetailView):
    """Return the read-only header row (used to cancel inline editing)."""

    model = Project
    template_name = "tasks/_project_header.html"
    context_object_name = "project"
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


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = QuickTaskForm
    http_method_names = ["post"]

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.project = None
        if request.user.is_authenticated:
            self.project = get_object_or_404(
                Project.objects.for_user(request.user),
                pk=kwargs["project_id"],
            )

    def form_valid(self, form):
        self.object = services.create_task(
            project=self.project,
            name=form.cleaned_data["name"],
        )
        if self.request.htmx:
            return render(self.request, "tasks/_task_row.html", {"task": self.object})
        return HttpResponseRedirect(reverse_lazy("tasks:project_list"))

    def form_invalid(self, form):
        if self.request.htmx:
            return render(
                self.request,
                "tasks/_quick_task_form.html",
                {"project": self.project, "form": form},
                status=400,
            )
        return HttpResponseRedirect(reverse_lazy("tasks:project_list"))


class TaskUpdateView(OwnerScopedMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/_task_edit_form.html"
    http_method_names = ["get", "post"]

    def form_valid(self, form):
        self.object = services.update_task(
            task=self.object,
            name=form.cleaned_data["name"],
            deadline=form.cleaned_data["deadline"],
            status=form.cleaned_data["status"],
        )
        if self.request.htmx:
            return render(self.request, "tasks/_task_row.html", {"task": self.object})
        return HttpResponseRedirect(reverse_lazy("tasks:project_list"))

    def form_invalid(self, form):
        if self.request.htmx:
            return render(
                self.request,
                "tasks/_task_edit_form.html",
                {"form": form, "task": self.object},
                status=400,
            )
        return HttpResponseRedirect(reverse_lazy("tasks:project_list"))


class TaskRowView(OwnerScopedMixin, DetailView):
    """Return the read-only task row (used to cancel inline editing)."""

    model = Task
    template_name = "tasks/_task_row.html"
    context_object_name = "task"
    http_method_names = ["get"]


class TaskToggleDoneView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task.objects.for_user(request.user), pk=pk)
        task = services.toggle_task_done(task=task)
        if request.htmx:
            return render(request, "tasks/_task_row.html", {"task": task})
        return HttpResponseRedirect(reverse_lazy("tasks:project_list"))


class TaskDeleteView(OwnerScopedMixin, DeleteView):
    model = Task
    http_method_names = ["post", "delete"]

    def form_valid(self, form):
        services.delete_task(task=self.object)
        if self.request.htmx:
            return HttpResponse(status=200)
        return HttpResponseRedirect(reverse_lazy("tasks:project_list"))


class TaskReorderView(LoginRequiredMixin, View):
    """Accept a new order for a project's tasks coming from SortableJS."""

    http_method_names = ["post"]

    def post(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(
            Project.objects.for_user(request.user),
            pk=project_id,
        )
        try:
            ordered_ids = [int(x) for x in request.POST.getlist("task_ids[]")]
        except (TypeError, ValueError):
            return HttpResponse(status=400)
        services.reorder_tasks(project=project, ordered_ids=ordered_ids)
        return HttpResponse(status=204)
