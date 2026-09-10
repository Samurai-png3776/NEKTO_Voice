from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_home, name='public_home'),
    path('title/<int:title_id>/', views.public_title_detail, name='public_title_detail'),
    path('dashboard/', views.team_dashboard, name='team_dashboard'),
]