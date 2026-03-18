from django.apps import AppConfig


class CustomUserConfig(AppConfig):
    name = "custom_user"
    verbose_name = "Custom User Management"

    def ready(self):
        from . import signals
