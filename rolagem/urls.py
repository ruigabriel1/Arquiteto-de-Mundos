"""
URLs para API REST de Rolagem de Dados
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RolagemDadoViewSet, TemplateRolagemViewSet

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r'', RolagemDadoViewSet, basename='rolagem')
router.register(r'templates', TemplateRolagemViewSet, basename='template-rolagem')

app_name = 'rolagem'

urlpatterns = [
    # Endpoints principais:
    # GET /api/rolagem/ - Listar rolagens do usuário
    # GET /api/rolagem/{id}/ - Detalhes da rolagem
    # DELETE /api/rolagem/{id}/ - Excluir rolagem
    
    # Actions de rolagem:
    # POST /api/rolagem/rolar/ - Fazer nova rolagem
    # POST /api/rolagem/rolar_atributo/ - Rolar teste de atributo
    # GET /api/rolagem/por_campanha/?campanha_id={id} - Rolagens por campanha
    # GET /api/rolagem/estatisticas/ - Estatísticas do usuário
    
    # Templates:
    # GET/POST /api/rolagem/templates/ - CRUD de templates
    # GET/PUT/DELETE /api/rolagem/templates/{id}/ - Gerenciar template
    # POST /api/rolagem/templates/{id}/usar/ - Usar template para rolagem
    
    path('', include(router.urls)),
]