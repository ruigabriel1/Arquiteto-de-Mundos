"""
URLs para interface web de usuários
"""

from django.urls import path
from . import web_views

app_name = 'usuarios'

urlpatterns = [
    # Página inicial
    path('', web_views.index_view, name='index'),
    
    # Autenticação
    path('cadastro/', web_views.cadastro_view, name='cadastro'),
    path('login/', web_views.login_view, name='login'),
    path('logout/', web_views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', web_views.dashboard_view, name='dashboard'),
    
    # Perfil e configurações
    path('perfil/', web_views.perfil_view, name='perfil'),
    path('alterar-senha/', web_views.alterar_senha_view, name='alterar_senha'),
    path('configuracoes/', web_views.configuracoes_view, name='configuracoes'),
    
    # Lista de usuários
    path('usuarios/', web_views.usuarios_list_view, name='usuarios_list'),
    path('usuarios/<int:user_id>/', web_views.usuario_detail_view, name='usuario_detail'),
]