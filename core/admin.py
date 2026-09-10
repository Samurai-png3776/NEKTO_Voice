from django.contrib import admin
from .models import UserProfile, Title, Episode, TrackAssignment, Comment

# Меняем стандартные заголовки Django в Админке
admin.site.site_header = "NEKTO Voice — РАЗДЕЛ ОЗВУЧКИ"
admin.site.site_title = "NEKTO Voice"
admin.site.index_title = "Управление проектами и озвучкой"

# Вложенный блок для добавления кучи людей прямо внутри Серии
class TrackAssignmentInline(admin.TabularInline):
    model = TrackAssignment
    extra = 5  # Сразу даёт 5 пустых строк для ввода людей
    verbose_name = "Участника и роль"
    verbose_name_plural = "Состав команды на серию (Озвучка / Перевод / Звук)"

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'number', 'name', 'created_at')
    list_filter = ('title',)
    search_fields = ('title__name', 'name')
    inlines = [TrackAssignmentInline] # Подключаем массовый ввод ролей!

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'telegram_id')
    search_fields = ('user__username', 'telegram_id')

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(TrackAssignment)
class TrackAssignmentAdmin(admin.ModelAdmin):
    list_display = ('episode', 'user', 'role', 'is_completed')
    list_filter = ('is_completed', 'role')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'title', 'episode', 'created_at')
    list_filter = ('title', 'created_at')
    search_fields = ('author_name', 'text')