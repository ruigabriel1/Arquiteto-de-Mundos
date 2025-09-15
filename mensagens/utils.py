"""
Funções utilitárias para notificações WebSocket
"""

from typing import List, Dict, Any, Optional
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from usuarios.models import Usuario


def send_notification_to_user(user_id: int, message: str, category: str = 'general', 
                              level: str = 'info', data: Optional[Dict] = None):
    """
    Enviar notificação para um usuário específico
    
    Args:
        user_id: ID do usuário
        message: Mensagem da notificação
        category: Categoria da notificação (general, campaign, character, etc.)
        level: Nível da notificação (info, warning, error, success)
        data: Dados adicionais
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    
    group_name = f'user_notifications_{user_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification',
            'message': message,
            'category': category,
            'level': level,
            'data': data or {},
            'timestamp': timezone.now().isoformat()
        }
    )


def send_notification_to_users(user_ids: List[int], message: str, category: str = 'general',
                               level: str = 'info', data: Optional[Dict] = None):
    """
    Enviar notificação para múltiplos usuários
    
    Args:
        user_ids: Lista de IDs dos usuários
        message: Mensagem da notificação
        category: Categoria da notificação
        level: Nível da notificação
        data: Dados adicionais
    """
    for user_id in user_ids:
        send_notification_to_user(user_id, message, category, level, data)


def send_campaign_invite_notification(user_id: int, campaign_id: int, 
                                      campaign_name: str, inviter_name: str):
    """
    Enviar notificação de convite para campanha
    
    Args:
        user_id: ID do usuário convidado
        campaign_id: ID da campanha
        campaign_name: Nome da campanha
        inviter_name: Nome de quem está convidando
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    
    group_name = f'user_notifications_{user_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'campaign_invite',
            'campaign_id': campaign_id,
            'campaign_name': campaign_name,
            'inviter_name': inviter_name,
            'timestamp': timezone.now().isoformat()
        }
    )


def send_character_update_notification(user_id: int, character_id: int,
                                       character_name: str, update_type: str,
                                       message: str):
    """
    Enviar notificação de atualização de personagem
    
    Args:
        user_id: ID do usuário
        character_id: ID do personagem
        character_name: Nome do personagem
        update_type: Tipo de atualização (level_up, damage, heal, etc.)
        message: Mensagem descritiva
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    
    group_name = f'user_notifications_{user_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'character_update',
            'character_id': character_id,
            'character_name': character_name,
            'update_type': update_type,
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
    )


def send_system_message_to_chat(sala_id: int, message: str, level: str = 'info'):
    """
    Enviar mensagem do sistema para uma sala de chat
    
    Args:
        sala_id: ID da sala de chat
        message: Mensagem do sistema
        level: Nível da mensagem (info, warning, error)
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    
    group_name = f'chat_sala_{sala_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'system_notification',
            'message': message,
            'level': level,
            'timestamp': timezone.now().isoformat()
        }
    )


def notify_user_joined_campaign(campaign_id: int, new_user_id: int, new_user_name: str,
                                participating_users: List[int]):
    """
    Notificar participantes que um novo usuário entrou na campanha
    
    Args:
        campaign_id: ID da campanha
        new_user_id: ID do novo usuário
        new_user_name: Nome do novo usuário
        participating_users: Lista de IDs dos participantes atuais
    """
    message = f"{new_user_name} entrou na campanha!"
    data = {
        'campaign_id': campaign_id,
        'new_user_id': new_user_id,
        'new_user_name': new_user_name
    }
    
    # Notificar todos os participantes exceto o novo usuário
    user_ids_to_notify = [uid for uid in participating_users if uid != new_user_id]
    send_notification_to_users(
        user_ids_to_notify,
        message,
        category='campaign',
        level='info',
        data=data
    )


def notify_user_left_campaign(campaign_id: int, left_user_name: str,
                              remaining_users: List[int]):
    """
    Notificar participantes que um usuário saiu da campanha
    
    Args:
        campaign_id: ID da campanha
        left_user_name: Nome do usuário que saiu
        remaining_users: Lista de IDs dos participantes restantes
    """
    message = f"{left_user_name} saiu da campanha."
    data = {
        'campaign_id': campaign_id,
        'left_user_name': left_user_name
    }
    
    send_notification_to_users(
        remaining_users,
        message,
        category='campaign',
        level='warning',
        data=data
    )


def broadcast_dice_roll_to_chat(sala_id: int, user_name: str, character_name: str,
                                expression: str, result: int, details: str):
    """
    Transmitir resultado de rolagem de dados para o chat
    
    Args:
        sala_id: ID da sala de chat
        user_name: Nome do usuário
        character_name: Nome do personagem (opcional)
        expression: Expressão dos dados
        result: Resultado final
        details: Detalhes da rolagem
    """
    if character_name:
        message = f"{character_name} ({user_name}) rolou {expression}: {result}"
    else:
        message = f"{user_name} rolou {expression}: {result}"
    
    if details:
        message += f" [{details}]"
    
    send_system_message_to_chat(sala_id, message, level='info')


def get_online_users_in_chat(sala_id: int) -> List[int]:
    """
    Obter lista de usuários online em uma sala de chat
    
    Args:
        sala_id: ID da sala de chat
        
    Returns:
        Lista de IDs de usuários online
    """
    from .models import ParticipacaoChat
    
    return list(
        ParticipacaoChat.objects.filter(
            sala_id=sala_id,
            online=True
        ).values_list('usuario_id', flat=True)
    )


def disconnect_user_from_all_chats(user_id: int):
    """
    Marcar usuário como offline em todas as salas de chat
    
    Args:
        user_id: ID do usuário
    """
    from .models import ParticipacaoChat
    
    ParticipacaoChat.objects.filter(
        usuario_id=user_id,
        online=True
    ).update(online=False)