"""Добавила функцию для обработки регистрации.
Добавила функции отображения страницы профиля,
редактирования профиля, изменения пароля.
Добавила функцию представления для создания постов.
В функцию profile добавила условие, что только автору видны отложенные посты.
Добавила функцию post_edit, которая проверяет права пользователя
и отображает форму редактирования.
Добавила функции для добавления и редактирования комментариев.
Добавила функции для удаления постов и комментариев.
"""
from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Category, Comment
from .forms import RegistrationForm, PostForm, CommentForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden


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
    if request.user == user:
        posts = user.posts.all()  # Показываем все посты автору
    else:
        posts = user.posts.filter(
            is_published=True, publish_date__lte=timezone.now()
        )
    return render(
        request, 'users/profile.html', {'user': user, 'posts': posts}
    )


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


@login_required
def post_create(request):
    """Представление для создания постов"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Проверяет права пользователя и отображает форму редактирования"""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('post_detail', post_id=post.id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create.html', {'form': form, 'is_edit': True})


@login_required
def add_comment(request, post_id):
    """Добавление комментариев"""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()
    return render(
        request, 'blog/add_comment.html', {'form': form, 'post': post}
    )


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментариев"""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('post_detail', post_id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(
        request, 'blog/edit_comment.html', {'form': form, 'post': comment.post}
    )


@login_required
def delete_post(request, post_id):
    """Удаление поста"""
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return HttpResponseForbidden("Вы не можете удалить эту публикацию.")

    if request.method == 'POST':
        post.delete()
        return redirect('profile', username=request.user.username)

    return render(request, 'blog/delete_post.html', {'post': post})


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        return HttpResponseForbidden("Вы не можете удалить этот комментарий.")

    if request.method == 'POST':
        comment.delete()
        return redirect('post_detail', post_id=post_id)

    return render(request, 'blog/delete_comment.html', {'comment': comment})
