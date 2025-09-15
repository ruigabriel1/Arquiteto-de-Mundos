"""
URLs para API REST de Chat/Mensagens
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SalaChatViewSet, 
    MensagemViewSet, 
    ParticipacaoChatViewSet
)
from .test_views import chat_test_view
from .chat_views import chat_room_view, chat_list_view, chat_api_status

# Criar roteador para as APIs
router = DefaultRouter()
router.register(r'salas', SalaChatViewSet, basename='salachat')
router.register(r'mensagens', MensagemViewSet, basename='mensagem')
router.register(r'participacoes', ParticipacaoChatViewSet, basename='participacaochat')

app_name = 'mensagens'

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
    
    # Interface de chat
    path('chat/<int:sala_id>/', chat_room_view, name='chat_room'),
    path('chat/', chat_list_view, name='chat_list'),
    path('api/chat/<int:sala_id>/status/', chat_api_status, name='chat_status'),
    
    # Página de teste
    path('test/', chat_test_view, name='chat_test'),
]
