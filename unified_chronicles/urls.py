"""
URL configuration for unified_chronicles project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import render

def home(request):
    return JsonResponse({
        'message': 'Unified Chronicles - Arquiteto de Mundos',
        'status': 'online',
        'version': '1.0.0'
    })

def health_check(request):
    return JsonResponse({'status': 'healthy'})

urlpatterns = [
    path('', home, name='home'),
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/', home, name='api_root'),
]
