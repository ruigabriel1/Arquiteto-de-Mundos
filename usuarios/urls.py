"""
URLs para API REST de usuários
"""

from django.urls import path
from .views import (
    UsuarioCreateView, UsuarioProfileView, UsuarioListView, UsuarioDetailView,
    login_view, logout_view, alterar_senha_view, estatisticas_view,
    atualizar_configuracoes_view
)

app_name = 'usuarios_api'

urlpatterns = [
    # Autenticação
    path('register/', UsuarioCreateView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('alterar-senha/', alterar_senha_view, name='alterar_senha'),
    
    # Perfil
    path('profile/', UsuarioProfileView.as_view(), name='profile'),
    path('estatisticas/', estatisticas_view, name='estatisticas'),
    path('configuracoes/', atualizar_configuracoes_view, name='configuracoes'),
    
    # Usuários
    path('', UsuarioListView.as_view(), name='list'),
    path('<int:pk>/', UsuarioDetailView.as_view(), name='detail'),
]