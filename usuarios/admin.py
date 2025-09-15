"""
Configuração do Django Admin para usuários
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Admin customizado para o modelo Usuario"""
    
    # Campos mostrados na lista
    list_display = (
        'username', 'nome_completo', 'email', 'nivel_experiencia',
        'campanhas_como_jogador', 'campanhas_como_mestre', 'is_staff', 
        'is_active', 'date_joined'
    )
    
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'date_joined',
        'campanhas_como_jogador', 'campanhas_como_mestre'
    )
    
    search_fields = ('username', 'nome_completo', 'email')
    ordering = ('-date_joined',)
    
    # Configuração dos fieldsets para edição
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_("Informações Pessoais"), {
            'fields': ('nome_completo', 'first_name', 'last_name', 'email', 
                      'data_nascimento', 'avatar', 'bio')
        }),
        (_("Estatísticas de Jogo"), {
            'fields': ('campanhas_como_jogador', 'campanhas_como_mestre', 
                      'horas_jogadas')
        }),
        (_("Configurações"), {
            'classes': ('collapse',),
            'fields': ('configuracoes_jogo', 'configuracoes_interface')
        }),
        (_("Permissões"), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 
                      'groups', 'user_permissions')
        }),
        (_("Datas Importantes"), {
            'fields': ('last_login', 'date_joined', 'data_ultima_atividade')
        }),
    )
    
    # Fieldsets para criação de novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nome_completo', 'email', 
                      'password1', 'password2'),
        }),
    )
    
    # Campos read-only
    readonly_fields = ('date_joined', 'last_login', 'data_ultima_atividade')
    
    def nivel_experiencia(self, obj):
        """Mostra o nível de experiência do usuário"""
        return obj.nivel_experiencia
    nivel_experiencia.short_description = _("Nível")
    
    def get_queryset(self, request):
        """Otimiza consultas"""
        return super().get_queryset(request).select_related()
