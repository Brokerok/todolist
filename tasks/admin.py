from django.contrib import admin

from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "order", "created_at")
    search_fields = ("name", "owner__username", "owner__email")
    list_filter = ("created_at",)
    autocomplete_fields = ("owner",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "status", "deadline", "order")
    list_filter = ("status", "deadline")
    search_fields = ("name", "project__name")
    autocomplete_fields = ("project",)
