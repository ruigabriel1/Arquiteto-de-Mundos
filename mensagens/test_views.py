"""
Views para testes do sistema de chat
"""

from django.shortcuts import render
from django.http import HttpResponse

def chat_test_view(request):
    """View simples para testar o WebSocket chat"""
    return render(request, 'chat_test.html')