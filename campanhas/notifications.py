"""
Sistema de notificações para campanhas
"""
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class CampaignNotificationManager:
    """Gerenciador de notificações para campanhas"""
    
    @staticmethod
    def notify_participation_approved(participacao):
        """
        Notificar usuário sobre aprovação de participação
        
        Args:
            participacao: CampaignParticipant aprovado
        """
        try:
            usuario = participacao.usuario
            campanha = participacao.campanha
            
            # Log da notificação
            logger.info(
                f"Notificando aprovação de participação: {usuario.username} em {campanha.nome}"
            )
            
            # TODO: Em uma implementação completa, isso poderia:
            # - Criar entrada no banco de notificações
            # - Enviar email
            # - Enviar notificação push
            # - Criar entrada no feed de atividades
            
            # Por enquanto, apenas log
            print(f"✅ NOTIFICAÇÃO: {usuario.nome_completo or usuario.username} foi aprovado na campanha '{campanha.nome}'")
            
        except Exception as e:
            logger.error(f"Erro ao notificar aprovação: {e}")
    
    @staticmethod
    def notify_participation_rejected(participacao, motivo=None):
        """
        Notificar usuário sobre rejeição de participação
        
        Args:
            participacao: CampaignParticipant rejeitado
            motivo: Motivo da rejeição (opcional)
        """
        try:
            usuario = participacao.usuario
            campanha = participacao.campanha
            
            logger.info(
                f"Notificando rejeição de participação: {usuario.username} em {campanha.nome}"
            )
            
            motivo_texto = f" Motivo: {motivo}" if motivo else ""
            print(f"❌ NOTIFICAÇÃO: Sua inscrição na campanha '{campanha.nome}' foi rejeitada.{motivo_texto}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar rejeição: {e}")
    
    @staticmethod
    def notify_new_participant_request(campanha, participacao):
        """
        Notificar organizador sobre nova solicitação de participação
        
        Args:
            campanha: Campanha
            participacao: Nova participação solicitada
        """
        try:
            organizador = campanha.organizador
            usuario = participacao.usuario
            
            logger.info(
                f"Notificando organizador sobre nova participação: {usuario.username} em {campanha.nome}"
            )
            
            print(f"📢 NOTIFICAÇÃO ORGANIZADOR: {usuario.nome_completo or usuario.username} solicitou participação na campanha '{campanha.nome}'")
            
        except Exception as e:
            logger.error(f"Erro ao notificar organizador: {e}")
    
    @staticmethod
    def notify_participant_left(campanha, usuario, motivo=None):
        """
        Notificar organizador sobre saída de participante
        
        Args:
            campanha: Campanha
            usuario: Usuário que saiu
            motivo: Motivo da saída (opcional)
        """
        try:
            organizador = campanha.organizador
            
            logger.info(
                f"Notificando saída de participante: {usuario.username} de {campanha.nome}"
            )
            
            motivo_texto = f" Motivo: {motivo}" if motivo else ""
            print(f"👋 NOTIFICAÇÃO ORGANIZADOR: {usuario.nome_completo or usuario.username} saiu da campanha '{campanha.nome}'.{motivo_texto}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar saída: {e}")
    
    @staticmethod
    def notify_campaign_created(campanha):
        """
        Notificar sobre criação de nova campanha (para admins ou feed público)
        
        Args:
            campanha: Nova campanha criada
        """
        try:
            organizador = campanha.organizador
            
            logger.info(f"Nova campanha criada: {campanha.nome} por {organizador.username}")
            
            print(f"🆕 CAMPANHA CRIADA: '{campanha.nome}' por {organizador.nome_completo or organizador.username}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar criação de campanha: {e}")
    
    @staticmethod
    def add_flash_message(request, nivel, mensagem):
        """
        Adicionar mensagem flash para o usuário
        
        Args:
            request: Request do Django
            nivel: Nível da mensagem (success, info, warning, error)
            mensagem: Texto da mensagem
        """
        try:
            if nivel == 'success':
                messages.success(request, mensagem)
            elif nivel == 'info':
                messages.info(request, mensagem)
            elif nivel == 'warning':
                messages.warning(request, mensagem)
            elif nivel == 'error':
                messages.error(request, mensagem)
            else:
                messages.info(request, mensagem)
                
        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem flash: {e}")


def notify_participation_approved(participacao):
    """
    Função auxiliar para notificar aprovação de participação
    Pode ser chamada de qualquer lugar do código
    """
    CampaignNotificationManager.notify_participation_approved(participacao)


def notify_participation_rejected(participacao, motivo=None):
    """
    Função auxiliar para notificar rejeição de participação
    """
    CampaignNotificationManager.notify_participation_rejected(participacao, motivo)


def notify_new_participant_request(campanha, participacao):
    """
    Função auxiliar para notificar organizador sobre nova solicitação
    """
    CampaignNotificationManager.notify_new_participant_request(campanha, participacao)


def notify_participant_left(campanha, usuario, motivo=None):
    """
    Função auxiliar para notificar organizador sobre saída
    """
    CampaignNotificationManager.notify_participant_left(campanha, usuario, motivo)


def notify_campaign_created(campanha):
    """
    Função auxiliar para notificar criação de campanha
    """
    CampaignNotificationManager.notify_campaign_created(campanha)