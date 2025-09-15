"""
Consumers WebSocket para Chat/Mensagens em Tempo Real
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from .models import SalaChat, ParticipacaoChat, Mensagem, TipoMensagem
from .serializers import MensagemDetailSerializer, ParticipacaoChatSerializer
from usuarios.models import Usuario
from personagens.models import Personagem

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer para chat em tempo real por sala
    
    Gerencia conexões WebSocket para salas de chat específicas,
    permitindo mensagens em tempo real, comandos RPG e notificações
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sala_id = None
        self.sala_group_name = None
        self.user = None
        self.sala = None
        self.participacao = None
    
    async def connect(self):
        """Conectar usuário à sala de chat"""
        self.sala_id = self.scope['url_route']['kwargs']['sala_id']
        self.sala_group_name = f'chat_sala_{self.sala_id}'
        self.user = self.scope.get('user')
        
        # Verificar autenticação
        if isinstance(self.user, AnonymousUser):
            logger.warning(f"Tentativa de conexão anônima à sala {self.sala_id}")
            await self.close(code=4001)
            return
        
        # Verificar acesso à sala
        try:
            self.sala, self.participacao = await self.verificar_acesso_sala()
        except ObjectDoesNotExist:
            logger.warning(f"Usuário {self.user.id} tentou acessar sala inexistente {self.sala_id}")
            await self.close(code=4004)
            return
        except PermissionError:
            logger.warning(f"Usuário {self.user.id} sem permissão para sala {self.sala_id}")
            await self.close(code=4003)
            return
        
        # Aceitar conexão WebSocket
        await self.accept()
        
        # Entrar no grupo da sala
        await self.channel_layer.group_add(
            self.sala_group_name,
            self.channel_name
        )
        
        # Marcar usuário como online
        await self.marcar_usuario_online(True)
        
        # Notificar outros usuários que entrou na sala
        await self.channel_layer.group_send(
            self.sala_group_name,
            {
                'type': 'usuario_status',
                'action': 'entrou',
                'usuario_id': self.user.id,
                'usuario_nome': await self.get_usuario_nome(),
                'timestamp': timezone.now().isoformat()
            }
        )
        
        logger.info(f"Usuário {self.user.username} conectou à sala {self.sala_id}")
    
    async def disconnect(self, close_code):
        """Desconectar usuário da sala de chat"""
        if hasattr(self, 'sala_group_name') and self.sala_group_name:
            # Marcar usuário como offline
            await self.marcar_usuario_online(False)
            
            # Notificar outros usuários que saiu da sala
            await self.channel_layer.group_send(
                self.sala_group_name,
                {
                    'type': 'usuario_status',
                    'action': 'saiu',
                    'usuario_id': self.user.id if self.user else None,
                    'usuario_nome': await self.get_usuario_nome() if self.user else 'Usuário',
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            # Sair do grupo da sala
            await self.channel_layer.group_discard(
                self.sala_group_name,
                self.channel_name
            )
        
        logger.info(f"Usuário desconectou da sala {self.sala_id} (código: {close_code})")
    
    async def receive(self, text_data):
        """Receber mensagem do WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'send_message':
                await self.handle_send_message(data)
            elif action == 'execute_command':
                await self.handle_execute_command(data)
            elif action == 'typing':
                await self.handle_typing(data)
            elif action == 'mark_read':
                await self.handle_mark_read(data)
            elif action == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            else:
                await self.send_error(f"Ação '{action}' não reconhecida")
        
        except json.JSONDecodeError:
            await self.send_error("Formato JSON inválido")
        except Exception as e:
            logger.exception(f"Erro ao processar mensagem WebSocket: {e}")
            await self.send_error("Erro interno do servidor")
    
    async def handle_send_message(self, data):
        """Processar envio de mensagem"""
        conteudo = data.get('message', '').strip()
        personagem_id = data.get('personagem_id')
        destinatario_username = data.get('destinatario_username')
        
        if not conteudo:
            await self.send_error("Mensagem não pode estar vazia")
            return
        
        try:
            # Validar personagem se fornecido
            personagem = None
            if personagem_id:
                personagem = await self.get_personagem(personagem_id)
                if not personagem:
                    await self.send_error("Personagem não encontrado")
                    return
            
            # Validar destinatário se fornecido
            destinatario = None
            if destinatario_username:
                destinatario = await self.get_destinatario(destinatario_username)
                if not destinatario:
                    await self.send_error("Destinatário não encontrado")
                    return
            
            # Criar mensagem
            mensagem = await self.criar_mensagem(
                conteudo=conteudo,
                personagem=personagem,
                destinatario=destinatario
            )
            
            # Processar comando se necessário
            if conteudo.startswith('/'):
                resultado = await self.processar_comando(mensagem)
                if resultado and 'erro' in resultado:
                    await self.send_error(resultado['erro'])
                    return
            
            # Serializar mensagem
            mensagem_data = await self.serializar_mensagem(mensagem)
            
            # Determinar destinatários
            if mensagem.tipo == TipoMensagem.WHISPER:
                # Enviar whisper apenas para remetente e destinatário
                await self.enviar_whisper(mensagem_data, destinatario)
            else:
                # Enviar para toda a sala
                await self.channel_layer.group_send(
                    self.sala_group_name,
                    {
                        'type': 'chat_message',
                        'mensagem': mensagem_data
                    }
                )
            
            # Atualizar contador de mensagens não lidas
            await self.atualizar_mensagens_nao_lidas(mensagem)
        
        except Exception as e:
            logger.exception(f"Erro ao enviar mensagem: {e}")
            await self.send_error("Erro ao enviar mensagem")
    
    async def handle_execute_command(self, data):
        """Processar execução de comando"""
        comando = data.get('command', '').strip()
        personagem_id = data.get('personagem_id')
        
        if not comando or not comando.startswith('/'):
            await self.send_error("Comando inválido")
            return
        
        try:
            # Validar personagem se fornecido
            personagem = None
            if personagem_id:
                personagem = await self.get_personagem(personagem_id)
        
            # Criar mensagem de comando
            mensagem = await self.criar_mensagem(
                conteudo=comando,
                personagem=personagem
            )
            
            # Processar comando
            resultado = await self.processar_comando(mensagem)
            if resultado and 'erro' in resultado:
                await self.send_error(resultado['erro'])
                return
            
            # Serializar e enviar resultado
            mensagem_data = await self.serializar_mensagem(mensagem)
            await self.channel_layer.group_send(
                self.sala_group_name,
                {
                    'type': 'chat_message',
                    'mensagem': mensagem_data
                }
            )
        
        except Exception as e:
            logger.exception(f"Erro ao executar comando: {e}")
            await self.send_error("Erro ao executar comando")
    
    async def handle_typing(self, data):
        """Processar indicação de digitação"""
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.sala_group_name,
            {
                'type': 'user_typing',
                'usuario_id': self.user.id,
                'usuario_nome': await self.get_usuario_nome(),
                'is_typing': is_typing
            }
        )
    
    async def handle_mark_read(self, data):
        """Marcar mensagens como lidas"""
        await self.marcar_mensagens_lidas()
        await self.send(text_data=json.dumps({
            'type': 'messages_marked_read',
            'timestamp': timezone.now().isoformat()
        }))
    
    # Handlers para mensagens do grupo
    
    async def chat_message(self, event):
        """Enviar mensagem de chat para WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'mensagem': event['mensagem']
        }))
    
    async def usuario_status(self, event):
        """Notificar mudança de status do usuário"""
        # Não enviar notificação para o próprio usuário
        if event['usuario_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_status',
                'action': event['action'],
                'usuario_id': event['usuario_id'],
                'usuario_nome': event['usuario_nome'],
                'timestamp': event['timestamp']
            }))
    
    async def user_typing(self, event):
        """Notificar que usuário está digitando"""
        # Não enviar notificação para o próprio usuário
        if event['usuario_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_typing',
                'usuario_id': event['usuario_id'],
                'usuario_nome': event['usuario_nome'],
                'is_typing': event['is_typing']
            }))
    
    async def system_notification(self, event):
        """Enviar notificação do sistema"""
        await self.send(text_data=json.dumps({
            'type': 'system_notification',
            'message': event['message'],
            'level': event.get('level', 'info'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))
    
    # Métodos auxiliares
    
    async def send_error(self, message: str):
        """Enviar mensagem de erro"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def enviar_whisper(self, mensagem_data: Dict, destinatario: Usuario):
        """Enviar whisper para remetente e destinatário"""
        # Enviar para o remetente
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'mensagem': mensagem_data
        }))
        
        # Enviar para o destinatário (se estiver online na sala)
        await self.channel_layer.group_send(
            self.sala_group_name,
            {
                'type': 'whisper_message',
                'mensagem': mensagem_data,
                'destinatario_id': destinatario.id
            }
        )
    
    async def whisper_message(self, event):
        """Receber whisper se for o destinatário"""
        if event['destinatario_id'] == self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'mensagem': event['mensagem']
            }))
    
    # Métodos de banco de dados (database_sync_to_async)
    
    @database_sync_to_async
    def verificar_acesso_sala(self):
        """Verificar se usuário tem acesso à sala"""
        try:
            sala = SalaChat.objects.get(id=self.sala_id)
            
            # Verificar se usuário é participante da campanha
            if not sala.campanha.participantes.filter(id=self.user.id).exists():
                raise PermissionError("Usuário não é participante da campanha")
            
            # Obter ou criar participação
            participacao, created = ParticipacaoChat.objects.get_or_create(
                sala=sala,
                usuario=self.user,
                defaults={
                    'primeira_conexao': timezone.now(),
                    'online': True
                }
            )
            
            return sala, participacao
            
        except SalaChat.DoesNotExist:
            raise ObjectDoesNotExist("Sala de chat não encontrada")
    
    @database_sync_to_async
    def marcar_usuario_online(self, online: bool):
        """Marcar usuário como online/offline"""
        if self.participacao:
            self.participacao.online = online
            if online:
                self.participacao.ultima_conexao = timezone.now()
            self.participacao.save()
    
    @database_sync_to_async
    def get_usuario_nome(self) -> str:
        """Obter nome do usuário"""
        if self.user:
            return self.user.get_full_name() or self.user.username
        return "Usuário"
    
    @database_sync_to_async
    def get_personagem(self, personagem_id: int):
        """Obter personagem do usuário"""
        try:
            return Personagem.objects.get(
                id=personagem_id,
                usuario=self.user
            )
        except Personagem.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_destinatario(self, username: str):
        """Obter usuário destinatário"""
        try:
            return Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            return None
    
    @database_sync_to_async
    def criar_mensagem(self, conteudo: str, personagem=None, destinatario=None):
        """Criar nova mensagem"""
        return Mensagem.objects.create(
            sala=self.sala,
            usuario=self.user,
            personagem=personagem,
            destinatario=destinatario,
            conteudo=conteudo
        )
    
    @database_sync_to_async
    def processar_comando(self, mensagem: Mensagem):
        """Processar comando da mensagem"""
        return mensagem.processar_comando()
    
    @database_sync_to_async
    def serializar_mensagem(self, mensagem: Mensagem) -> Dict[str, Any]:
        """Serializar mensagem para envio"""
        # Refresh da mensagem para pegar dados atualizados
        mensagem.refresh_from_db()
        serializer = MensagemDetailSerializer(mensagem)
        return serializer.data
    
    @database_sync_to_async
    def marcar_mensagens_lidas(self):
        """Marcar todas as mensagens como lidas"""
        if self.participacao:
            self.participacao.mensagens_nao_lidas = 0
            self.participacao.ultima_mensagem_vista = timezone.now()
            self.participacao.save()
    
    @database_sync_to_async
    def atualizar_mensagens_nao_lidas(self, mensagem: Mensagem):
        """Atualizar contador de mensagens não lidas para outros participantes"""
        outros_participantes = ParticipacaoChat.objects.filter(
            sala=self.sala
        ).exclude(usuario=self.user)
        
        for participacao in outros_participantes:
            if participacao.ultima_mensagem_vista < mensagem.timestamp:
                participacao.mensagens_nao_lidas += 1
                participacao.save()


class NotificacaoConsumer(AsyncWebsocketConsumer):
    """
    Consumer para notificações gerais do usuário
    
    Gerencia notificações de sistema, convites para campanhas,
    atualizações de personagens, etc.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.user_group_name = None
    
    async def connect(self):
        """Conectar usuário às notificações"""
        self.user = self.scope.get('user')
        
        # Verificar autenticação
        if isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            return
        
        self.user_group_name = f'user_notifications_{self.user.id}'
        
        # Aceitar conexão
        await self.accept()
        
        # Entrar no grupo de notificações do usuário
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        logger.info(f"Usuário {self.user.username} conectou às notificações")
    
    async def disconnect(self, close_code):
        """Desconectar das notificações"""
        if hasattr(self, 'user_group_name') and self.user_group_name:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        
        logger.info(f"Usuário desconectou das notificações (código: {close_code})")
    
    async def receive(self, text_data):
        """Receber mensagem do WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            else:
                await self.send_error(f"Ação '{action}' não reconhecida")
        
        except json.JSONDecodeError:
            await self.send_error("Formato JSON inválido")
        except Exception as e:
            logger.exception(f"Erro ao processar notificação: {e}")
            await self.send_error("Erro interno do servidor")
    
    # Handlers para tipos de notificação
    
    async def notification(self, event):
        """Enviar notificação geral"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'category': event.get('category', 'general'),
            'level': event.get('level', 'info'),
            'data': event.get('data', {}),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))
    
    async def campaign_invite(self, event):
        """Notificar convite para campanha"""
        await self.send(text_data=json.dumps({
            'type': 'campaign_invite',
            'campaign_id': event['campaign_id'],
            'campaign_name': event['campaign_name'],
            'inviter_name': event['inviter_name'],
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))
    
    async def character_update(self, event):
        """Notificar atualização de personagem"""
        await self.send(text_data=json.dumps({
            'type': 'character_update',
            'character_id': event['character_id'],
            'character_name': event['character_name'],
            'update_type': event['update_type'],
            'message': event['message'],
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))
    
    async def send_error(self, message: str):
        """Enviar mensagem de erro"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }))