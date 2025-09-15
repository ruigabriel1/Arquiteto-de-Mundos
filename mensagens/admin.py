"""
Admin para Chat/Mensagens
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import SalaChat, ParticipacaoChat, Mensagem, TipoMensagem


class MensagemInline(admin.TabularInline):
    """Inline para mensagens na sala"""
    model = Mensagem
    fk_name = 'sala'
    extra = 0
    readonly_fields = ['timestamp', 'usuario', 'tipo', 'conteudo_truncado']
    fields = ['timestamp', 'usuario', 'tipo', 'conteudo_truncado']
    
    def conteudo_truncado(self, obj):
        """Conteúdo truncado da mensagem"""
        return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo
    conteudo_truncado.short_description = 'Conteúdo'
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SalaChat)
class SalaChatAdmin(admin.ModelAdmin):
    """Admin para Salas de Chat"""
    
    list_display = [
        'nome', 'campanha', 'total_participantes', 'total_mensagens',
        'participantes_online', 'comandos_habilitados', 'data_criacao'
    ]
    
    list_filter = [
        'comandos_habilitados', 'rolagens_publicas', 'historico_visivel',
        'data_criacao', 'campanha__nome'
    ]
    
    search_fields = ['nome', 'descricao', 'campanha__nome']
    
    readonly_fields = [
        'data_criacao', 'data_atualizacao', 'total_participantes',
        'total_mensagens', 'participantes_online', 'ultima_mensagem_info'
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'campanha')
        }),
        ('Configurações', {
            'fields': (
                'comandos_habilitados', 'rolagens_publicas',
                'historico_visivel', 'max_mensagens_historico'
            )
        }),
        ('Estatísticas', {
            'fields': (
                'total_participantes', 'participantes_online',
                'total_mensagens', 'ultima_mensagem_info'
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        })
    )
    
    def total_participantes(self, obj):
        """Total de participantes da sala"""
        return obj.participacoes.count()
    total_participantes.short_description = 'Total Participantes'
    
    def total_mensagens(self, obj):
        """Total de mensagens na sala"""
        return obj.mensagens.count()
    total_mensagens.short_description = 'Total Mensagens'
    
    def participantes_online(self, obj):
        """Participantes online"""
        online = obj.participacoes.filter(online=True).count()
        if online > 0:
            return format_html(
                '<span style="color: green;">● {}</span>',
                online
            )
        return '0'
    participantes_online.short_description = 'Online'
    
    def ultima_mensagem_info(self, obj):
        """Informações da última mensagem"""
        if obj.ultima_mensagem:
            msg = obj.ultima_mensagem
            return format_html(
                '<strong>{}</strong><br/>'
                '<small>{}</small><br/>'
                '<em>{}</em>',
                msg.usuario.username if msg.usuario else 'Sistema',
                msg.timestamp.strftime('%d/%m/%Y %H:%M'),
                msg.conteudo[:50] + '...' if len(msg.conteudo) > 50 else msg.conteudo
            )
        return 'Nenhuma mensagem'
    ultima_mensagem_info.short_description = 'Última Mensagem'
    
    inlines = [MensagemInline]
    
    def get_queryset(self, request):
        """Otimizar queryset"""
        return super().get_queryset(request).select_related(
            'campanha', 'ultima_mensagem', 'ultima_mensagem__usuario'
        ).prefetch_related('participacoes')




@admin.register(ParticipacaoChat)
class ParticipacaoChatAdmin(admin.ModelAdmin):
    """Admin para Participações em Chat"""
    
    list_display = [
        'usuario_nome', 'sala_nome', 'online_status', 'is_moderador',
        'mensagens_nao_lidas', 'ultima_conexao'
    ]
    
    list_filter = [
        'online', 'mutado', 'is_moderador', 'notificacoes_habilitadas',
        'sala__nome', 'primeira_conexao', 'ultima_conexao'
    ]
    
    search_fields = [
        'usuario__username', 'usuario__first_name', 'usuario__last_name',
        'sala__nome'
    ]
    
    readonly_fields = [
        'primeira_conexao', 'total_mensagens_enviadas'
    ]
    
    fieldsets = (
        ('Participação', {
            'fields': ('sala', 'usuario', 'primeira_conexao')
        }),
        ('Status', {
            'fields': ('online', 'is_moderador', 'mutado')
        }),
        ('Mensagens', {
            'fields': (
                'mensagens_nao_lidas', 'ultima_mensagem_vista',
                'total_mensagens_enviadas'
            )
        }),
        ('Configurações', {
            'fields': ('notificacoes_habilitadas',)
        }),
        ('Timestamps', {
            'fields': ('ultima_conexao',),
            'classes': ('collapse',)
        })
    )
    
    def usuario_nome(self, obj):
        """Nome do usuário"""
        return obj.usuario.get_full_name() or obj.usuario.username
    usuario_nome.short_description = 'Usuário'
    
    def sala_nome(self, obj):
        """Nome da sala"""
        return obj.sala.nome
    sala_nome.short_description = 'Sala'
    
    def online_status(self, obj):
        """Status online"""
        if obj.online:
            return format_html('<span style="color: green;">● Online</span>')
        return format_html('<span style="color: red;">○ Offline</span>')
    online_status.short_description = 'Status'
    
    def total_mensagens_enviadas(self, obj):
        """Total de mensagens enviadas pelo usuário na sala"""
        return obj.sala.mensagens.filter(usuario=obj.usuario).count()
    total_mensagens_enviadas.short_description = 'Mensagens Enviadas'
    
    def get_queryset(self, request):
        """Otimizar queryset"""
        return super().get_queryset(request).select_related(
            'usuario', 'sala'
        )


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    """Admin para Mensagens"""
    
    list_display = [
        'timestamp', 'sala_nome', 'usuario_nome', 'tipo_display',
        'conteudo_truncado', 'editada'
    ]
    
    list_filter = [
        'tipo', 'editada', 'timestamp', 'sala__nome'
    ]
    
    search_fields = [
        'conteudo', 'usuario__username', 'personagem__nome',
        'destinatario__username', 'sala__nome'
    ]
    
    readonly_fields = [
        'timestamp', 'timestamp_edicao', 'tipo_display', 'metadados_formatados'
    ]
    
    fieldsets = (
        ('Mensagem', {
            'fields': ('conteudo', 'tipo_display', 'editada')
        }),
        ('Contexto', {
            'fields': ('sala', 'usuario', 'personagem', 'destinatario')
        }),
        ('Integração', {
            'fields': ('rolagem',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('metadados_formatados',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'timestamp_edicao'),
            'classes': ('collapse',)
        })
    )
    
    def sala_nome(self, obj):
        """Nome da sala"""
        return obj.sala.nome
    sala_nome.short_description = 'Sala'
    
    def usuario_nome(self, obj):
        """Nome do usuário"""
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return 'Sistema'
    usuario_nome.short_description = 'Usuário'
    
    def tipo_display(self, obj):
        """Exibição do tipo com cor"""
        cores = {
            TipoMensagem.NORMAL: 'black',
            TipoMensagem.WHISPER: 'purple',
            TipoMensagem.COMANDO_ACAO: 'blue',
            TipoMensagem.COMANDO_ROLAGEM: 'green',
            TipoMensagem.SISTEMA: 'orange'
        }
        cor = cores.get(obj.tipo, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            cor,
            obj.get_tipo_display()
        )
    tipo_display.short_description = 'Tipo'
    
    def conteudo_truncado(self, obj):
        """Conteúdo truncado"""
        return obj.conteudo[:100] + '...' if len(obj.conteudo) > 100 else obj.conteudo
    conteudo_truncado.short_description = 'Conteúdo'
    
    def metadados_formatados(self, obj):
        """Metadados formatados"""
        if obj.metadados:
            import json
            try:
                formatted = json.dumps(obj.metadados, indent=2, ensure_ascii=False)
                return format_html('<pre>{}</pre>', formatted)
            except:
                return str(obj.metadados)
        return 'Nenhum metadado'
    metadados_formatados.short_description = 'Metadados'
    
    def get_queryset(self, request):
        """Otimizar queryset"""
        return super().get_queryset(request).select_related(
            'usuario', 'destinatario', 'personagem', 'rolagem', 'sala'
        )
    
    def has_add_permission(self, request):
        """Não permitir adicionar mensagens pelo admin"""
        return False
