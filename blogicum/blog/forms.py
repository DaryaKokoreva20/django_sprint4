"""Создала форму регистрации RegistrationForm.
Создала форму для комментариев.
"""
from django import forms

from .models import Post, User, Comment


class UserForm(forms.ModelForm):
    """Форма для создания и редактирования профиля пользователя"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования публикаций"""

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    """Форма для добавления комментариев к публикациям"""

    class Meta:
        model = Comment
        fields = ('text',)
