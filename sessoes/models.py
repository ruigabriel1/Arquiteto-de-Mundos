from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


class SessionParticipant(models.Model):
    """
    Modelo que vincula um usuário a um personagem específico em uma sessão de jogo.
    Garante a regra: "Um Personagem por Usuário por Sessão".
    """
    
    PARTICIPANT_STATUS = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('banido', 'Banido'),
        ('aguardando', 'Aguardando Aprovação'),
    ]
    
    # Relacionamentos
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Usuário",
        help_text="Usuário que participará da sessão"
    )
    
    personagem = models.ForeignKey(
        'personagens.Personagem',
        on_delete=models.CASCADE,
        verbose_name="Personagem",
        help_text="Personagem que será usado na sessão"
    )
    
    sessao = models.ForeignKey(
        'sessoes.SessaoJogo',
        on_delete=models.CASCADE,
        verbose_name="Sessão",
        help_text="Sessão de jogo onde o usuário participará"
    )
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=PARTICIPANT_STATUS,
        default='aguardando',
        verbose_name="Status",
        help_text="Status atual da participação na sessão"
    )
    
    # Timestamps
    data_entrada = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de Entrada",
        help_text="Quando o usuário se juntou à sessão"
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização",
        help_text="Última vez que o registro foi modificado"
    )
    
    data_saida = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Saída",
        help_text="Quando o usuário deixou a sessão (se aplicável)"
    )
    
    # Metadados
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Observações sobre a participação do usuário"
    )
    
    aprovado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='participacoes_aprovadas',
        verbose_name="Aprovado Por",
        help_text="Usuário que aprovou a participação (normalmente o mestre)"
    )
    
    data_aprovacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Aprovação",
        help_text="Quando a participação foi aprovada"
    )

    class Meta:
        verbose_name = "Participante da Sessão"
        verbose_name_plural = "Participantes das Sessões"
        
        # Garantir que um usuário só pode ter um personagem ativo por sessão
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'sessao'],
                condition=models.Q(status__in=['ativo', 'aguardando']),
                name='unique_user_per_session'
            ),
            models.UniqueConstraint(
                fields=['personagem', 'sessao'],
                condition=models.Q(status__in=['ativo', 'aguardando']),
                name='unique_character_per_session'
            )
        ]
        
        indexes = [
            models.Index(fields=['usuario', 'sessao']),
            models.Index(fields=['personagem', 'sessao']),
            models.Index(fields=['status']),
            models.Index(fields=['data_entrada']),
        ]
        
        ordering = ['data_entrada']

    def __str__(self):
        return f"{self.usuario.username} - {self.personagem.nome} em {self.sessao.titulo}"
    
    def clean(self):
        """Validações personalizadas do modelo"""
        super().clean()
        
        # Verificar se o usuário é o dono do personagem
        if self.personagem and self.usuario and self.personagem.usuario != self.usuario:
            raise ValidationError({
                'personagem': 'Você só pode usar personagens que você criou.'
            })
        
        # Verificar se o personagem está disponível para uso
        if self.personagem and not self.personagem.ativo:
            raise ValidationError({
                'personagem': 'Este personagem não está disponível para uso.'
            })
    
    def save(self, *args, **kwargs):
        """Salvar com validações personalizadas"""
        self.clean()
        super().save(*args, **kwargs)
    
    def aprovar(self, aprovado_por_user=None):
        """Aprovar a participação na sessão"""
        self.status = 'ativo'
        self.aprovado_por = aprovado_por_user
        self.data_aprovacao = timezone.now()
        self.save()
    
    def banir(self, motivo=None):
        """Banir o participante da sessão"""
        self.status = 'banido'
        self.data_saida = timezone.now()
        if motivo:
            self.observacoes += f"\nBanido: {motivo}"
        self.save()
    
    def sair_da_sessao(self):
        """Marcar como inativo (saiu da sessão)"""
        self.status = 'inativo'
        self.data_saida = timezone.now()
        self.save()
    
    @property
    def esta_ativo(self):
        """Verificar se a participação está ativa"""
        return self.status == 'ativo'
    
    @property
    def pode_jogar(self):
        """Verificar se o usuário pode participar da sessão"""
        return self.status in ['ativo', 'aguardando']


class SessaoJogo(models.Model):
    """
    Modelo básico para sessões de jogo (será expandido conforme necessário)
    """
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Nome da sessão de jogo"
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição da sessão"
    )
    
    mestre = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Mestre",
        help_text="Usuário que conduzirá a sessão"
    )
    
    data_criacao = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de Criação"
    )
    
    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa",
        help_text="Se a sessão está ativa e aceita participantes"
    )
    
    max_participantes = models.PositiveIntegerField(
        default=6,
        verbose_name="Máximo de Participantes",
        help_text="Número máximo de jogadores na sessão"
    )

    class Meta:
        verbose_name = "Sessão de Jogo"
        verbose_name_plural = "Sessões de Jogo"
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo
    
    def get_participantes_ativos(self):
        """Retornar participantes ativos na sessão"""
        return SessionParticipant.objects.filter(
            sessao=self,
            status='ativo'
        )
    
    def vagas_disponiveis(self):
        """Calcular quantas vagas ainda estão disponíveis"""
        participantes_ativos = self.get_participantes_ativos().count()
        return max(0, self.max_participantes - participantes_ativos)
    
    def pode_aceitar_participante(self):
        """Verificar se a sessão pode aceitar mais participantes"""
        return self.ativa and self.vagas_disponiveis() > 0