from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dentman.app'

    def ready(self):
        import dentman.app.signals
