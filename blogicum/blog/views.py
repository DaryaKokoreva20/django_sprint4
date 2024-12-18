"""Добавила функцию для обработки регистрации.
Добавила функции отображения страницы профиля,
редактирования профиля, изменения пароля.
Добавила функцию представления для создания постов.
Настроила пагинатор на 10 позиций.
В функцию profile добавила условие, что только автору видны отложенные посты.
Добавила функцию post_edit, которая проверяет права пользователя
и отображает форму редактирования.
Добавила функции для добавления и редактирования комментариев.
Добавила функции для удаления постов и комментариев.
Добавила классы для отображения и редактирования страниц.
"""


from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    DetailView, CreateView, ListView, UpdateView, DeleteView
)

from .models import Category, Comment, Post, User
from .forms import CommentForm, PostForm, UserForm

PAGINATOR_POST = 10
PAGINATOR_CATEGORY = 10
PAGINATOR_PROFILE = 10


def filtered_post(posts, is_count_comments=True):
    """Функция для фильтрации публикаций по заданным критериям"""
    posts_query = posts.filter(
        pub_date__lte=datetime.today(),
        is_published=True,
        category__is_published=True
    ).order_by(
        '-pub_date'
    )
    return posts_query.annotate(
        comment_count=Count('comments')
    ) if is_count_comments else posts_query


class PostCategoryView(ListView):
    """Отображение списка публикаций в заданной категории"""

    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = PAGINATOR_CATEGORY

    def get_queryset(self):
        """Получение списка отфильтрованных публикаций"""
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return filtered_post(self.category.posts.all())

    def get_context_data(self, **kwargs):
        """Добавление информации о категории в контекст"""
        return dict(
            **super().get_context_data(**kwargs),
            category=self.category
        )


class PostListView(ListView):
    """Представление для отображения всех публикаций на главной странице"""

    paginate_by = PAGINATOR_POST
    template_name = 'blog/index.html'

    def get_queryset(self):
        """Получение отфильтрованных публикаций"""
        return filtered_post(Post.objects.all())


class PostCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания новой публикации"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Автоматическое назначение текущего пользователя как автора"""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправление на профиль автора после создания публикации"""
        return reverse(
            'blog:profile', args=[self.request.user.username]
        )


class PostDetailView(DetailView):
    """Отображение подробной информации о публикации"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        """Добавление комментариев и формы для добавления нового комментария"""
        return dict(
            **super().get_context_data(**kwargs),
            form=CommentForm(),
            comments=self.object.comments.select_related('author')
        )

    def get_object(self):
        """Получение публикации с учётом её статуса и прав доступа"""
        posts = Post.objects
        return get_object_or_404(
            posts.filter(
                is_published=True
            ) or posts.filter(
                author=self.request.user
            )
            if self.request.user and self.request.user.is_authenticated
            else filtered_post(Post.objects, is_count_comments=False),
            pk=self.kwargs["post_id"],
        )


class PostMixin(LoginRequiredMixin):
    """Миксин для проверки прав пользователя на публикацию"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Проверка, что публикация принадлежит текущему пользователю"""
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if post.author != self.request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostMixin, UpdateView):
    """Редактирование существующей публикации"""

    def get_success_url(self):
        """Перенаправление на стр с деталями публикации после редактирования"""
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class PostDeleteView(PostMixin, DeleteView):
    """Удаление публикации"""

    def get_success_url(self):
        """Перенаправление на профиль пользователя после удаления публикации"""
        return reverse('blog:profile', args=[self.request.user.username])


class ProfileListView(ListView):
    """Просмотр профиля пользователя и его публикаций"""

    paginate_by = PAGINATOR_PROFILE
    template_name = 'blog/profile.html'
    model = Post

    def get_object(self):
        """Получение объекта пользователя по имени"""
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        """Получение публикаций пользователя"""
        return self.get_object().posts.all()

    def get_context_data(self, **kwargs):
        """Добавление данных профиля в контекст"""
        return dict(
            **super().get_context_data(**kwargs),
            profile=self.get_object()
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование данных профиля пользователя"""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        """Получение текущего пользователя"""
        return self.request.user

    def get_success_url(self):
        """Перенаправление на профиль пользователя после обновления"""
        return reverse('blog:profile', args=[self.request.user.username])


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария к публикации"""

    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        """Добавление формы комментария в контекст"""
        return dict(**super().get_context_data(**kwargs), form=CommentForm())

    def form_valid(self, form):
        """Назначение текущего пользователя автором и привязка к публикации"""
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправление на страницу публикации после добавления коммента"""
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentMixin(LoginRequiredMixin):
    """Миксин для проверки авторства комментариев"""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        """Перенаправление на страницу публикации после действия с комментом"""
        return reverse('blog:post_detail', args=[self.kwargs['comment_id']])

    def dispatch(self, request, *args, **kwargs):
        """Проверка авторства комментария"""
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        if comment.author != self.request.user:
            return redirect('blog:post_detail',
                            post_id=self.kwargs['comment_id']
                            )
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(CommentMixin, UpdateView):
    """Редактирование комментария"""

    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    """Удаление комментария"""

    ...
