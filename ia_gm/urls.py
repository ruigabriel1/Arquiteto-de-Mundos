"""
URLs para o sistema "Arquiteto de Mundos" - Interface de Mestre IA
"""

from django.urls import path
from . import views

app_name = 'ia_gm'

urlpatterns = [
    # Interface principal
    path('', views.ArquitetoPainelView.as_view(), name='painel'),
    
    # Gestão de sessões
    path('campanha/<int:campanha_id>/criar-sessao/', views.criar_sessao_gm, name='criar_sessao'),
    path('sessao/<int:sessao_id>/', views.SessaoGMView.as_view(), name='sessao'),
    path('sessao/<int:sessao_id>/historico/', views.historico_interacoes, name='historico'),
    path('sessao/<int:sessao_id>/analise/', views.analise_personagem, name='analise_personagem'),
    path('sessao/<int:sessao_id>/biblioteca/', views.biblioteca_conteudo, name='biblioteca'),
    
    # APIs para interação em tempo real
    path('api/gerar-conteudo/', views.api_gerar_conteudo, name='api_gerar_conteudo'),
    path('api/registrar-evento/', views.api_registrar_evento, name='api_registrar_evento'),
    path('api/sugestoes/<int:sessao_id>/', views.api_obter_sugestoes, name='api_sugestoes'),
    path('api/configuracoes/', views.api_atualizar_configuracoes_sessao, name='api_configuracoes'),
    path('api/encerrar-sessao/', views.api_encerrar_sessao, name='api_encerrar_sessao'),
    
    # APIs do modo de jogo
    path('api/ativar-modo-jogo/', views.api_ativar_modo_jogo, name='api_ativar_modo_jogo'),
    path('api/processar-acao/', views.api_processar_acao_jogador, name='api_processar_acao'),
    path('api/status-sessao/<int:sessao_id>/', views.api_status_sessao, name='api_status_sessao'),
    path('api/pausar-sessao/', views.api_pausar_sessao, name='api_pausar_sessao'),
    path('api/retomar-sessao/', views.api_retomar_sessao, name='api_retomar_sessao'),
]