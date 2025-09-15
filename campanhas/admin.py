"""
Configuração do Django Admin para campanhas
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Campanha, ParticipacaoCampanha, ConviteCampanha, CampaignParticipant


class ParticipacaoInline(admin.TabularInline):
    """Inline para participantes da campanha"""
    model = ParticipacaoCampanha
    extra = 0
    fields = ('usuario', 'data_entrada', 'ativo', 'observacoes')
    readonly_fields = ('data_entrada',)


class ConviteInline(admin.TabularInline):
    """Inline para convites da campanha"""
    model = ConviteCampanha
    extra = 0
    fields = ('convidado', 'convidado_por', 'estado', 'data_convite')
    readonly_fields = ('data_convite',)


class CampaignParticipantInline(admin.TabularInline):
    """Inline para participantes com personagens da campanha"""
    model = CampaignParticipant
    extra = 0
    fields = ('usuario', 'personagem', 'status', 'data_entrada', 'aprovado_por')
    readonly_fields = ('data_entrada', 'data_atualizacao')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'usuario', 'personagem', 'aprovado_por'
        )


@admin.register(Campanha)
class CampanhaAdmin(admin.ModelAdmin):
    """Admin para campanhas"""
    
    list_display = (
        'nome', 'organizador', 'sistema_jogo', 'estado', 'num_jogadores_display',
        'nivel_inicial', 'nivel_maximo', 'ia_ativa', 'data_criacao'
    )
    
    list_filter = (
        'estado', 'sistema_jogo', 'ia_ativa', 'nivel_inicial',
        'data_criacao', 'organizador'
    )
    
    search_fields = ('nome', 'descricao', 'organizador__username')
    ordering = ('-data_atualizacao',)
    
    fieldsets = (
        (None, {
            'fields': ('nome', 'organizador', 'sistema_jogo', 'estado')
        }),
        (_("Descrição"), {
            'fields': ('descricao',)
        }),
        (_("Configurações de Jogo"), {
            'fields': (
                'nivel_inicial', 'nivel_maximo', 'max_jogadores'
            )
        }),
        (_("IA Game Master"), {
            'fields': ('ia_ativa', 'configuracoes_ia', 'personalidade_gm')
        }),
        (_("Datas"), {
            'fields': (
                'data_criacao', 'data_inicio', 'data_ultima_sessao', 
                'data_atualizacao'
            ),
            'classes': ('collapse',)
        }),
        (_("Configurações Avançadas"), {
            'fields': ('configuracoes_gerais',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    inlines = [ParticipacaoInline, CampaignParticipantInline, ConviteInline]
    
    def num_jogadores_display(self, obj):
        """Mostra número atual/máximo de jogadores"""
        atual = obj.num_jogadores
        maximo = obj.max_jogadores
        
        if atual >= maximo:
            color = 'red'
        elif atual >= maximo * 0.8:
            color = 'orange'
        else:
            color = 'green'
            
        return format_html(
            '<span style="color: {}">{}/{}</span>',
            color, atual, maximo
        )
    
    num_jogadores_display.short_description = _("Jogadores")
    
    def get_queryset(self, request):
        """Otimiza consultas"""
        return super().get_queryset(request).select_related(
            'organizador', 'sistema_jogo'
        ).prefetch_related('participacoes')


@admin.register(ParticipacaoCampanha)
class ParticipacaoCampanhaAdmin(admin.ModelAdmin):
    """Admin para participações em campanhas"""
    
    list_display = (
        'usuario', 'campanha', 'data_entrada', 'ativo', 'dias_na_campanha'
    )
    
    list_filter = ('ativo', 'data_entrada', 'campanha__sistema_jogo')
    search_fields = ('usuario__username', 'campanha__nome')
    ordering = ('-data_entrada',)
    
    fieldsets = (
        (None, {
            'fields': ('usuario', 'campanha', 'ativo')
        }),
        (_("Datas"), {
            'fields': ('data_entrada', 'data_saida')
        }),
        (_("Observações"), {
            'fields': ('observacoes',)
        }),
    )
    
    readonly_fields = ('data_entrada',)
    
    def dias_na_campanha(self, obj):
        """Calcula dias de participação"""
        from django.utils import timezone
        if obj.data_saida:
            delta = obj.data_saida - obj.data_entrada
        else:
            delta = timezone.now() - obj.data_entrada
        return delta.days
    
    dias_na_campanha.short_description = _("Dias")
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'usuario', 'campanha'
        )


@admin.register(ConviteCampanha)
class ConviteCampanhaAdmin(admin.ModelAdmin):
    """Admin para convites de campanhas"""
    
    list_display = (
        'convidado', 'campanha', 'convidado_por', 'estado',
        'data_convite', 'expirado_display'
    )
    
    list_filter = ('estado', 'data_convite', 'data_expiracao')
    search_fields = (
        'convidado__username', 'campanha__nome', 'convidado_por__username'
    )
    ordering = ('-data_convite',)
    
    fieldsets = (
        (None, {
            'fields': (
                'campanha', 'convidado', 'convidado_por', 'estado'
            )
        }),
        (_("Mensagem"), {
            'fields': ('mensagem',)
        }),
        (_("Datas"), {
            'fields': (
                'data_convite', 'data_resposta', 'data_expiracao'
            )
        }),
    )
    
    readonly_fields = ('data_convite',)
    
    def expirado_display(self, obj):
        """Mostra se o convite está expirado"""
        if obj.expirado:
            return format_html(
                '<span style="color: red;">✓ Expirado</span>'
            )
        return format_html(
            '<span style="color: green;">✓ Válido</span>'
        )
    
    expirado_display.short_description = _("Status")
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'campanha', 'convidado', 'convidado_por'
        )


@admin.register(CampaignParticipant)
class CampaignParticipantAdmin(admin.ModelAdmin):
    """Admin para participações em campanhas com personagens"""
    
    list_display = (
        'usuario', 'personagem', 'campanha', 'status_colored', 
        'data_entrada', 'aprovado_por', 'pode_jogar_display', 'experiencia_ganha'
    )
    
    list_filter = (
        'status', 'data_entrada', 'data_aprovacao', 'personagem_ativo',
        'campanha__sistema_jogo', 'campanha__organizador'
    )
    
    search_fields = (
        'usuario__username', 'usuario__nome_completo',
        'personagem__nome', 'campanha__nome'
    )
    
    readonly_fields = (
        'data_entrada', 'data_atualizacao', 'data_aprovacao', 
        'pode_jogar_display'
    )
    
    fieldsets = (
        (_("Participação"), {
            'fields': ('usuario', 'campanha', 'personagem', 'status')
        }),
        (_("Configurações"), {
            'fields': ('personagem_ativo', 'experiencia_ganha')
        }),
        (_("Aprovação"), {
            'fields': ('aprovado_por', 'data_aprovacao'),
            'classes': ('collapse',)
        }),
        (_("Timestamps"), {
            'fields': ('data_entrada', 'data_atualizacao', 'data_saida'),
            'classes': ('collapse',)
        }),
        (_("Observações"), {
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
            'aguardando': 'orange',
            'pendente': 'blue'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            f'<span style="color: {color}; font-weight: bold;">{obj.get_status_display()}</span>'
        )
    status_colored.short_description = _("Status")
    
    def pode_jogar_display(self, obj):
        """Mostrar se pode jogar com ícone"""
        if obj.pode_jogar:
            return format_html('<span style="color: green;">✓ Sim</span>')
        else:
            return format_html('<span style="color: red;">✗ Não</span>')
    pode_jogar_display.short_description = _("Pode Jogar")
    
    # Ações em lote
    def aprovar_participacao(self, request, queryset):
        """Aprovar participações em lote"""
        count = 0
        for participant in queryset.filter(status='aguardando'):
            if participant.personagem:  # Só aprova se tem personagem
                participant.aprovar(aprovado_por_user=request.user)
                count += 1
        
        self.message_user(
            request, 
            f'{count} participação(ões) aprovada(s) com sucesso.'
        )
    aprovar_participacao.short_description = _("Aprovar participações selecionadas")
    
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
    banir_participante.short_description = _("Banir participantes selecionados")
    
    def marcar_inativo(self, request, queryset):
        """Marcar participantes como inativos"""
        count = 0
        for participant in queryset.filter(status='ativo'):
            participant.sair_da_campanha()
            count += 1
        
        self.message_user(
            request, 
            f'{count} participante(s) marcado(s) como inativo(s).'
        )
    marcar_inativo.short_description = _("Marcar como inativo")
    
    def get_queryset(self, request):
        """Otimizar consultas com select_related"""
        return super().get_queryset(request).select_related(
            'usuario', 'personagem', 'campanha', 'aprovado_por'
        )
