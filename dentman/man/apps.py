from django.apps import AppConfig


class ManConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dentman.man'

    def ready(self):
        import dentman.man.signals
