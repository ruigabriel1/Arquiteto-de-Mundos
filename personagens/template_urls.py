"""
URLs para views de templates de Personagens
"""

from django.urls import path
from . import template_views

app_name = 'personagens_web'

urlpatterns = [
    # Lista de personagens
    path('', template_views.listar_personagens, name='listar'),
    
    # Criar novo personagem
    path('criar/', template_views.criar_personagem, name='criar'),
    path('criar/avancado/', template_views.criar_personagem_avancado, name='criar_avancado'),
    
    # Detalhes do personagem
    path('<int:pk>/', template_views.detalhe_personagem, name='detalhe'),
    
    # Editar personagem
    path('<int:pk>/editar/', template_views.editar_personagem, name='editar'),
    
    # Deletar personagem
    path('<int:pk>/deletar/', template_views.deletar_personagem, name='deletar'),
    
    # AJAX endpoints
    path('ajax/racas/', template_views.buscar_racas_por_sistema, name='ajax_racas'),
    path('ajax/classes/', template_views.buscar_classes_por_sistema, name='ajax_classes'),
]
