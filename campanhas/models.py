"""
Modelos para gerenciamento de campanhas de RPG
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class Campanha(models.Model):
    """Campanhas de RPG"""
    
    ESTADOS_CAMPANHA = [
        ('planejamento', _("Em Planejamento")),
        ('ativa', _("Ativa")),
        ('pausada', _("Pausada")),
        ('finalizada', _("Finalizada")),
        ('cancelada', _("Cancelada")),
    ]
    
    nome = models.CharField(
        _("Nome"),
        max_length=100,
        help_text=_("Nome da campanha")
    )
    
    descricao = models.TextField(
        _("Descrição"),
        help_text=_("Descrição e sinôpse da campanha")
    )
    
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='campanhas_organizadas',
        verbose_name=_("Organizador")
    )
    
    # TODO: Remover em migração futura - campo legado
    # mestre = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name='campanhas_mestradas_legacy',
    #     verbose_name=_("Mestre (Legado)"),
    #     null=True,
    #     blank=True
    # )
    
    jogadores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ParticipacaoCampanha',
        related_name='campanhas_participando',
        verbose_name=_("Jogadores")
    )
    
    sistema_jogo = models.ForeignKey(
        'sistema_unificado.SistemaJogo',
        on_delete=models.PROTECT,
        verbose_name=_("Sistema de Jogo")
    )
    
    nivel_inicial = models.PositiveSmallIntegerField(
        _("Nível Inicial"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text=_("Nível inicial dos personagens")
    )
    
    nivel_maximo = models.PositiveSmallIntegerField(
        _("Nível Máximo"),
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text=_("Nível máximo da campanha")
    )
    
    max_jogadores = models.PositiveSmallIntegerField(
        _("Máx. Jogadores"),
        default=6,
        validators=[MinValueValidator(2), MaxValueValidator(10)],
        help_text=_("Número máximo de jogadores")
    )
    
    # Configurações da IA GM
    ia_ativa = models.BooleanField(
        _("IA GM Ativa"),
        default=True,
        help_text=_("Usar IA como Game Master")
    )
    
    configuracoes_ia = models.JSONField(
        _("Configurações da IA"),
        default=dict,
        help_text=_("Configurações comportamentais da IA GM")
    )
    
    personalidade_gm = models.JSONField(
        _("Personalidade do GM"),
        default=dict,
        help_text=_("Traços de personalidade do GM artificial")
    )
    
    # Estado da campanha
    estado = models.CharField(
        _("Estado"),
        max_length=20,
        choices=ESTADOS_CAMPANHA,
        default='planejamento'
    )
    
    # Datas importantes
    data_criacao = models.DateTimeField(
        _("Data de Criação"),
        auto_now_add=True
    )
    
    data_inicio = models.DateTimeField(
        _("Data de Início"),
        null=True,
        blank=True,
        help_text=_("Data da primeira sessão")
    )
    
    data_ultima_sessao = models.DateTimeField(
        _("Última Sessão"),
        null=True,
        blank=True
    )
    
    data_atualizacao = models.DateTimeField(
        _("Última Atualização"),
        auto_now=True
    )
    
    # Configurações adicionais
    configuracoes_gerais = models.JSONField(
        _("Configurações Gerais"),
        default=dict,
        help_text=_("Regras da casa e configurações especiais")
    )
    
    class Meta:
        verbose_name = _("Campanha")
        verbose_name_plural = _("Campanhas")
        ordering = ['-data_atualizacao']
    
    def __str__(self):
        return f"{self.nome} (organizada por {self.organizador.username})"
    
    @property
    def num_jogadores(self):
        """Número atual de jogadores ativos"""
        return self.participacoes.filter(ativo=True).count()
    
    @property
    def tem_vagas(self):
        """Verifica se há vagas disponíveis"""
        return self.num_jogadores < self.max_jogadores
    
    @property
    def duracao_dias(self):
        """Duração da campanha em dias"""
        if not self.data_inicio:
            return 0
        fim = self.data_ultima_sessao or timezone.now()
        return (fim - self.data_inicio).days


class ParticipacaoCampanha(models.Model):
    """Relação jogador-campanha"""
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Usuário")
    )
    
    campanha = models.ForeignKey(
        Campanha,
        on_delete=models.CASCADE,
        related_name='participacoes',
        verbose_name=_("Campanha")
    )
    
    data_entrada = models.DateTimeField(
        _("Data de Entrada"),
        auto_now_add=True
    )
    
    data_saida = models.DateTimeField(
        _("Data de Saída"),
        null=True,
        blank=True
    )
    
    ativo = models.BooleanField(
        _("Ativo"),
        default=True,
        help_text=_("Participante ativo na campanha")
    )
    
    observacoes = models.TextField(
        _("Observações"),
        blank=True,
        help_text=_("Anotações sobre a participação")
    )
    
    class Meta:
        verbose_name = _("Participação em Campanha")
        verbose_name_plural = _("Participações em Campanhas")
        unique_together = ['usuario', 'campanha']
        ordering = ['data_entrada']
    
    def __str__(self):
        status = "✓" if self.ativo else "✗"
        return f"{status} {self.usuario.username} em {self.campanha.nome}"


class ConviteCampanha(models.Model):
    """Convites para participar de campanhas"""
    
    ESTADOS_CONVITE = [
        ('pendente', _("Pendente")),
        ('aceito', _("Aceito")),
        ('recusado', _("Recusado")),
        ('cancelado', _("Cancelado")),
        ('expirado', _("Expirado")),
    ]
    
    campanha = models.ForeignKey(
        Campanha,
        on_delete=models.CASCADE,
        related_name='convites',
        verbose_name=_("Campanha")
    )
    
    convidado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='convites_recebidos',
        verbose_name=_("Convidado")
    )
    
    convidado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='convites_enviados',
        verbose_name=_("Convidado por")
    )
    
    estado = models.CharField(
        _("Estado"),
        max_length=15,
        choices=ESTADOS_CONVITE,
        default='pendente'
    )
    
    mensagem = models.TextField(
        _("Mensagem"),
        blank=True,
        help_text=_("Mensagem personalizada do convite")
    )
    
    data_convite = models.DateTimeField(
        _("Data do Convite"),
        auto_now_add=True
    )
    
    data_resposta = models.DateTimeField(
        _("Data da Resposta"),
        null=True,
        blank=True
    )
    
    data_expiracao = models.DateTimeField(
        _("Data de Expiração"),
        help_text=_("Convite expira automaticamente")
    )
    
    class Meta:
        verbose_name = _("Convite para Campanha")
        verbose_name_plural = _("Convites para Campanhas")
        unique_together = ['campanha', 'convidado']
        ordering = ['-data_convite']
    
    def __str__(self):
        return f"Convite para {self.convidado.username} - {self.campanha.nome} ({self.get_estado_display()})"
    
    @property
    def expirado(self):
        """Verifica se o convite está expirado"""
        from django.utils import timezone
        return timezone.now() > self.data_expiracao


class CampaignParticipant(models.Model):
    """
    Modelo que vincula usuários a personagens específicos em campanhas.
    Implementa a regra: "Um Personagem por Usuário por Campanha".
    """
    
    PARTICIPANT_STATUS = [
        ('ativo', _('Ativo')),
        ('inativo', _('Inativo')),
        ('banido', _('Banido')),
        ('aguardando', _('Aguardando Aprovação')),
        ('pendente', _('Pendente de Personagem')),
    ]
    
    # Relacionamentos principais
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Usuário"),
        help_text=_("Usuário que participa da campanha")
    )
    
    campanha = models.ForeignKey(
        'Campanha',
        on_delete=models.CASCADE,
        related_name='participantes_personagens',
        verbose_name=_("Campanha"),
        help_text=_("Campanha onde o usuário participa")
    )
    
    personagem = models.ForeignKey(
        'personagens.Personagem',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Personagem"),
        help_text=_("Personagem usado pelo usuário nesta campanha")
    )
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=PARTICIPANT_STATUS,
        default='pendente',
        verbose_name=_("Status"),
        help_text=_("Status atual da participação na campanha")
    )
    
    # Timestamps
    data_entrada = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Data de Entrada"),
        help_text=_("Quando o usuário se juntou à campanha")
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Última Atualização"),
        help_text=_("Última vez que o registro foi modificado")
    )
    
    data_saida = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Data de Saída"),
        help_text=_("Quando o usuário deixou a campanha (se aplicável)")
    )
    
    # Metadados
    observacoes = models.TextField(
        blank=True,
        verbose_name=_("Observações"),
        help_text=_("Observações sobre a participação do usuário")
    )
    
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='participacoes_campanha_aprovadas',
        verbose_name=_("Aprovado Por"),
        help_text=_("Usuário que aprovou a participação (organizador da campanha)")
    )
    
    data_aprovacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Data de Aprovação"),
        help_text=_("Quando a participação foi aprovada")
    )
    
    # Configurações de personagem
    personagem_ativo = models.BooleanField(
        default=True,
        verbose_name=_("Personagem Ativo"),
        help_text=_("Se o personagem está ativo nesta campanha")
    )
    
    experiencia_ganha = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Experiência Ganha"),
        help_text=_("XP ganha pelo personagem nesta campanha")
    )
    
    class Meta:
        verbose_name = _("Participante da Campanha")
        verbose_name_plural = _("Participantes das Campanhas")
        
        # Garantir que um usuário só pode ter um personagem ativo por campanha
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'campanha'],
                condition=models.Q(status__in=['ativo', 'aguardando', 'pendente']),
                name='unique_user_per_campaign'
            ),
            models.UniqueConstraint(
                fields=['personagem', 'campanha'],
                condition=models.Q(status__in=['ativo', 'aguardando'], personagem__isnull=False),
                name='unique_character_per_campaign'
            )
        ]
        
        indexes = [
            models.Index(fields=['usuario', 'campanha']),
            models.Index(fields=['personagem', 'campanha']),
            models.Index(fields=['status']),
            models.Index(fields=['data_entrada']),
        ]
        
        ordering = ['data_entrada']
    
    def __str__(self):
        if self.personagem:
            return f"{self.usuario.username} - {self.personagem.nome} em {self.campanha.nome}"
        return f"{self.usuario.username} (sem personagem) em {self.campanha.nome}"
    
    def clean(self):
        """Validações personalizadas do modelo"""
        super().clean()
        
        # Verificar se o usuário é o dono do personagem (se especificado)
        if self.personagem and self.usuario and self.personagem.usuario != self.usuario:
            raise ValidationError({
                'personagem': _('Você só pode usar personagens que você criou.')
            })
        
        # Verificar se o personagem está ativo
        if self.personagem and not self.personagem.ativo:
            raise ValidationError({
                'personagem': _('Este personagem não está disponível para uso.')
            })
        
        # Verificar se o sistema de jogo do personagem é compatível com a campanha
        if self.personagem and self.campanha and self.personagem.sistema_jogo != self.campanha.sistema_jogo:
            raise ValidationError({
                'personagem': _('O personagem deve ser do mesmo sistema de jogo da campanha.')
            })
    
    def save(self, *args, **kwargs):
        """Salvar com validações personalizadas"""
        self.clean()
        super().save(*args, **kwargs)
    
    def aprovar(self, aprovado_por_user=None):
        """Aprovar a participação na campanha"""
        self.status = 'ativo'
        self.aprovado_por = aprovado_por_user
        self.data_aprovacao = timezone.now()
        self.save()
    
    def banir(self, motivo=None):
        """Banir o participante da campanha"""
        self.status = 'banido'
        self.data_saida = timezone.now()
        if motivo:
            self.observacoes += f"\nBanido: {motivo}"
        self.save()
    
    def sair_da_campanha(self):
        """Marcar como inativo (saiu da campanha)"""
        self.status = 'inativo'
        self.data_saida = timezone.now()
        self.save()
    
    def definir_personagem(self, personagem):
        """Definir o personagem para esta participação"""
        if self.personagem:
            raise ValidationError(_('Já existe um personagem definido para esta participação.'))
        
        self.personagem = personagem
        if self.status == 'pendente':
            self.status = 'aguardando'  # Muda para aguardando aprovação
        self.save()
    
    @property
    def esta_ativo(self):
        """Verificar se a participação está ativa"""
        return self.status == 'ativo'
    
    @property
    def pode_jogar(self):
        """Verificar se o usuário pode participar da campanha"""
        return self.status in ['ativo'] and self.personagem is not None
    
    @property
    def precisa_personagem(self):
        """Verificar se precisa definir um personagem"""
        return self.status == 'pendente' or (self.status == 'aguardando' and not self.personagem)
    
    @property
    def aguardando_aprovacao(self):
        """Verificar se está aguardando aprovação"""
        return self.status == 'aguardando' and self.personagem is not None
