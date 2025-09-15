"""
Configuração do Django Admin para o sistema unificado
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import SistemaJogo, ConteudoSistema, EquivalenciaConteudo


@admin.register(SistemaJogo)
class SistemaJogoAdmin(admin.ModelAdmin):
    """Admin para sistemas de jogo"""
    
    list_display = ('nome', 'codigo', 'versao', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'codigo', 'data_criacao')
    search_fields = ('nome', 'codigo', 'versao')
    ordering = ('nome',)
    
    fieldsets = (
        (None, {
            'fields': ('nome', 'codigo', 'versao', 'ativo')
        }),
        (_("Descrição"), {
            'fields': ('descricao',)
        }),
        (_("Configurações"), {
            'classes': ('collapse',),
            'fields': ('configuracoes',)
        }),
        (_("Metadados"), {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao')


@admin.register(ConteudoSistema)
class ConteudoSistemaAdmin(admin.ModelAdmin):
    """Admin para conteúdo dos sistemas"""
    
    list_display = (
        'nome', 'tipo', 'sistema_jogo', 'nivel_minimo', 
        'ativo', 'tem_equivalencias'
    )
    
    list_filter = (
        'sistema_jogo', 'tipo', 'ativo', 'nivel_minimo', 
        'data_criacao'
    )
    
    search_fields = ('nome', 'descricao', 'tags')
    ordering = ('tipo', 'nome')
    
    fieldsets = (
        (None, {
            'fields': ('sistema_jogo', 'tipo', 'nome', 'nivel_minimo', 'ativo')
        }),
        (_("Descrição"), {
            'fields': ('descricao',)
        }),
        (_("Dados do Sistema"), {
            'fields': ('dados_originais',)
        }),
        (_("Sistema Unificado"), {
            'classes': ('collapse',),
            'fields': ('dados_convertidos', 'equivalencias')
        }),
        (_("Categorização"), {
            'fields': ('tags',)
        }),
        (_("Metadados"), {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    def tem_equivalencias(self, obj):
        """Indica se o conteúdo tem equivalências"""
        count = obj.equivalencias_como_origem.count() + obj.equivalencias_como_destino.count()
        if count > 0:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                count
            )
        return format_html('<span style="color: red;">✗</span>')
    
    tem_equivalencias.short_description = _("Equivalências")
    
    def get_queryset(self, request):
        """Otimiza consultas"""
        return super().get_queryset(request).select_related(
            'sistema_jogo'
        ).prefetch_related(
            'equivalencias_como_origem',
            'equivalencias_como_destino'
        )


class EquivalenciaInline(admin.TabularInline):
    """Inline para gerenciar equivalências"""
    model = EquivalenciaConteudo
    fk_name = 'conteudo_origem'
    extra = 1
    
    fields = ('conteudo_destino', 'nivel_equivalencia', 'observacoes')


@admin.register(EquivalenciaConteudo)
class EquivalenciaConteudoAdmin(admin.ModelAdmin):
    """Admin para equivalências entre conteúdos"""
    
    list_display = (
        'conteudo_origem', 'conteudo_destino', 'nivel_equivalencia', 
        'data_criacao'
    )
    
    list_filter = (
        'nivel_equivalencia', 'data_criacao',
        'conteudo_origem__sistema_jogo', 'conteudo_destino__sistema_jogo'
    )
    
    search_fields = (
        'conteudo_origem__nome', 'conteudo_destino__nome', 'observacoes'
    )
    
    ordering = ('-data_criacao',)
    
    fieldsets = (
        (None, {
            'fields': ('conteudo_origem', 'conteudo_destino', 'nivel_equivalencia')
        }),
        (_("Observações"), {
            'fields': ('observacoes',)
        }),
        (_("Metadados"), {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('data_criacao',)
    
    def get_queryset(self, request):
        """Otimiza consultas"""
        return super().get_queryset(request).select_related(
            'conteudo_origem__sistema_jogo',
            'conteudo_destino__sistema_jogo'
        )
