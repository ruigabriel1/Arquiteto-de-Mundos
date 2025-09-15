"""
URLs para Personagens - Views tradicionais e APIs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import PersonagemViewSet
from . import api_views, template_views

# Configurar router para ViewSet da API REST
router = DefaultRouter()
router.register(r'api', PersonagemViewSet, basename='personagem-api')

app_name = 'personagens'

urlpatterns = [
    # Views de Templates (Interface Web)
    path('', template_views.listar_personagens, name='listar'),
    path('criar/', template_views.criar_personagem, name='criar'),
    path('criar/avancado/', template_views.criar_personagem_avancado, name='criar_avancado'),
    path('<int:pk>/', template_views.detalhe_personagem, name='detalhe'),
    path('<int:pk>/editar/', template_views.editar_personagem, name='editar'),
    path('<int:pk>/deletar/', template_views.deletar_personagem, name='deletar'),
    
    # APIs para construção dinâmica de personagens
    path('api/sistemas/', api_views.listar_sistemas, name='api_sistemas'),
    path('api/sistema-conteudo/<str:sistema_slug>/', api_views.sistema_conteudo, name='api_sistema_conteudo'),
    path('api/raca/<int:raca_id>/', api_views.detalhes_raca, name='api_detalhes_raca'),
    path('api/classe/<int:classe_id>/', api_views.detalhes_classe, name='api_detalhes_classe'),
    
    # API REST (ViewSet) - endpoints avançados
    # GET /personagens/api/ - Listar personagens
    # POST /personagens/api/ - Criar personagem
    # GET /personagens/api/{id}/ - Detalhes do personagem
    # PUT/PATCH /personagens/api/{id}/ - Atualizar personagem
    # DELETE /personagens/api/{id}/ - Excluir personagem
    # Actions customizadas: historico, backups, restaurar_backup, curar, causar_dano, subir_nivel, etc.
    path('', include(router.urls)),
]
