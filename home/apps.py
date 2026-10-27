from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        try:
            import home.signals  # noqa: F401
        except ImportError:
            pass
