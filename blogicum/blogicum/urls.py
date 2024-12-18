'''Подключила обработчики 404 и 500.
Добавила пути для встроенных стр авторизации, регистрации, изменения пароля.
'''

from django.contrib import admin

from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
