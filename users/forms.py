from allauth.account.forms import LoginForm, SignupForm


def _bootstrapify(form, css_class: str = "form-control") -> None:
    """Inject Bootstrap classes into widgets of the given form."""
    for field in form.fields.values():
        widget = field.widget
        existing = widget.attrs.get("class", "")
        widget.attrs["class"] = f"{existing} {css_class}".strip()
        widget.attrs.setdefault("placeholder", field.label or "")


class BootstrapLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrapify(self)


class BootstrapSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrapify(self)
