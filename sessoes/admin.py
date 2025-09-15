from django.contrib import admin
from django.utils.html import format_html
from .models import SessionParticipant, SessaoJogo


@admin.register(SessaoJogo)
class SessaoJogoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'mestre', 'participantes_count', 'vagas_disponiveis', 'ativa', 'data_criacao')
    list_filter = ('ativa', 'data_criacao', 'mestre')
    search_fields = ('titulo', 'descricao', 'mestre__username', 'mestre__nome_completo')
    readonly_fields = ('data_criacao', 'participantes_count', 'vagas_disponiveis')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'mestre')
        }),
        ('Configurações', {
            'fields': ('ativa', 'max_participantes')
        }),
        ('Estatísticas', {
            'fields': ('data_criacao', 'participantes_count', 'vagas_disponiveis'),
            'classes': ('collapse',)
        })
    )
    
    def participantes_count(self, obj):
        """Mostrar número de participantes ativos"""
        count = obj.get_participantes_ativos().count()
        return format_html(f'<strong>{count}</strong>')
    participantes_count.short_description = 'Participantes Ativos'
    
    def vagas_disponiveis(self, obj):
        """Mostrar vagas disponíveis com cores"""
        vagas = obj.vagas_disponiveis()
        if vagas == 0:
            color = 'red'
        elif vagas <= 2:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            f'<span style="color: {color}; font-weight: bold;">{vagas}</span>'
        )
    vagas_disponiveis.short_description = 'Vagas Disponíveis'


@admin.register(SessionParticipant)
class SessionParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'usuario', 'personagem', 'sessao', 'status_colored', 
        'data_entrada', 'aprovado_por', 'pode_jogar_display'
    )
    list_filter = (
        'status', 'data_entrada', 'data_aprovacao', 
        'sessao__ativa', 'sessao__mestre'
    )
    search_fields = (
        'usuario__username', 'usuario__nome_completo',
        'personagem__nome', 'sessao__titulo'
    )
    readonly_fields = (
        'data_entrada', 'data_atualizacao', 'data_aprovacao', 
        'pode_jogar_display'
    )
    
    fieldsets = (
        ('Participação', {
            'fields': ('usuario', 'personagem', 'sessao', 'status')
        }),
        ('Aprovação', {
            'fields': ('aprovado_por', 'data_aprovacao'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('data_entrada', 'data_atualizacao', 'data_saida'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        })
    )
    
    # Ações personalizadas
    actions = ['aprovar_participacao', 'banir_participante', 'marcar_inativo']
    
    def status_colored(self, obj):
        """Mostrar status com cores"""
        colors = {
            'ativo': 'green',
            'inativo': 'gray',
            'banido': 'red',
            'aguardando': 'orange'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            f'<span style="color: {color}; font-weight: bold;">{obj.get_status_display()}</span>'
        )
    status_colored.short_description = 'Status'
    
    def pode_jogar_display(self, obj):
        """Mostrar se pode jogar com ícone"""
        if obj.pode_jogar:
            return format_html('<span style="color: green;">✓ Sim</span>')
        else:
            return format_html('<span style="color: red;">✗ Não</span>')
    pode_jogar_display.short_description = 'Pode Jogar'
    
    # Ações em lote
    def aprovar_participacao(self, request, queryset):
        """Aprovar participações em lote"""
        count = 0
        for participant in queryset.filter(status='aguardando'):
            participant.aprovar(aprovado_por_user=request.user)
            count += 1
        
        self.message_user(
            request, 
            f'{count} participação(ões) aprovada(s) com sucesso.'
        )
    aprovar_participacao.short_description = 'Aprovar participações selecionadas'
    
    def banir_participante(self, request, queryset):
        """Banir participantes em lote"""
        count = 0
        for participant in queryset.exclude(status='banido'):
            participant.banir(motivo="Banido via admin")
            count += 1
        
        self.message_user(
            request, 
            f'{count} participante(s) banido(s) com sucesso.'
        )
    banir_participante.short_description = 'Banir participantes selecionados'
    
    def marcar_inativo(self, request, queryset):
        """Marcar participantes como inativos"""
        count = 0
        for participant in queryset.filter(status='ativo'):
            participant.sair_da_sessao()
            count += 1
        
        self.message_user(
            request, 
            f'{count} participante(s) marcado(s) como inativo(s).'
        )
    marcar_inativo.short_description = 'Marcar como inativo'
    
    # Filtros customizados
    def get_queryset(self, request):
        """Otimizar consultas com select_related"""
        return super().get_queryset(request).select_related(
            'usuario', 'personagem', 'sessao', 'aprovado_por'
        )


# Inline para mostrar participantes na página da sessão
class SessionParticipantInline(admin.TabularInline):
    model = SessionParticipant
    extra = 0
    readonly_fields = ('data_entrada', 'data_atualizacao', 'data_aprovacao')
    fields = (
        'usuario', 'personagem', 'status', 
        'data_entrada', 'aprovado_por'
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'usuario', 'personagem', 'aprovado_por'
        )


# Adicionar inline à SessaoJogo
SessaoJogoAdmin.inlines = [SessionParticipantInline]