"""
Modelos para gerenciamento de sessões e participação de usuários
Implementa a regra: Um usuário pode controlar apenas um personagem por sessão ativa
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.db.models import Q


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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participacoes_sessao',
        verbose_name=_('Usuário')
    )
    
    sessao = models.ForeignKey(
        'ia_gm.SessaoIA',  # Assumindo que existe este modelo
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
    
    ip_address = models.GenericIPAddressField(
        _('Endereço IP'),
        null=True,
        blank=True,
        help_text=_('IP usado para entrar na sessão')
    )
    
    user_agent = models.CharField(
        _('User Agent'),
        max_length=500,
        blank=True,
        help_text=_('Navegador/dispositivo usado')
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
    
    def clean(self):
        """Validações do modelo"""
        errors = []
        
        # 1. Verificar se usuário já está em outra sessão ativa
        if self.pk is None and self.usuario_id:  # Apenas na criação
            outras_sessoes_ativas = SessionParticipant.objects.filter(
                usuario=self.usuario,
                estado__in=['aguardando', 'ativo', 'pausado']
            ).exclude(sessao=self.sessao)
            
            if outras_sessoes_ativas.exists():
                sessao_conflito = outras_sessoes_ativas.first()
                errors.append(ValidationError(
                    f'Usuário {self.usuario.username} já está ativo na sessão {sessao_conflito.sessao}',
                    code='usuario_ja_em_sessao'
                ))
        
        # 2. Verificar se personagem já está sendo usado em outra sessão
        if self.personagem_id:
            outras_participacoes = SessionParticipant.objects.filter(
                personagem=self.personagem,
                estado__in=['ativo', 'pausado']
            ).exclude(pk=self.pk)
            
            if outras_participacoes.exists():
                participacao_conflito = outras_participacoes.first()
                errors.append(ValidationError(
                    f'Personagem {self.personagem.nome} já está ativo na sessão {participacao_conflito.sessao}',
                    code='personagem_ja_em_uso'
                ))
        
        # 3. Verificar se personagem pertence ao usuário
        if self.personagem_id and self.usuario_id:
            if self.personagem.criador != self.usuario:
                errors.append(ValidationError(
                    'Usuário não pode usar personagem que não criou',
                    code='personagem_nao_pertence_usuario'
                ))
        
        # 4. Validar estados
        if self.estado == 'ativo' and not self.personagem:
            errors.append(ValidationError(
                'Não pode estar ativo sem ter selecionado um personagem',
                code='ativo_sem_personagem'
            ))
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        # Executar validações
        self.clean()
        
        # Se está selecionando personagem pela primeira vez
        if self.personagem and not self.data_selecao_personagem:
            self.data_selecao_personagem = timezone.now()
            
            # Automaticamente ativar se estava aguardando
            if self.estado == 'aguardando':
                self.estado = 'ativo'
        
        # Se está saindo, definir data de saída
        if self.estado in ['saiu', 'expulso'] and not self.data_saida:
            self.data_saida = timezone.now()
        
        super().save(*args, **kwargs)
    
    # Métodos de conveniência
    
    @property
    def esta_ativo(self):
        """Verifica se o participante está atualmente ativo na sessão"""
        return self.estado in ['aguardando', 'ativo', 'pausado']
    
    @property
    def pode_selecionar_personagem(self):
        """Verifica se pode selecionar/trocar personagem"""
        # Se ainda não selecionou, sempre pode
        if not self.personagem:
            return True
        
        # Se mestre permite trocas
        if self.pode_trocar_personagem:
            return True
        
        # Se não está bloqueado
        if self.bloqueado_ate and timezone.now() < self.bloqueado_ate:
            return False
        
        return False
    
    @property
    def tempo_na_sessao(self):
        """Calcula tempo total na sessão"""
        if self.data_saida:
            return self.data_saida - self.data_entrada
        return timezone.now() - self.data_entrada
    
    @property
    def minutos_inativo(self):
        """Minutos desde a última atividade"""
        if not self.data_ultima_atividade:
            return 0
        delta = timezone.now() - self.data_ultima_atividade
        return int(delta.total_seconds() / 60)
    
    def marcar_atividade(self):
        """Atualiza timestamp de última atividade"""
        self.data_ultima_atividade = timezone.now()
        self.save(update_fields=['data_ultima_atividade'])
    
    def selecionar_personagem(self, personagem):
        """
        Seleciona um personagem para esta sessão.
        Aplica todas as validações de negócio.
        """
        if not self.pode_selecionar_personagem:
            raise ValidationError('Não é possível trocar de personagem neste momento')
        
        # Verificar se personagem pertence ao usuário
        if personagem.criador != self.usuario:
            raise ValidationError('Você só pode usar seus próprios personagens')
        
        # Verificar se personagem não está em uso
        conflito = SessionParticipant.objects.filter(
            personagem=personagem,
            estado__in=['ativo', 'pausado']
        ).exclude(pk=self.pk).first()
        
        if conflito:
            raise ValidationError(
                f'Personagem já está em uso na sessão {conflito.sessao}'
            )
        
        # Selecionar o personagem
        self.personagem = personagem
        self.data_selecao_personagem = timezone.now()
        self.estado = 'ativo'
        self.save()
    
    def sair_da_sessao(self, motivo='saiu'):
        """Remove o usuário da sessão"""
        self.estado = motivo
        self.data_saida = timezone.now()
        self.save()
    
    def pausar_participacao(self):
        """Pausa temporariamente a participação"""
        if self.estado == 'ativo':
            self.estado = 'pausado'
            self.save()
    
    def retomar_participacao(self):
        """Retoma participação após pausa"""
        if self.estado == 'pausado':
            self.estado = 'ativo'
            self.save()
    
    @classmethod
    def get_usuario_sessao_ativa(cls, usuario):
        """Retorna a sessão ativa do usuário, se houver"""
        return cls.objects.filter(
            usuario=usuario,
            estado__in=['aguardando', 'ativo', 'pausado']
        ).first()
    
    @classmethod
    def get_personagem_sessao_ativa(cls, personagem):
        """Retorna a sessão onde o personagem está ativo"""
        return cls.objects.filter(
            personagem=personagem,
            estado__in=['ativo', 'pausado']
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


class SessionCharacterReservation(models.Model):
    """
    Modelo para reservar personagens temporariamente durante seleção.
    Previne condições de corrida quando múltiplos usuários selecionam o mesmo personagem.
    """
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservas_personagem'
    )
    
    personagem = models.ForeignKey(
        'personagens.Personagem',
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    
    sessao = models.ForeignKey(
        'ia_gm.SessaoIA',
        on_delete=models.CASCADE,
        related_name='reservas_personagem'
    )
    
    data_reserva = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    
    class Meta:
        verbose_name = _('Reserva de Personagem')
        verbose_name_plural = _('Reservas de Personagem')
        unique_together = [('personagem', 'sessao')]
        indexes = [
            models.Index(fields=['expira_em']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.expira_em:
            # Reserva válida por 5 minutos
            self.expira_em = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)
    
    @property
    def expirou(self):
        return timezone.now() > self.expira_em
    
    @classmethod
    def limpar_expiradas(cls):
        """Remove reservas expiradas"""
        return cls.objects.filter(expira_em__lt=timezone.now()).delete()
    
    @classmethod
    def reservar_personagem(cls, usuario, personagem, sessao):
        """Tenta reservar um personagem"""
        cls.limpar_expiradas()
        
        try:
            reserva, created = cls.objects.get_or_create(
                personagem=personagem,
                sessao=sessao,
                defaults={
                    'usuario': usuario,
                    'expira_em': timezone.now() + timezone.timedelta(minutes=5)
                }
            )
            
            if created or reserva.usuario == usuario:
                return reserva
            else:
                return None  # Já reservado por outro usuário
                
        except Exception:
            return None