"""
Configuração do Django Admin para personagens
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Personagem, HistoricoPersonagem, BackupPersonagem


class HistoricoInline(admin.TabularInline):
    """Inline para histórico do personagem"""
    model = HistoricoPersonagem
    extra = 0
    fields = ('tipo', 'descricao', 'usuario_mudanca', 'data_mudanca')
    readonly_fields = ('data_mudanca',)
    ordering = ('-data_mudanca',)


class BackupInline(admin.TabularInline):
    """Inline para backups do personagem"""
    model = BackupPersonagem
    extra = 0
    fields = ('versao', 'motivo_backup', 'data_backup')
    readonly_fields = ('data_backup',)
    ordering = ('-versao',)


@admin.register(Personagem)
class PersonagemAdmin(admin.ModelAdmin):
    """Admin para personagens"""
    
    list_display = (
        'nome', 'usuario', 'campanha', 'nivel', 'sistema_jogo',
        'vida_display', 'ativo', 'publico', 'data_atualizacao'
    )
    
    list_filter = (
        'sistema_jogo', 'campanha', 'nivel', 'ativo', 'publico',
        'data_criacao', 'usuario'
    )
    
    search_fields = (
        'nome', 'usuario__username', 'campanha__nome', 'historia'
    )
    
    ordering = ('-data_atualizacao',)
    
    fieldsets = (
        (None, {
            'fields': (
                'nome', 'usuario', 'campanha', 'sistema_jogo', 'avatar'
            )
        }),
        (_("Progressão"), {
            'fields': ('nivel', 'experiencia')
        }),
        (_("Atributos"), {
            'fields': (
                'forca', 'destreza', 'constituicao',
                'inteligencia', 'sabedoria', 'carisma'
            )
        }),
        (_("Combate"), {
            'fields': (
                'pontos_vida_max', 'pontos_vida_atual', 
                'pontos_vida_temporarios', 'classe_armadura'
            )
        }),
        (_("Dados do Sistema"), {
            'fields': (
                'raca', 'classes', 'antecedente', 'pericias',
                'magias_conhecidas', 'equipamentos', 'talentos'
            ),
            'classes': ('collapse',)
        }),
        (_("Sistema Unificado"), {
            'fields': ('dados_unificados',),
            'classes': ('collapse',)
        }),
        (_("Narrativa"), {
            'fields': (
                'historia', 'personalidade', 'anotacoes_jogador',
                'anotacoes_mestre'
            ),
            'classes': ('collapse',)
        }),
        (_("Status"), {
            'fields': ('ativo', 'publico', 'versao')
        }),
        (_("Metadados"), {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    inlines = [HistoricoInline, BackupInline]
    
    def vida_display(self, obj):
        """Mostra status de vida do personagem"""
        atual = obj.pontos_vida_atual
        maximo = obj.pontos_vida_max
        
        if obj.morto:
            color = 'red'
            status = 'Morto'
        elif atual <= maximo * 0.25:
            color = 'red'
            status = 'Crítico'
        elif atual <= maximo * 0.5:
            color = 'orange'
            status = 'Ferido'
        else:
            color = 'green'
            status = 'Saudável'
        
        return format_html(
            '<span style="color: {}">{}/{} ({})</span>',
            color, atual, maximo, status
        )
    
    vida_display.short_description = _("Vida")
    
    def get_queryset(self, request):
        """Otimiza consultas"""
        return super().get_queryset(request).select_related(
            'usuario', 'campanha', 'sistema_jogo'
        )


@admin.register(HistoricoPersonagem)
class HistoricoPersonagemAdmin(admin.ModelAdmin):
    """Admin para histórico de personagens"""
    
    list_display = (
        'personagem', 'tipo', 'descricao_resumida', 'usuario_mudanca',
        'data_mudanca'
    )
    
    list_filter = ('tipo', 'data_mudanca', 'usuario_mudanca')
    search_fields = (
        'personagem__nome', 'descricao', 'usuario_mudanca__username'
    )
    ordering = ('-data_mudanca',)
    
    fieldsets = (
        (None, {
            'fields': (
                'personagem', 'tipo', 'usuario_mudanca'
            )
        }),
        (_("Mudança"), {
            'fields': ('descricao',)
        }),
        (_("Dados Técnicos"), {
            'fields': ('dados_anteriores', 'dados_novos'),
            'classes': ('collapse',)
        }),
        (_("Metadados"), {
            'fields': ('data_mudanca',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('data_mudanca',)
    
    def descricao_resumida(self, obj):
        """Mostra descrição resumida"""
        return obj.descricao[:50] + '...' if len(obj.descricao) > 50 else obj.descricao
    
    descricao_resumida.short_description = _("Descrição")
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'personagem', 'usuario_mudanca'
        )


@admin.register(BackupPersonagem)
class BackupPersonagemAdmin(admin.ModelAdmin):
    """Admin para backups de personagens"""
    
    list_display = (
        'personagem', 'versao', 'motivo_backup', 'data_backup'
    )
    
    list_filter = ('data_backup', 'motivo_backup')
    search_fields = ('personagem__nome', 'motivo_backup')
    ordering = ('-data_backup',)
    
    fieldsets = (
        (None, {
            'fields': ('personagem', 'versao', 'motivo_backup')
        }),
        (_("Dados do Backup"), {
            'fields': ('dados_personagem',),
            'classes': ('collapse',)
        }),
        (_("Metadados"), {
            'fields': ('data_backup',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('data_backup',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('personagem')
