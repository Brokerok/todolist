from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model so we can extend it later without painful migrations."""

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
