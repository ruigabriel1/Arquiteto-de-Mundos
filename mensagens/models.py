"""
Modelos para Sistema de Chat/Mensagens de Campanhas
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinLengthValidator
import json

Usuario = get_user_model()


class TipoMensagem(models.TextChoices):
    """Tipos de mensagem no chat"""
    
    NORMAL = 'normal', _('Mensagem Normal')
    SISTEMA = 'sistema', _('Mensagem do Sistema')
    ROLAGEM = 'rolagem', _('Rolagem de Dados')
    WHISPER = 'whisper', _('Mensagem Privada')
    ACAO = 'acao', _('Ação (/me)')
    COMANDO = 'comando', _('Comando do Sistema')
    ENTRADA = 'entrada', _('Entrada de Jogador')
    SAIDA = 'saida', _('Saída de Jogador')


class SalaChat(models.Model):
    """Sala de chat vinculada a uma campanha"""
    
    campanha = models.OneToOneField(
        'campanhas.Campanha',
        on_delete=models.CASCADE,
        related_name='sala_chat',
        verbose_name=_("Campanha")
    )
    
    nome = models.CharField(
        _("Nome da Sala"),
        max_length=100,
        help_text=_("Nome personalizado da sala de chat")
    )
    
    descricao = models.TextField(
        _("Descrição"),
        blank=True,
        help_text=_("Descrição da sala de chat")
    )
    
    # Configurações da sala
    comandos_habilitados = models.BooleanField(
        _("Comandos Habilitados"),
        default=True,
        help_text=_("Permitir comandos como /roll, /whisper")
    )
    
    rolagens_publicas = models.BooleanField(
        _("Rolagens Públicas"),
        default=True,
        help_text=_("Exibir todas as rolagens no chat")
    )
    
    historico_visivel = models.BooleanField(
        _("Histórico Visível"),
        default=True,
        help_text=_("Jogadores podem ver mensagens antigas")
    )
    
    max_mensagens_historico = models.PositiveIntegerField(
        _("Máx. Mensagens no Histórico"),
        default=1000,
        help_text=_("Limite de mensagens mantidas no histórico")
    )
    
    # Metadados
    data_criacao = models.DateTimeField(
        _("Data de Criação"),
        auto_now_add=True
    )
    
    data_atualizacao = models.DateTimeField(
        _("Ultima Atualização"),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _("Sala de Chat")
        verbose_name_plural = _("Salas de Chat")
        ordering = ['-data_atualizacao']
    
    def __str__(self):
        return f"Chat: {self.nome} ({self.campanha.nome})"
    
    @property
    def participantes_online(self):
        """Participantes atualmente online"""
        return self.participacoes.filter(online=True).count()
    
    @property
    def ultima_mensagem(self):
        """Ultima mensagem da sala"""
        return self.mensagens.order_by('-timestamp').first()
    
    def adicionar_mensagem_sistema(self, conteudo, metadados=None):
        """Adicionar mensagem do sistema"""
        return Mensagem.objects.create(
            sala=self,
            usuario=None,
            tipo=TipoMensagem.SISTEMA,
            conteudo=conteudo,
            metadados=metadados or {}
        )


class ParticipacaoChat(models.Model):
    """Participação de um usuário em uma sala de chat"""
    
    sala = models.ForeignKey(
        SalaChat,
        on_delete=models.CASCADE,
        related_name='participacoes',
        verbose_name=_("Sala")
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='participacoes_chat',
        verbose_name=_("Usuário")
    )
    
    # Status da participação
    online = models.BooleanField(
        _("Online"),
        default=False,
        help_text=_("Usuário está atualmente conectado")
    )
    
    mutado = models.BooleanField(
        _("Mutado"),
        default=False,
        help_text=_("Usuário foi silenciado")
    )
    
    is_moderador = models.BooleanField(
        _("Moderador"),
        default=False,
        help_text=_("Usuário pode moderar o chat")
    )
    
    # Timestamps
    primeira_conexao = models.DateTimeField(
        _("Primeira Conexão"),
        auto_now_add=True
    )
    
    ultima_conexao = models.DateTimeField(
        _("Ultima Conexão"),
        auto_now=True
    )
    
    ultima_mensagem_vista = models.DateTimeField(
        _("Ultima Mensagem Vista"),
        null=True,
        blank=True,
        help_text=_("Timestamp da última mensagem visualizada")
    )
    
    # Configurações pessoais
    notificacoes_habilitadas = models.BooleanField(
        _("Notificações"),
        default=True,
        help_text=_("Receber notificações de mensagens")
    )
    
    class Meta:
        verbose_name = _("Participação em Chat")
        verbose_name_plural = _("Participações em Chat")
        unique_together = ['sala', 'usuario']
        ordering = ['-ultima_conexao']
    
    def __str__(self):
        status = "🟢" if self.online else "🔴"
        return f"{status} {self.usuario.username} - {self.sala.nome}"
    
    def marcar_online(self):
        """Marcar usuário como online"""
        self.online = True
        self.ultima_conexao = timezone.now()
        self.save()
    
    def marcar_offline(self):
        """Marcar usuário como offline"""
        self.online = False
        self.save()
    
    def atualizar_ultima_mensagem_vista(self):
        """Atualizar timestamp da última mensagem vista"""
        self.ultima_mensagem_vista = timezone.now()
        self.save()
    
    @property
    def mensagens_nao_lidas(self):
        """Contar mensagens não lidas"""
        if not self.ultima_mensagem_vista:
            return self.sala.mensagens.count()
        
        return self.sala.mensagens.filter(
            timestamp__gt=self.ultima_mensagem_vista
        ).count()


class Mensagem(models.Model):
    """Mensagem em uma sala de chat"""
    
    sala = models.ForeignKey(
        SalaChat,
        on_delete=models.CASCADE,
        related_name='mensagens',
        verbose_name=_("Sala")
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensagens_chat',
        null=True,  # Pode ser None para mensagens do sistema
        blank=True,
        verbose_name=_("Usuário")
    )
    
    tipo = models.CharField(
        _("Tipo"),
        max_length=10,
        choices=TipoMensagem.choices,
        default=TipoMensagem.NORMAL
    )
    
    conteudo = models.TextField(
        _("Conteúdo"),
        validators=[MinLengthValidator(1)],
        help_text=_("Conteúdo da mensagem")
    )
    
    # Mensagem privada (whisper)
    destinatario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensagens_recebidas',
        null=True,
        blank=True,
        verbose_name=_("Destinatário"),
        help_text=_("Para mensagens privadas")
    )
    
    # Dados adicionais (rolagens, comandos, etc.)
    metadados = models.JSONField(
        _("Metadados"),
        default=dict,
        blank=True,
        help_text=_("Dados adicionais da mensagem")
    )
    
    # Vinculação com outros sistemas
    rolagem = models.ForeignKey(
        'rolagem.RolagemDado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mensagens_chat',
        verbose_name=_("Rolagem"),
        help_text=_("Rolagem associada à mensagem")
    )
    
    personagem = models.ForeignKey(
        'personagens.Personagem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mensagens_chat',
        verbose_name=_("Personagem"),
        help_text=_("Personagem associado à mensagem")
    )
    
    # Controle de edição
    editada = models.BooleanField(
        _("Editada"),
        default=False
    )
    
    timestamp_edicao = models.DateTimeField(
        _("Data de Edição"),
        null=True,
        blank=True
    )
    
    # Timestamp
    timestamp = models.DateTimeField(
        _("Data/Hora"),
        default=timezone.now
    )
    
    class Meta:
        verbose_name = _("Mensagem")
        verbose_name_plural = _("Mensagens")
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['sala', 'timestamp']),
            models.Index(fields=['usuario', 'tipo']),
            models.Index(fields=['sala', 'tipo', 'timestamp']),
        ]
    
    def __str__(self):
        if self.tipo == TipoMensagem.SISTEMA:
            return f"[SISTEMA] {self.conteudo[:50]}..."
        elif self.tipo == TipoMensagem.WHISPER:
            return f"[WHISPER] {self.usuario.username} → {self.destinatario.username}"
        else:
            username = self.usuario.username if self.usuario else 'Sistema'
            return f"{username}: {self.conteudo[:50]}..."
    
    def to_dict(self):
        """Converter mensagem para dicionário (WebSocket)"""
        return {
            'id': self.id,
            'sala_id': self.sala.id,
            'usuario': {
                'id': self.usuario.id if self.usuario else None,
                'username': self.usuario.username if self.usuario else 'Sistema',
                'nome_completo': self.usuario.get_full_name() if self.usuario else 'Sistema'
            } if self.usuario else None,
            'tipo': self.tipo,
            'conteudo': self.conteudo,
            'destinatario': {
                'id': self.destinatario.id,
                'username': self.destinatario.username
            } if self.destinatario else None,
            'personagem': {
                'id': self.personagem.id,
                'nome': self.personagem.nome
            } if self.personagem else None,
            'rolagem': {
                'id': self.rolagem.id,
                'expressao': self.rolagem.expressao,
                'resultado': self.rolagem.resultado_final
            } if self.rolagem else None,
            'metadados': self.metadados,
            'editada': self.editada,
            'timestamp': self.timestamp.isoformat(),
            'timestamp_edicao': self.timestamp_edicao.isoformat() if self.timestamp_edicao else None
        }
    
    @classmethod
    def processar_comando(cls, sala, usuario, conteudo, personagem=None):
        """Processar comando do chat (ex: /roll 1d20+5)"""
        
        if not conteudo.startswith('/'):
            return None
        
        partes = conteudo[1:].split(' ', 1)
        comando = partes[0].lower()
        args = partes[1] if len(partes) > 1 else ''
        
        if comando == 'roll' and args:
            # Comando de rolagem
            try:
                from rolagem.models import RolagemDado, TipoRolagem
                
                # Fazer rolagem
                rolagem = RolagemDado.rolar_dados(
                    expressao=args,
                    usuario=usuario,
                    campanha=sala.campanha,
                    personagem=personagem,
                    tipo=TipoRolagem.CUSTOM,
                    descricao=f"Rolagem no chat: {args}"
                )
                
                # Criar mensagem de rolagem
                conteudo_rolagem = f"🎲 {args} = **{rolagem.resultado_final}**"
                if rolagem.resultados_individuais:
                    detalhes = ', '.join([str(r['resultado']) for r in rolagem.resultados_individuais])
                    conteudo_rolagem += f" [{detalhes}]"
                
                return cls.objects.create(
                    sala=sala,
                    usuario=usuario,
                    tipo=TipoMensagem.ROLAGEM,
                    conteudo=conteudo_rolagem,
                    rolagem=rolagem,
                    personagem=personagem,
                    metadados={
                        'comando': comando,
                        'args': args,
                        'expressao': args,
                        'resultado': rolagem.resultado_final
                    }
                )
                
            except Exception as e:
                # Erro na rolagem
                return cls.objects.create(
                    sala=sala,
                    usuario=usuario,
                    tipo=TipoMensagem.COMANDO,
                    conteudo=f"❌ Erro na rolagem '{args}': {str(e)}",
                    metadados={'erro': str(e), 'comando': comando}
                )
        
        elif comando == 'me' and args:
            # Comando de ação (/me faz algo)
            nome = personagem.nome if personagem else usuario.get_full_name()
            return cls.objects.create(
                sala=sala,
                usuario=usuario,
                tipo=TipoMensagem.ACAO,
                conteudo=f"*{nome} {args}*",
                personagem=personagem,
                metadados={'comando': comando, 'acao': args}
            )
        
        else:
            # Comando desconhecido
            return cls.objects.create(
                sala=sala,
                usuario=usuario,
                tipo=TipoMensagem.COMANDO,
                conteudo=f"❓ Comando desconhecido: /{comando}",
                metadados={'comando': comando, 'erro': 'comando_desconhecido'}
            )
