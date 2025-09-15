"""
URLs para interface web de campanhas e participação
"""

from django.urls import path, include
from .views import (
    campanhas_publicas_view,
    detalhes_campanha_view,
    participar_campanha_view,
    definir_personagem_view,
    sair_campanha_view,
    minhas_campanhas_view,
    gerenciar_campanha_view,
    aprovar_participacao_view,
    rejeitar_participacao_view,
    remover_participante_view,
    criar_campanha_view,
    ajax_personagens_compativeis,
)

app_name = 'campanhas'

urlpatterns = [
    # Interface web principal
    path('', campanhas_publicas_view, name='publicas'),
    path('minhas/', minhas_campanhas_view, name='minhas'),
    path('criar/', criar_campanha_view, name='criar'),
    path('<int:campanha_id>/', detalhes_campanha_view, name='detalhes'),
    
    # Participação
    path('<int:campanha_id>/participar/', participar_campanha_view, name='participar'),
    path('<int:campanha_id>/definir-personagem/', definir_personagem_view, name='definir_personagem'),
    path('<int:campanha_id>/sair/', sair_campanha_view, name='sair'),
    
    # Gerenciamento (organizadores)
    path('<int:campanha_id>/gerenciar/', gerenciar_campanha_view, name='gerenciar'),
    path('participacao/<int:participacao_id>/aprovar/', aprovar_participacao_view, name='aprovar_participacao'),
    path('participacao/<int:participacao_id>/rejeitar/', rejeitar_participacao_view, name='rejeitar_participacao'),
    path('participacao/<int:participacao_id>/remover/', remover_participante_view, name='remover_participante'),
    
    # AJAX endpoints
    path('<int:campanha_id>/personagens-compativeis/', ajax_personagens_compativeis, name='personagens_compativeis'),
    
    # API REST (endpoints existentes preservados)
    # path('api/', include('campanhas.api_urls')),  # Será criado posteriormente se necessário
]
