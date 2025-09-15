"""
Modelos para o Sistema Unificado - D&D 5e + Tormenta20
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class SistemaJogo(models.Model):
    """Sistemas de jogo suportados"""
    
    SISTEMAS_CHOICES = [
        ('dnd5e', 'D&D 5th Edition'),
        ('t20', 'Tormenta20'),
        ('unified', 'Sistema Unificado'),
    ]
    
    nome = models.CharField(
        _("Nome"),
        max_length=50,
        help_text=_("Nome do sistema de jogo")
    )
    
    codigo = models.CharField(
        _("Código"),
        max_length=10,
        unique=True,
        choices=SISTEMAS_CHOICES,
        help_text=_("Código único do sistema")
    )
    
    versao = models.CharField(
        _("Versão"),
        max_length=20,
        help_text=_("Versão do sistema (ex: 5.1, 1.0)")
    )
    
    descricao = models.TextField(
        _("Descrição"),
        blank=True,
        help_text=_("Descrição detalhada do sistema")
    )
    
    configuracoes = models.JSONField(
        _("Configurações"),
        default=dict,
        help_text=_("Configurações específicas do sistema")
    )
    
    ativo = models.BooleanField(
        _("Ativo"),
        default=True,
        help_text=_("Sistema disponível para uso")
    )
    
    data_criacao = models.DateTimeField(
        _("Data de Criação"),
        auto_now_add=True
    )
    
    data_atualizacao = models.DateTimeField(
        _("Última Atualização"),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _("Sistema de Jogo")
        verbose_name_plural = _("Sistemas de Jogo")
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.versao})"


class ConteudoSistema(models.Model):
    """Conteúdo dos sistemas (classes, raças, magias, etc.)"""
    
    TIPOS_CONTEUDO = [
        ('raca', _("Raça")),
        ('classe', _("Classe")),
        ('magia', _("Magia")),
        ('item', _("Item/Equipamento")),
        ('monstro', _("Monstro/Criatura")),
        ('pericia', _("Perícia")),
        ('talento', _("Talento/Feat")),
        ('antecedente', _("Antecedente")),
    ]
    
    sistema_jogo = models.ForeignKey(
        SistemaJogo,
        on_delete=models.CASCADE,
        related_name='conteudos',
        verbose_name=_("Sistema de Jogo")
    )
    
    tipo = models.CharField(
        _("Tipo"),
        max_length=20,
        choices=TIPOS_CONTEUDO,
        help_text=_("Tipo do conteúdo")
    )
    
    nome = models.CharField(
        _("Nome"),
        max_length=100,
        help_text=_("Nome do elemento")
    )
    
    descricao = models.TextField(
        _("Descrição"),
        help_text=_("Descrição detalhada do elemento")
    )
    
    dados_originais = models.JSONField(
        _("Dados Originais"),
        help_text=_("Dados no formato original do sistema")
    )
    
    dados_convertidos = models.JSONField(
        _("Dados Convertidos"),
        default=dict,
        help_text=_("Dados convertidos para o sistema unificado")
    )
    
    equivalencias = models.JSONField(
        _("Equivalências"),
        default=dict,
        help_text=_("Mapeamentos de equivalência entre sistemas")
    )
    
    nivel_minimo = models.PositiveSmallIntegerField(
        _("Nível Mínimo"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text=_("Nível mínimo para usar este conteúdo")
    )
    
    tags = models.JSONField(
        _("Tags"),
        default=list,
        help_text=_("Tags para categorização e busca")
    )
    
    ativo = models.BooleanField(
        _("Ativo"),
        default=True,
        help_text=_("Conteúdo disponível para uso")
    )
    
    data_criacao = models.DateTimeField(
        _("Data de Criação"),
        auto_now_add=True
    )
    
    data_atualizacao = models.DateTimeField(
        _("Última Atualização"),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _("Conteúdo do Sistema")
        verbose_name_plural = _("Conteúdos dos Sistemas")
        ordering = ['tipo', 'nome']
        indexes = [
            models.Index(fields=['sistema_jogo', 'tipo']),
            models.Index(fields=['tipo', 'nivel_minimo']),
        ]
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()}) - {self.sistema_jogo.codigo}"


class EquivalenciaConteudo(models.Model):
    """Equivalências diretas entre conteúdos de diferentes sistemas"""
    
    conteudo_origem = models.ForeignKey(
        ConteudoSistema,
        on_delete=models.CASCADE,
        related_name='equivalencias_como_origem',
        verbose_name=_("Conteúdo de Origem")
    )
    
    conteudo_destino = models.ForeignKey(
        ConteudoSistema,
        on_delete=models.CASCADE,
        related_name='equivalencias_como_destino',
        verbose_name=_("Conteúdo de Destino")
    )
    
    nivel_equivalencia = models.PositiveSmallIntegerField(
        _("Nível de Equivalência"),
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=100,
        help_text=_("Porcentagem de equivalência (1-100%)")
    )
    
    observacoes = models.TextField(
        _("Observações"),
        blank=True,
        help_text=_("Observações sobre a equivalência")
    )
    
    data_criacao = models.DateTimeField(
        _("Data de Criação"),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("Equivalência de Conteúdo")
        verbose_name_plural = _("Equivalências de Conteúdo")
        unique_together = ['conteudo_origem', 'conteudo_destino']
    
    def __str__(self):
        return f"{self.conteudo_origem} ↔ {self.conteudo_destino} ({self.nivel_equivalencia}%)"
