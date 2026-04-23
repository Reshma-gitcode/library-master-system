from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'

    def ready(self):
        """Register signal handlers when the app is ready."""
        import library.signals  # noqa: F401
