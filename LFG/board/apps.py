from django.apps import AppConfig


class BoardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'board'
    verbose_name = 'Доска объявлений'

    def ready(self):
        from . import signals  # выполнение модуля -> регистрация сигналов
