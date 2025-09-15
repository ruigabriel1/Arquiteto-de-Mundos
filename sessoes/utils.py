"""
Funções utilitárias para gerenciamento de sessões e participações
"""
from django.db import transaction, models
from django.core.exceptions import ValidationError
from .models import SessionParticipant, SessaoJogo


class SessionParticipationManager:
    """Gerenciador para operações de participação em sessões"""
    
    @staticmethod
    def participar_de_sessao(usuario, personagem, sessao):
        """
        Permite que um usuário participe de uma sessão com um personagem específico.
        
        Args:
            usuario: Instância do modelo Usuario
            personagem: Instância do modelo Personagem
            sessao: Instância do modelo SessaoJogo
            
        Returns:
            SessionParticipant: A participação criada
            
        Raises:
            ValidationError: Se não for possível participar da sessão
        """
        with transaction.atomic():
            # Verificar se a sessão pode aceitar participantes
            if not sessao.pode_aceitar_participante():
                raise ValidationError("A sessão não está aceitando novos participantes.")
            
            # Verificar se o usuário já está participando desta sessão
            participacao_existente = SessionParticipant.objects.filter(
                usuario=usuario,
                sessao=sessao,
                status__in=['ativo', 'aguardando']
            ).first()
            
            if participacao_existente:
                raise ValidationError(
                    "Você já está participando desta sessão com outro personagem."
                )
            
            # Verificar se o personagem já está sendo usado na sessão
            personagem_em_uso = SessionParticipant.objects.filter(
                personagem=personagem,
                sessao=sessao,
                status__in=['ativo', 'aguardando']
            ).first()
            
            if personagem_em_uso:
                raise ValidationError(
                    "Este personagem já está sendo usado nesta sessão."
                )
            
            # Verificar se o usuário é dono do personagem
            if personagem.usuario != usuario:
                raise ValidationError(
                    "Você só pode usar personagens que você criou."
                )
            
            # Verificar se o personagem está ativo
            if not personagem.ativo:
                raise ValidationError(
                    "Este personagem não está disponível para uso."
                )
            
            # Criar a participação
            participacao = SessionParticipant.objects.create(
                usuario=usuario,
                personagem=personagem,
                sessao=sessao,
                status='aguardando'
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
            SessionParticipant: A participação aprovada
            
        Raises:
            ValidationError: Se não for possível aprovar
        """
        try:
            participacao = SessionParticipant.objects.get(id=participacao_id)
        except SessionParticipant.DoesNotExist:
            raise ValidationError("Participação não encontrada.")
        
        # Verificar se quem está aprovando é o mestre da sessão
        if participacao.sessao.mestre != aprovado_por_user:
            raise ValidationError(
                "Apenas o mestre da sessão pode aprovar participações."
            )
        
        # Verificar se ainda há vagas
        if not participacao.sessao.pode_aceitar_participante():
            raise ValidationError("Não há mais vagas disponíveis na sessão.")
        
        # Aprovar
        participacao.aprovar(aprovado_por_user=aprovado_por_user)
        
        return participacao
    
    @staticmethod
    def sair_da_sessao(usuario, sessao, motivo=None):
        """
        Remover um usuário de uma sessão.
        
        Args:
            usuario: Usuário que está saindo
            sessao: Sessão da qual está saindo
            motivo: Motivo opcional para a saída
            
        Returns:
            bool: True se foi possível sair da sessão
        """
        participacao = SessionParticipant.objects.filter(
            usuario=usuario,
            sessao=sessao,
            status__in=['ativo', 'aguardando']
        ).first()
        
        if not participacao:
            return False
        
        participacao.sair_da_sessao()
        
        if motivo:
            participacao.observacoes += f"\nSaída: {motivo}"
            participacao.save()
        
        return True
    
    @staticmethod
    def get_sessoes_do_usuario(usuario, status_filter=None):
        """
        Obter todas as sessões de um usuário.
        
        Args:
            usuario: Usuário
            status_filter: Lista de status para filtrar (opcional)
            
        Returns:
            QuerySet: Participações do usuário
        """
        queryset = SessionParticipant.objects.filter(
            usuario=usuario
        ).select_related('sessao', 'personagem')
        
        if status_filter:
            queryset = queryset.filter(status__in=status_filter)
        
        return queryset
    
    @staticmethod
    def get_participantes_da_sessao(sessao, status_filter=None):
        """
        Obter todos os participantes de uma sessão.
        
        Args:
            sessao: Sessão
            status_filter: Lista de status para filtrar (opcional)
            
        Returns:
            QuerySet: Participantes da sessão
        """
        queryset = SessionParticipant.objects.filter(
            sessao=sessao
        ).select_related('usuario', 'personagem')
        
        if status_filter:
            queryset = queryset.filter(status__in=status_filter)
        
        return queryset
    
    @staticmethod
    def pode_usuario_participar(usuario, sessao):
        """
        Verificar se um usuário pode participar de uma sessão.
        
        Args:
            usuario: Usuário
            sessao: Sessão
            
        Returns:
            dict: Resultado da verificação com 'pode_participar' (bool) e 'motivo' (str)
        """
        # Verificar se a sessão está ativa
        if not sessao.ativa:
            return {
                'pode_participar': False,
                'motivo': 'A sessão não está ativa.'
            }
        
        # Verificar vagas
        if not sessao.pode_aceitar_participante():
            return {
                'pode_participar': False,
                'motivo': 'Não há vagas disponíveis na sessão.'
            }
        
        # Verificar se já está participando
        ja_participando = SessionParticipant.objects.filter(
            usuario=usuario,
            sessao=sessao,
            status__in=['ativo', 'aguardando']
        ).exists()
        
        if ja_participando:
            return {
                'pode_participar': False,
                'motivo': 'Você já está participando desta sessão.'
            }
        
        return {
            'pode_participar': True,
            'motivo': 'Pode participar.'
        }


def get_sessoes_disponiveis(usuario=None):
    """
    Obter todas as sessões que estão aceitando novos participantes.
    
    Args:
        usuario: Usuário para verificar se já está participando (opcional)
        
    Returns:
        QuerySet: Sessões disponíveis
    """
    sessoes = SessaoJogo.objects.filter(ativa=True).annotate(
        participantes_count=models.Count(
            'sessionparticipant',
            filter=models.Q(sessionparticipant__status='ativo')
        )
    ).filter(
        participantes_count__lt=models.F('max_participantes')
    )
    
    if usuario:
        # Excluir sessões onde o usuário já está participando
        sessoes_usuario = SessionParticipant.objects.filter(
            usuario=usuario,
            status__in=['ativo', 'aguardando']
        ).values_list('sessao_id', flat=True)
        
        sessoes = sessoes.exclude(id__in=sessoes_usuario)
    
    return sessoes


def get_personagens_disponiveis_para_usuario(usuario, sessao=None):
    """
    Obter personagens do usuário que estão disponíveis para uso.
    
    Args:
        usuario: Usuário
        sessao: Sessão específica para verificar conflitos (opcional)
        
    Returns:
        QuerySet: Personagens disponíveis
    """
    from personagens.models import Personagem
    
    personagens = Personagem.objects.filter(
        usuario=usuario,
        ativo=True
    )
    
    if sessao:
        # Excluir personagens já sendo usados na sessão
        personagens_em_uso = SessionParticipant.objects.filter(
            sessao=sessao,
            status__in=['ativo', 'aguardando']
        ).values_list('personagem_id', flat=True)
        
        personagens = personagens.exclude(id__in=personagens_em_uso)
    
    return personagens