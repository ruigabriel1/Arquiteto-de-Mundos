"""
Views básicas do projeto Unified Chronicles
"""

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from campanhas.models import Campanha
from ia_gm.models import SessaoIA, InteracaoIA

def index(request):
    """Página inicial moderna do Unified Chronicles"""
    context = {}
    
    # Se usuário logado, adicionar estatísticas
    if request.user.is_authenticated:
        context.update({
            'total_campanhas': Campanha.objects.filter(organizador=request.user).count(),
            'total_sessoes': SessaoIA.objects.filter(campanha__organizador=request.user).count(),
            'total_interacoes': InteracaoIA.objects.filter(sessao__campanha__organizador=request.user).count(),
        })
    
    return render(request, 'index.html', context)

@login_required
def dashboard_view(request):
    """Redireciona para o dashboard de usuários"""
    return redirect('usuarios:dashboard')

def api_root(request):
    """
    Endpoint raiz da API - informações básicas
    """
    return JsonResponse({
        'message': 'Bem-vindo ao Unified Chronicles API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'usuarios': '/api/usuarios/',
            'campanhas': '/api/campanhas/',
        },
        'documentation': {
            'usuarios': {
                'cadastro': 'POST /api/usuarios/cadastro/',
                'login': 'POST /api/usuarios/login/',
                'logout': 'POST /api/usuarios/logout/',
                'perfil': 'GET /api/usuarios/perfil/',
                'listagem': 'GET /api/usuarios/',
            },
            'campanhas': {
                'listagem': 'GET /api/campanhas/',
                'criar': 'POST /api/campanhas/',
                'detalhes': 'GET /api/campanhas/{id}/',
                'convites': 'GET /api/campanhas/convites/',
            }
        }
    })