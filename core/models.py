from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")
    telegram_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telegram ID")
    role = models.CharField(max_length=50, default="Участник", verbose_name="Роль в команде")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Title(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название тайтла")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    poster = models.ImageField(upload_to='posters/', verbose_name="Постер", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Тайтл"
        verbose_name_plural = "Тайтлы"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Episode(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='episodes', verbose_name="Тайтл")
    number = models.IntegerField(verbose_name="Номер серии")
    name = models.CharField(max_length=255, verbose_name="Название серии", default="Серия")
    video_url = models.URLField(verbose_name="Ссылка на видео / Плеер", default="", blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Серия"
        verbose_name_plural = "Серии"
        ordering = ['number']

    def __str__(self):
        return f"{self.title.name} — Серия {self.number}"

class TrackAssignment(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='assignments', verbose_name="Серия")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    role = models.CharField(max_length=50, verbose_name="Роль на серии", default="Озвучка", blank=True)
    is_completed = models.BooleanField(default=False, verbose_name="Готово")

    class Meta:
        verbose_name = "Назначение роли"
        verbose_name_plural = "Назначения ролей"

    def __str__(self):
        username = self.user.username if self.user else "Не назначен"
        return f"{self.episode} — {username} [{self.role}]"

class Comment(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='comments', verbose_name="Тайтл")
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='comments', blank=True, null=True, verbose_name="Серия")
    author_name = models.CharField(max_length=100, verbose_name="Имя автора", default="Аноним")
    text = models.TextField(verbose_name="Текст комментария", default="")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author_name}: {self.text[:30]}"