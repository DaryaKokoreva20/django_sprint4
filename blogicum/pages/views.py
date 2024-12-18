'''Создала обработчик csrf_failure и обработчики для ошибок 404 и 500'''

from django.shortcuts import render


def about(request):
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    template = 'pages/rules.html'
    return render(request, template)


def csrf_failure(request, reason=""):
    return render(request, 'pages/403_csrf.html', status=403)


def custom_404(request, exception):
    return render(request, 'pages/404.html', status=404)


def custom_500(request):
    return render(request, 'pages/500.html', status=500)
