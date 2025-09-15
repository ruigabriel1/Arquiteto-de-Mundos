"""
Funções utilitárias para gerenciamento de participação em campanhas
"""
from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CampaignParticipant, Campanha


class CampaignParticipationManager:
    """Gerenciador para operações de participação em campanhas"""
    
    @staticmethod
    def participar_de_campanha(usuario, campanha, personagem=None):
        """
        Permite que um usuário se inscreva em uma campanha.
        
        Args:
            usuario: Instância do modelo Usuario
            campanha: Instância do modelo Campanha
            personagem: Instância do modelo Personagem (opcional)
            
        Returns:
            CampaignParticipant: A participação criada
            
        Raises:
            ValidationError: Se não for possível participar da campanha
        """
        with transaction.atomic():
            # Verificar se a campanha pode aceitar participantes
            if not campanha.tem_vagas:
                raise ValidationError(_("A campanha não possui vagas disponíveis."))
            
            # Verificar se a campanha está ativa
            if campanha.estado not in ['planejamento', 'ativa']:
                raise ValidationError(_("A campanha não está aceitando novos participantes."))
            
            # Verificar se o usuário já está participando desta campanha
            participacao_existente = CampaignParticipant.objects.filter(
                usuario=usuario,
                campanha=campanha,
                status__in=['ativo', 'aguardando', 'pendente']
            ).first()
            
            if participacao_existente:
                raise ValidationError(_("Você já está participando desta campanha."))
            
            # Verificar se o personagem já está sendo usado na campanha (se especificado)
            if personagem:
                personagem_em_uso = CampaignParticipant.objects.filter(
                    personagem=personagem,
                    campanha=campanha,
                    status__in=['ativo', 'aguardando']
                ).first()
                
                if personagem_em_uso:
                    raise ValidationError(_("Este personagem já está sendo usado nesta campanha."))
                
                # Verificar se o usuário é dono do personagem
                if personagem.usuario != usuario:
                    raise ValidationError(_("Você só pode usar personagens que você criou."))
                
                # Verificar se o personagem está ativo
                if not personagem.ativo:
                    raise ValidationError(_("Este personagem não está disponível para uso."))
                
                # Verificar compatibilidade do sistema de jogo
                if personagem.sistema_jogo != campanha.sistema_jogo:
                    raise ValidationError(_("O personagem deve ser do mesmo sistema de jogo da campanha."))
            
            # Criar a participação
            status_inicial = 'aguardando' if personagem else 'pendente'
            participacao = CampaignParticipant.objects.create(
                usuario=usuario,
                campanha=campanha,
                personagem=personagem,
                status=status_inicial
            )
            
            return participacao
    
    @staticmethod
    def aprovar_participacao(participacao_id, aprovado_por_user):
        """
        Aprovar uma participação pendente.
        
        Args:
            participacao_id: ID da participação
            aprovado_por_user: Usuário que está aprovando
            
        Returns:
            CampaignParticipant: A participação aprovada
            
        Raises:
            ValidationError: Se não for possível aprovar
        """
        try:
            participacao = CampaignParticipant.objects.get(id=participacao_id)
        except CampaignParticipant.DoesNotExist:
            raise ValidationError(_("Participação não encontrada."))
        
        # Verificar se quem está aprovando é o organizador da campanha
        if participacao.campanha.organizador != aprovado_por_user:
            raise ValidationError(_("Apenas o organizador da campanha pode aprovar participações."))
        
        # Verificar se ainda há vagas
        if not participacao.campanha.tem_vagas:
            raise ValidationError(_("Não há mais vagas disponíveis na campanha."))
        
        # Verificar se tem personagem definido
        if not participacao.personagem:
            raise ValidationError(_("Não é possível aprovar participação sem personagem definido."))
        
        # Aprovar
        participacao.aprovar(aprovado_por_user=aprovado_por_user)
        
        return participacao
    
    @staticmethod
    def definir_personagem(participacao_id, personagem):
        """
        Definir personagem para uma participação pendente.
        
        Args:
            participacao_id: ID da participação
            personagem: Personagem a ser definido
            
        Returns:
            CampaignParticipant: A participação atualizada
            
        Raises:
            ValidationError: Se não for possível definir o personagem
        """
        try:
            participacao = CampaignParticipant.objects.get(id=participacao_id)
        except CampaignParticipant.DoesNotExist:
            raise ValidationError(_("Participação não encontrada."))
        
        # Verificar se o personagem pertence ao usuário da participação
        if personagem.usuario != participacao.usuario:
            raise ValidationError(_("Você só pode usar personagens que você criou."))
        
        # Verificar se o personagem já está sendo usado na campanha
        personagem_em_uso = CampaignParticipant.objects.filter(
            personagem=personagem,
            campanha=participacao.campanha,
            status__in=['ativo', 'aguardando']
        ).exclude(id=participacao.id).first()
        
        if personagem_em_uso:
            raise ValidationError(_("Este personagem já está sendo usado nesta campanha."))
        
        # Definir personagem
        participacao.definir_personagem(personagem)
        
        return participacao
    
    @staticmethod
    def sair_da_campanha(usuario, campanha, motivo=None, removido_por_organizador=False):
        """
        Remover um usuário de uma campanha.
        
        Args:
            usuario: Usuário que está saindo
            campanha: Campanha da qual está saindo
            motivo: Motivo opcional para a saída
            removido_por_organizador: Se foi removido pelo organizador
            
        Returns:
            bool: True se foi possível sair da campanha
        """
        participacao = CampaignParticipant.objects.filter(
            usuario=usuario,
            campanha=campanha,
            status__in=['ativo', 'aguardando', 'pendente']
        ).first()
        
        if not participacao:
            return False
        
        participacao.sair_da_campanha()
        
        if motivo:
            prefixo = "Removido pelo organizador" if removido_por_organizador else "Saída"
            participacao.observacoes += f"\n{prefixo}: {motivo}"
            participacao.save()
        
        return True
    
    @staticmethod
    def get_campanhas_do_usuario(usuario, status_filter=None):
        """
        Obter todas as campanhas de um usuário.
        
        Args:
            usuario: Usuário
            status_filter: Lista de status para filtrar (opcional)
            
        Returns:
            QuerySet: Participações do usuário
        """
        queryset = CampaignParticipant.objects.filter(
            usuario=usuario
        ).select_related('campanha', 'personagem')
        
        if status_filter:
            queryset = queryset.filter(status__in=status_filter)
        
        return queryset
    
    @staticmethod
    def get_participantes_da_campanha(campanha, status_filter=None):
        """
        Obter todos os participantes de uma campanha.
        
        Args:
            campanha: Campanha
            status_filter: Lista de status para filtrar (opcional)
            
        Returns:
            QuerySet: Participantes da campanha
        """
        queryset = CampaignParticipant.objects.filter(
            campanha=campanha
        ).select_related('usuario', 'personagem')
        
        if status_filter:
            queryset = queryset.filter(status__in=status_filter)
        
        return queryset
    
    @staticmethod
    def pode_usuario_participar(usuario, campanha):
        """
        Verificar se um usuário pode participar de uma campanha.
        
        Args:
            usuario: Usuário
            campanha: Campanha
            
        Returns:
            dict: Resultado da verificação com 'pode_participar' (bool) e 'motivo' (str)
        """
        # Verificar se a campanha está aceitando participantes
        if campanha.estado not in ['planejamento', 'ativa']:
            return {
                'pode_participar': False,
                'motivo': _('A campanha não está aceitando novos participantes.')
            }
        
        # Verificar vagas
        if not campanha.tem_vagas:
            return {
                'pode_participar': False,
                'motivo': _('Não há vagas disponíveis na campanha.')
            }
        
        # Verificar se é o organizador
        if campanha.organizador == usuario:
            return {
                'pode_participar': False,
                'motivo': _('Você é o organizador desta campanha.')
            }
        
        # Verificar se já está participando
        ja_participando = CampaignParticipant.objects.filter(
            usuario=usuario,
            campanha=campanha,
            status__in=['ativo', 'aguardando', 'pendente']
        ).exists()
        
        if ja_participando:
            return {
                'pode_participar': False,
                'motivo': _('Você já está participando desta campanha.')
            }
        
        return {
            'pode_participar': True,
            'motivo': _('Pode participar.')
        }
    
    @staticmethod
    def get_status_participacao(usuario, campanha):
        """
        Obter o status de participação de um usuário em uma campanha.
        
        Args:
            usuario: Usuário
            campanha: Campanha
            
        Returns:
            dict: Status da participação
        """
        participacao = CampaignParticipant.objects.filter(
            usuario=usuario,
            campanha=campanha
        ).first()
        
        if not participacao:
            return {
                'participando': False,
                'status': None,
                'personagem': None,
                'pode_definir_personagem': False
            }
        
        return {
            'participando': True,
            'status': participacao.status,
            'personagem': participacao.personagem,
            'pode_definir_personagem': participacao.precisa_personagem,
            'aguardando_aprovacao': participacao.aguardando_aprovacao,
            'pode_jogar': participacao.pode_jogar
        }


def get_campanhas_publicas(usuario=None):
    """
    Obter todas as campanhas públicas disponíveis para participação.
    
    Args:
        usuario: Usuário para filtrar campanhas já participando (opcional)
        
    Returns:
        QuerySet: Campanhas disponíveis
    """
    campanhas = Campanha.objects.filter(
        estado__in=['planejamento', 'ativa']
    ).annotate(
        participantes_count=models.Count(
            'participantes_personagens',
            filter=models.Q(participantes_personagens__status='ativo')
        )
    ).filter(
        participantes_count__lt=models.F('max_jogadores')
    ).select_related('organizador', 'sistema_jogo')
    
    if usuario:
        # Excluir campanhas onde o usuário é organizador
        campanhas = campanhas.exclude(organizador=usuario)
        
        # Excluir campanhas onde o usuário já está participando
        campanhas_usuario = CampaignParticipant.objects.filter(
            usuario=usuario,
            status__in=['ativo', 'aguardando', 'pendente']
        ).values_list('campanha_id', flat=True)
        
        campanhas = campanhas.exclude(id__in=campanhas_usuario)
    
    return campanhas.order_by('-data_atualizacao')


def get_personagens_compativeis_campanha(usuario, campanha):
    """
    Obter personagens do usuário que são compatíveis com uma campanha.
    
    Args:
        usuario: Usuário
        campanha: Campanha
        
    Returns:
        QuerySet: Personagens compatíveis
    """
    from personagens.models import Personagem
    
    personagens = Personagem.objects.filter(
        usuario=usuario,
        ativo=True,
        sistema_jogo=campanha.sistema_jogo
    )
    
    # Excluir personagens já sendo usados em outras campanhas ativas
    personagens_em_uso = CampaignParticipant.objects.filter(
        status__in=['ativo', 'aguardando'],
        personagem__isnull=False
    ).values_list('personagem_id', flat=True)
    
    personagens = personagens.exclude(id__in=personagens_em_uso)
    
    return personagens.order_by('nome')


def get_campanhas_organizadas_pelo_usuario(usuario):
    """
    Obter campanhas organizadas por um usuário.
    
    Args:
        usuario: Usuário organizador
        
    Returns:
        QuerySet: Campanhas organizadas
    """
    return Campanha.objects.filter(
        organizador=usuario
    ).annotate(
        participantes_ativos=models.Count(
            'participantes_personagens',
            filter=models.Q(participantes_personagens__status='ativo')
        )
    ).select_related('sistema_jogo').order_by('-data_atualizacao')