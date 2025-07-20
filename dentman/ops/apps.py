from django.apps import AppConfig


class OpsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dentman.ops'

    def ready(self):
        import dentman.ops.signals
