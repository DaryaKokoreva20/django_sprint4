"""Добавила функцию для обработки регистрации.
Добавила функции отображения страницы профиля,
редактирования профиля, изменения пароля.

"""
from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Category
from .forms import RegistrationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def posts():
    """Получение постов из БД"""
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def index(request):
    """Главная страница / Лента записей"""
    return render(request, 'blog/index.html', {'post_list': posts()[:5]})


def post_detail(request, id):
    """Отображение полного описания выбранной записи"""
    post = get_object_or_404(posts(), id=id)
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    """Отображение публикаций категории"""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    context = {'category': category,
               'post_list': posts().filter(category=category)}
    return render(request, 'blog/category.html', context)


def register(request):
    """Обработка регистрации"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(
        request, 'registration/registration_form.html', {'form': form}
    )


def profile(request, username):
    """Страница профиля"""
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    return render(request, 'profile.html', {'user': user, 'posts': posts})


@login_required
def edit_profile(request):
    """Страница редактирования профиля (доступна только владельцу аккаунта)"""
    if request.method == 'POST':
        pass
    return render(request, 'edit_profile.html')


@login_required
def change_password(request):
    """Страница изменения пароля (доступна только владельцу аккаунта)"""
    if request.method == 'POST':
        pass
    return render(request, 'change_password.html')
