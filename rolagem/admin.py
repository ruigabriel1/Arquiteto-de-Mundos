"""
Django Admin para Sistema de Rolagem de Dados
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import RolagemDado, TemplateRolagem


@admin.register(RolagemDado)
class RolagemDadoAdmin(admin.ModelAdmin):
    """Admin para Rolagens de Dados"""
    
    list_display = (
        'id', 'expressao', 'resultado_final', 'usuario',
        'personagem', 'campanha', 'tipo', 'modificador',
        'data_rolagem', 'publica_icon', 'secreta_icon'
    )
    
    list_filter = (
        'tipo', 'modificador', 'publica', 'secreta',
        'data_rolagem', 'campanha'
    )
    
    search_fields = (
        'usuario__username', 'personagem__nome',
        'campanha__nome', 'expressao', 'descricao'
    )
    
    readonly_fields = (
        'resultados_individuais', 'resultado_final',
        'resultado_bruto', 'modificador_valor', 'data_rolagem'
    )
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'usuario', 'campanha', 'personagem',
                'tipo', 'modificador', 'expressao'
            )
        }),
        ('Resultados', {
            'fields': (
                'resultados_individuais', 'resultado_bruto',
                'modificador_valor', 'resultado_final'
            ),
            'classes': ('collapse',)
        }),
        ('Detalhes', {
            'fields': (
                'descricao', 'metadados', 'publica', 'secreta',
                'data_rolagem'
            )
        })
    )
    
    ordering = ['-data_rolagem']
    
    def publica_icon(self, obj):
        """Ícone para rolagem pública"""
        if obj.publica:
            return format_html('<span style="color: green;">✓ Pública</span>')
        return format_html('<span style="color: orange;">✗ Privada</span>')
    publica_icon.short_description = 'Visibilidade'
    
    def secreta_icon(self, obj):
        """Ícone para rolagem secreta"""
        if obj.secreta:
            return format_html('<span style="color: red;">🔒 Secreta</span>')
        return format_html('<span style="color: gray;">👁 Normal</span>')
    secreta_icon.short_description = 'Segredo'
    
    def has_add_permission(self, request):
        """Desabilitar adição manual de rolagens"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Permitir apenas visualização"""
        return request.user.is_superuser


@admin.register(TemplateRolagem)
class TemplateRolagemAdmin(admin.ModelAdmin):
    """Admin para Templates de Rolagem"""
    
    list_display = (
        'nome', 'expressao', 'tipo', 'usuario',
        'data_criacao', 'data_atualizacao'
    )
    
    list_filter = ('tipo', 'data_criacao', 'usuario')
    
    search_fields = ('nome', 'expressao', 'descricao', 'usuario__username')
    
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'nome', 'tipo')
        }),
        ('Configuração da Rolagem', {
            'fields': ('expressao', 'descricao')
        }),
        ('Configurações Avançadas', {
            'fields': ('configuracoes',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['usuario__username', 'nome']
