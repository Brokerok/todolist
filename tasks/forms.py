from django import forms

from .models import Project, Task


class ProjectForm(forms.ModelForm):
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


class TaskForm(forms.ModelForm):
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


class QuickTaskForm(forms.ModelForm):
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
