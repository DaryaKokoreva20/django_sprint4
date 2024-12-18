"""Добавила путь для регистрации.
Добавила пути для страницы профиля, редактирования профиля и изменения пароля.
Добавила пути для создания постов, редактирования.
Добавила пути для комментариев.
"""
from django.urls import path
from .views import register

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('auth/registration/', register, name='register'),
    path('profile/<username>/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('create/', views.post_create, name='post_create'),
    path('<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment, name='edit_comment'),
]
