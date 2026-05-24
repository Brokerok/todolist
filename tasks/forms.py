from datetime import date

from django import forms

from .models import Project, Task


class _StripNameMixin:
    """Treat 'whitespace-only' as empty and trim surrounding whitespace."""

    def clean_name(self) -> str:
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Name cannot be empty.")
        return name


class ProjectForm(_StripNameMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Project name",
                    "maxlength": "200",
                    "required": True,
                    "autocomplete": "off",
                }
            ),
        }


class TaskForm(_StripNameMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "deadline", "status"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Task name",
                    "maxlength": "200",
                    "required": True,
                    "autocomplete": "off",
                }
            ),
            "deadline": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
                format="%Y-%m-%d",
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_deadline(self) -> date | None:
        deadline = self.cleaned_data.get("deadline")
        if deadline and deadline < date.today():
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline


class QuickTaskForm(_StripNameMixin, forms.ModelForm):
    """Single-input form used by the 'Start typing here to create a task...' field."""

    class Meta:
        model = Task
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Start typing here to create a task...",
                    "maxlength": "200",
                    "required": True,
                    "autocomplete": "off",
                }
            ),
        }
