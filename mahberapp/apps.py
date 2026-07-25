from django.apps import AppConfig


class MahberappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mahberapp'

    def ready(self):
        import mahberapp.signals  # noqa: F401
