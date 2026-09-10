from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Управление проектами'

    def ready(self):
        from django.contrib.auth.models import User, Group
        User._meta.verbose_name = 'Пользователь'
        User._meta.verbose_name_plural = 'Пользователи'
        Group._meta.verbose_name = 'Группа прав'
        Group._meta.verbose_name_plural = 'Группы прав'