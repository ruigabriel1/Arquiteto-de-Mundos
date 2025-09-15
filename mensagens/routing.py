"""
Roteamento WebSocket para Chat/Mensagens
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Conectar a uma sala de chat específica
    re_path(r'ws/chat/sala/(?P<sala_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    
    # Notificações gerais do usuário 
    re_path(r'ws/notificacoes/$', consumers.NotificacaoConsumer.as_asgi()),
]