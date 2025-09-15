"""
Modelos para gerenciamento de usuários do Unified Chronicles
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q


class Usuario(AbstractUser):
    """Modelo personalizado de usuário"""
    
    nome_completo = models.CharField(
        _("Nome Completo"), 
        max_length=150, 
        help_text=_("Nome completo do usuário")
    )
    
    data_nascimento = models.DateField(
        _("Data de Nascimento"), 
        null=True, 
        blank=True
    )
    
    avatar = models.ImageField(
        _("Avatar"), 
        upload_to='avatares/', 
        null=True, 
        blank=True,
        help_text=_("Imagem de perfil do usuário")
    )
    
    bio = models.TextField(
        _("Biografia"), 
        max_length=500, 
        blank=True,
        help_text=_("Descrição pessoal do usuário")
    )
    
    # Configurações de jogo
    configuracoes_jogo = models.JSONField(
        _("Configurações de Jogo"),
        default=dict,
        help_text=_("Preferências pessoais para mecânicas de jogo")
    )
    
    # Configurações de interface
    configuracoes_interface = models.JSONField(
        _("Configurações de Interface"),
        default=dict,
        help_text=_("Preferências de tema, layout e acessibilidade")
    )
    
    # Estatísticas
    campanhas_como_jogador = models.PositiveIntegerField(
        _("Campanhas como Jogador"),
        default=0
    )
    
    campanhas_como_mestre = models.PositiveIntegerField(
        _("Campanhas como Mestre"),
        default=0
    )
    
    horas_jogadas = models.PositiveIntegerField(
        _("Horas Jogadas"),
        default=0,
        help_text=_("Total de horas em sessões de RPG")
    )
    
    # Metadata
    data_ultima_atividade = models.DateTimeField(
        _("Última Atividade"),
        auto_now=True
    )
    
    ativo = models.BooleanField(
        _("Ativo"),
        default=True,
        help_text=_("Define se o usuário pode acessar o sistema")
    )
    
    class Meta:
        verbose_name = _("Usuário")
        verbose_name_plural = _("Usuários")
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.nome_completo} ({self.username})"
    
    @property
    def nivel_experiencia(self):
        """Calcula nível de experiência baseado nas horas jogadas"""
        if self.horas_jogadas < 10:
            return "Novato"
        elif self.horas_jogadas < 50:
            return "Iniciante"
        elif self.horas_jogadas < 200:
            return "Experiente"
        elif self.horas_jogadas < 500:
            return "Veterano"
        else:
            return "Lenda"
    
    def pode_mestrar(self):
        """Verifica se o usuário tem experiência suficiente para mestrar"""
        return self.horas_jogadas >= 20 or self.campanhas_como_mestre > 0


class SessionParticipant(models.Model):
    """
    Modelo que vincula usuário-personagem-sessão com regras de negócio.
    
    REGRA FUNDAMENTAL: Um usuário só pode controlar um personagem por sessão ativa.
    """
    
    ESTADOS_PARTICIPACAO = [
        ('aguardando', _('Aguardando Seleção')),  # Usuário entrou mas não selecionou personagem
        ('ativo', _('Ativo na Sessão')),         # Usuário com personagem ativo
        ('pausado', _('Pausado')),               # Temporariamente ausente
        ('saiu', _('Saiu da Sessão')),          # Saiu voluntariamente  
        ('expulso', _('Expulso')),              # Removido pelo mestre
        ('desconectado', _('Desconectado')),    # Perdeu conexão
    ]
    
    # Chaves estrangeiras
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='participacoes_sessao',
        verbose_name=_('Usuário')
    )
    
    sessao = models.ForeignKey(
        'ia_gm.SessaoIA',
        on_delete=models.CASCADE,
        related_name='participantes',
        verbose_name=_('Sessão')
    )
    
    personagem = models.ForeignKey(
        'personagens.Personagem',
        on_delete=models.CASCADE,
        related_name='participacoes_sessao',
        verbose_name=_('Personagem'),
        null=True,
        blank=True,
        help_text=_('Personagem controlado pelo usuário nesta sessão')
    )
    
    # Estado e controle
    estado = models.CharField(
        _('Estado'),
        max_length=20,
        choices=ESTADOS_PARTICIPACAO,
        default='aguardando'
    )
    
    # Timestamps importantes
    data_entrada = models.DateTimeField(
        _('Data de Entrada'),
        auto_now_add=True,
        help_text=_('Quando o usuário entrou na sessão')
    )
    
    data_selecao_personagem = models.DateTimeField(
        _('Data de Seleção do Personagem'),
        null=True,
        blank=True,
        help_text=_('Quando o personagem foi selecionado')
    )
    
    data_ultima_atividade = models.DateTimeField(
        _('Última Atividade'),
        auto_now=True
    )
    
    data_saida = models.DateTimeField(
        _('Data de Saída'),
        null=True,
        blank=True
    )
    
    # Controle de bloqueio
    bloqueado_ate = models.DateTimeField(
        _('Bloqueado até'),
        null=True,
        blank=True,
        help_text=_('Se definido, usuário não pode trocar personagem até esta data')
    )
    
    pode_trocar_personagem = models.BooleanField(
        _('Pode Trocar Personagem'),
        default=False,
        help_text=_('Se o mestre permite troca de personagem durante a sessão')
    )
    
    # Metadados
    observacoes = models.TextField(
        _('Observações'),
        blank=True,
        help_text=_('Notas do mestre ou sistema sobre esta participação')
    )
    
    class Meta:
        verbose_name = _('Participante de Sessão')
        verbose_name_plural = _('Participantes de Sessão')
        ordering = ['data_entrada']
        
        # CONSTRAINT FUNDAMENTAL: Um usuário por sessão
        unique_together = [
            ('usuario', 'sessao'),
        ]
        
        # Índices para performance
        indexes = [
            models.Index(fields=['usuario', 'estado']),
            models.Index(fields=['sessao', 'estado']),
            models.Index(fields=['personagem', 'estado']),
            models.Index(fields=['data_entrada']),
        ]
    
    def __str__(self):
        status_emoji = {
            'aguardando': '⏳',
            'ativo': '✅',
            'pausado': '⏸️',
            'saiu': '👋',
            'expulso': '❌',
            'desconectado': '🔌'
        }.get(self.estado, '❓')
        
        personagem_nome = self.personagem.nome if self.personagem else 'Sem personagem'
        return f"{status_emoji} {self.usuario.username} - {personagem_nome} (Sessão {self.sessao.id})"
    
    @property
    def esta_ativo(self):
        """Verifica se o participante está atualmente ativo na sessão"""
        return self.estado in ['aguardando', 'ativo', 'pausado']
    
    @classmethod
    def get_usuario_sessao_ativa(cls, usuario):
        """Retorna a sessão ativa do usuário, se houver"""
        return cls.objects.filter(
            usuario=usuario,
            estado__in=['aguardando', 'ativo', 'pausado']
        ).first()
    
    @classmethod
    def pode_usuario_entrar_sessao(cls, usuario, sessao):
        """Verifica se usuário pode entrar em uma sessão"""
        # Verificar se já não está na sessão
        ja_na_sessao = cls.objects.filter(
            usuario=usuario,
            sessao=sessao,
            estado__in=['aguardando', 'ativo', 'pausado']
        ).exists()
        
        if ja_na_sessao:
            return False, 'Usuário já está nesta sessão'
        
        # Verificar se não está em outra sessão
        em_outra_sessao = cls.objects.filter(
            usuario=usuario,
            estado__in=['aguardando', 'ativo', 'pausado']
        ).exclude(sessao=sessao).exists()
        
        if em_outra_sessao:
            return False, 'Usuário já está ativo em outra sessão'
        
        return True, 'Pode entrar na sessão'
