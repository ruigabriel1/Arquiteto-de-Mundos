"""
Views Django para interface de chat
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from .models import SalaChat, ParticipacaoChat
# from .services import ChatService  # Removido temporariamente


@login_required
def chat_room_view(request, sala_id):
    """
    Renderizar página da sala de chat
    """
    # Verificar se a sala existe
    sala = get_object_or_404(SalaChat, id=sala_id)
    
    # Verificar se o usuário tem acesso à campanha
    if not sala.campanha.participantes.filter(id=request.user.id).exists():
        return HttpResponseForbidden("Você não tem acesso a esta sala de chat.")
    
    # Obter participantes
    participantes = ParticipacaoChat.objects.filter(
        sala=sala
    ).select_related('usuario').order_by('-online', 'usuario__username')
    
    context = {
        'sala': sala,
        'participantes': participantes,
        'user': request.user,
        'campanha': sala.campanha,
    }
    
    return render(request, 'chat/chat_room.html', context)


@login_required
def chat_list_view(request):
    """
    Listar salas de chat disponíveis para o usuário
    """
    # Obter salas de chat do usuário
    salas = SalaChat.objects.filter(
        campanha__participantes=request.user
    ).select_related('campanha').prefetch_related('participacoes')
    
    context = {
        'salas': salas,
        'user': request.user,
    }
    
    return render(request, 'chat/chat_list.html', context)


@login_required
@require_http_methods(["GET"])
def chat_api_status(request, sala_id):
    """
    API para verificar status da sala de chat
    """
    try:
        sala = get_object_or_404(SalaChat, id=sala_id)
        
        # Verificar acesso
        if not sala.campanha.participantes.filter(id=request.user.id).exists():
            return JsonResponse({'error': 'Acesso negado'}, status=403)
        
        # Obter estatísticas
        participantes_online = ParticipacaoChat.objects.filter(
            sala=sala, online=True
        ).count()
        
        total_mensagens = sala.mensagens.count()
        
        return JsonResponse({
            'sala_id': sala.id,
            'nome': sala.nome,
            'participantes_online': participantes_online,
            'total_mensagens': total_mensagens,
            'comandos_habilitados': sala.comandos_habilitados,
            'status': 'ativo' if participantes_online > 0 else 'inativo',
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)