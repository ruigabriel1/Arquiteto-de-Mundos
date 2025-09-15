"""
Modelos para fichas de personagem do sistema unificado
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Personagem(models.Model):
    """Fichas de personagem para o sistema unificado"""
    
    # Identificação
    nome = models.CharField(
        _("Nome"),
        max_length=100,
        help_text=_("Nome do personagem")
    )
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='personagens',
        verbose_name=_("Usuário")
    )
    
    campanha = models.ForeignKey(
        'campanhas.Campanha',
        on_delete=models.CASCADE,
        related_name='personagens',
        verbose_name=_("Campanha")
    )
    
    sistema_jogo = models.ForeignKey(
        'sistema_unificado.SistemaJogo',
        on_delete=models.PROTECT,
        verbose_name=_("Sistema de Jogo")
    )
    
    # Imagem do personagem
    avatar = models.ImageField(
        _("Avatar"),
        upload_to='personagens/avatares/',
        null=True,
        blank=True,
        help_text=_("Imagem do personagem")
    )
    
    # Progressão
    nivel = models.PositiveSmallIntegerField(
        _("Nível"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    
    experiencia = models.PositiveIntegerField(
        _("Pontos de Experiência"),
        default=0,
        help_text=_("XP acumulado")
    )
    
    # Atributos primários (sistema unificado 3-18)
    forca = models.PositiveSmallIntegerField(
        _("Força"),
        default=10,
        validators=[MinValueValidator(3), MaxValueValidator(18)]
    )
    
    destreza = models.PositiveSmallIntegerField(
        _("Destreza"),
        default=10,
        validators=[MinValueValidator(3), MaxValueValidator(18)]
    )
    
    constituicao = models.PositiveSmallIntegerField(
        _("Constituição"),
        default=10,
        validators=[MinValueValidator(3), MaxValueValidator(18)]
    )
    
    inteligencia = models.PositiveSmallIntegerField(
        _("Inteligência"),
        default=10,
        validators=[MinValueValidator(3), MaxValueValidator(18)]
    )
    
    sabedoria = models.PositiveSmallIntegerField(
        _("Sabedoria"),
        default=10,
        validators=[MinValueValidator(3), MaxValueValidator(18)]
    )
    
    carisma = models.PositiveSmallIntegerField(
        _("Carisma"),
        default=10,
        validators=[MinValueValidator(3), MaxValueValidator(18)]
    )
    
    # Pontos de Vida
    pontos_vida_max = models.PositiveSmallIntegerField(
        _("PV Máximo"),
        default=8,
        help_text=_("Pontos de vida máximos")
    )
    
    pontos_vida_atual = models.PositiveSmallIntegerField(
        _("PV Atual"),
        default=8,
        help_text=_("Pontos de vida atuais")
    )
    
    pontos_vida_temporarios = models.PositiveSmallIntegerField(
        _("PV Temporários"),
        default=0,
        help_text=_("Pontos de vida temporários")
    )
    
    # Classe Armadura e Defesas
    classe_armadura = models.PositiveSmallIntegerField(
        _("CA"),
        default=10,
        help_text=_("Classe de Armadura")
    )
    
    # Dados flexíveis por sistema (JSONFields)
    raca = models.JSONField(
        _("Raça"),
        default=dict,
        help_text=_("Dados da raça: {'nome': 'Elfo', 'origem': 'dnd5e', 'tracos': [...]}")
    )
    
    classes = models.JSONField(
        _("Classes"),
        default=list,
        help_text=_("Lista de classes: [{'nome': 'Guerreiro', 'nivel': 5, 'origem': 't20'}]")
    )
    
    antecedente = models.JSONField(
        _("Antecedente"),
        default=dict,
        help_text=_("Background/Antecedente do personagem")
    )
    
    pericias = models.JSONField(
        _("Perícias"),
        default=list,
        help_text=_("Lista de perícias e proficiências")
    )
    
    magias_conhecidas = models.JSONField(
        _("Magias Conhecidas"),
        default=list,
        help_text=_("Lista de magias do personagem")
    )
    
    equipamentos = models.JSONField(
        _("Equipamentos"),
        default=list,
        help_text=_("Inventário e equipamentos")
    )
    
    talentos = models.JSONField(
        _("Talentos"),
        default=list,
        help_text=_("Lista de talentos/feats")
    )
    
    # Sistema unificado - dados convertidos
    dados_unificados = models.JSONField(
        _("Dados Unificados"),
        default=dict,
        help_text=_("Dados convertidos para o sistema unificado")
    )
    
    # Informações narrativas
    historia = models.TextField(
        _("História"),
        blank=True,
        help_text=_("Background e história do personagem")
    )
    
    personalidade = models.TextField(
        _("Personalidade"),
        blank=True,
        help_text=_("Traços de personalidade, ideais, vínculos e defeitos")
    )
    
    anotacoes_jogador = models.TextField(
        _("Anotações do Jogador"),
        blank=True,
        help_text=_("Anotações pessoais do jogador")
    )
    
    anotacoes_mestre = models.TextField(
        _("Anotações do Mestre"),
        blank=True,
        help_text=_("Anotações visíveis apenas ao mestre")
    )
    
    # Status do personagem
    ativo = models.BooleanField(
        _("Ativo"),
        default=True,
        help_text=_("Personagem ativo na campanha")
    )
    
    publico = models.BooleanField(
        _("Público"),
        default=False,
        help_text=_("Ficha visível para outros jogadores")
    )
    
    # Metadados
    data_criacao = models.DateTimeField(
        _("Data de Criação"),
        auto_now_add=True
    )
    
    data_atualizacao = models.DateTimeField(
        _("Última Atualização"),
        auto_now=True
    )
    
    versao = models.PositiveSmallIntegerField(
        _("Versão"),
        default=1,
        help_text=_("Versão da ficha (para backup)")
    )
    
    class Meta:
        verbose_name = _("Personagem")
        verbose_name_plural = _("Personagens")
        ordering = ['nome']
        indexes = [
            models.Index(fields=['usuario', 'campanha']),
            models.Index(fields=['campanha', 'ativo']),
        ]
    
    def __str__(self):
        return f"{self.nome} (N{self.nivel}) - {self.usuario.username}"
    
    # Propriedades calculadas
    @property
    def modificador_forca(self):
        """Modificador de Força"""
        return (self.forca - 10) // 2
    
    @property
    def modificador_destreza(self):
        """Modificador de Destreza"""
        return (self.destreza - 10) // 2
    
    @property
    def modificador_constituicao(self):
        """Modificador de Constituição"""
        return (self.constituicao - 10) // 2
    
    @property
    def modificador_inteligencia(self):
        """Modificador de Inteligência"""
        return (self.inteligencia - 10) // 2
    
    @property
    def modificador_sabedoria(self):
        """Modificador de Sabedoria"""
        return (self.sabedoria - 10) // 2
    
    @property
    def modificador_carisma(self):
        """Modificador de Carisma"""
        return (self.carisma - 10) // 2
    
    @property
    def bonus_proficiencia(self):
        """Bônus de proficiência baseado no nível"""
        return 2 + (self.nivel - 1) // 4
    
    @property
    def morto(self):
        """Verifica se o personagem está morto"""
        return self.pontos_vida_atual <= 0
    
    @property
    def classe_principal(self):
        """Retorna a classe de maior nível"""
        if not self.classes:
            return None
        return max(self.classes, key=lambda c: c.get('nivel', 0))
    
    def pode_editar(self, usuario):
        """Verifica se o usuário pode editar este personagem"""
        return (
            usuario == self.usuario or
            usuario == self.campanha.organizador or
            usuario.is_staff
        )
    
    def pode_visualizar(self, usuario):
        """Verifica se o usuário pode visualizar este personagem"""
        if self.pode_editar(usuario):
            return True
        
        if self.publico:
            # Verifica se é participante da mesma campanha
            return self.campanha.participacoes.filter(
                usuario=usuario, ativo=True
            ).exists()
        
        return False
    
    def calcular_modificador(self, valor_atributo):
        """Calcular modificador D&D para qualquer atributo"""
        return (valor_atributo - 10) // 2
    
    def calcular_pontos_vida_iniciais(self):
        """Calcular pontos de vida iniciais baseado na classe e constituição"""
        # Valores base por classe principal (simplificado)
        classe_principal = self.classe_principal
        if not classe_principal:
            dado_vida = 6  # Padrão
        else:
            # Mapear classes para dados de vida
            mapeamento_dados = {
                'guerreiro': 10, 'paladino': 10, 'ranger': 10,
                'barbaro': 12,
                'clerigo': 8, 'druida': 8, 'mago': 6, 'feiticeiro': 6,
                'ladino': 8, 'bardo': 8
            }
            classe_nome = classe_principal.get('nome', '').lower()
            dado_vida = mapeamento_dados.get(classe_nome, 8)
        
        # Pontos de vida = (dado de vida máximo) + modificador constituição
        self.pontos_vida_maximo = dado_vida + self.modificador_constituicao
        self.pontos_vida_atual = self.pontos_vida_maximo
        
        return self.pontos_vida_maximo
    
    def calcular_pontos_vida_maximos(self):
        """Recalcular pontos de vida máximos baseado no nível atual"""
        classe_principal = self.classe_principal
        if not classe_principal:
            dado_vida = 6
        else:
            mapeamento_dados = {
                'guerreiro': 10, 'paladino': 10, 'ranger': 10,
                'barbaro': 12,
                'clerigo': 8, 'druida': 8, 'mago': 6, 'feiticeiro': 6,
                'ladino': 8, 'bardo': 8
            }
            classe_nome = classe_principal.get('nome', '').lower()
            dado_vida = mapeamento_dados.get(classe_nome, 8)
        
        # Nível 1: máximo do dado + CON
        # Níveis seguintes: média do dado + CON por nível
        media_dado = (dado_vida // 2) + 1
        
        pontos_nivel_1 = dado_vida + self.modificador_constituicao
        pontos_niveis_extras = (self.nivel - 1) * (media_dado + self.modificador_constituicao)
        
        self.pontos_vida_maximo = max(1, pontos_nivel_1 + pontos_niveis_extras)
        return self.pontos_vida_maximo
    
    def calcular_classe_armadura(self):
        """Calcular classe de armadura base (10 + DEX)"""
        # Classe de armadura base = 10 + modificador de Destreza
        # TODO: Considerar armaduras e escudos dos equipamentos
        self.classe_armadura = 10 + self.modificador_destreza
        return self.classe_armadura
    
    def calcular_iniciativa(self):
        """Calcular bônus de iniciativa (DEX)"""
        self.iniciativa = self.modificador_destreza
        return self.iniciativa
    
    def to_dict(self):
        """Converter personagem para dicionário (para backup)"""
        return {
            'nome': self.nome,
            'nivel': self.nivel,
            'experiencia': self.experiencia,
            'forca': self.forca,
            'destreza': self.destreza,
            'constituicao': self.constituicao,
            'inteligencia': self.inteligencia,
            'sabedoria': self.sabedoria,
            'carisma': self.carisma,
            'pontos_vida_maximo': self.pontos_vida_maximo,
            'pontos_vida_atual': self.pontos_vida_atual,
            'pontos_vida_temporario': self.pontos_vida_temporario,
            'classe_armadura': self.classe_armadura,
            'iniciativa': self.iniciativa,
            'raca': self.raca,
            'classes': self.classes,
            'antecedente': self.antecedente,
            'pericias': self.pericias,
            'magias_conhecidas': self.magias_conhecidas,
            'equipamentos': self.equipamentos,
            'talentos': self.talentos,
            'historia': self.historia,
            'personalidade': self.personalidade,
            'anotacoes_jogador': self.anotacoes_jogador,
            'publico': self.publico,
            'versao': self.versao
        }
    
    def from_dict(self, dados):
        """Restaurar personagem de dicionário (backup)"""
        campos_permitidos = [
            'nome', 'nivel', 'experiencia', 'forca', 'destreza', 'constituicao',
            'inteligencia', 'sabedoria', 'carisma', 'pontos_vida_maximo',
            'pontos_vida_atual', 'pontos_vida_temporario', 'classe_armadura',
            'iniciativa', 'raca', 'classes', 'antecedente', 'pericias',
            'magias_conhecidas', 'equipamentos', 'talentos', 'historia',
            'personalidade', 'anotacoes_jogador', 'publico'
        ]
        
        for campo in campos_permitidos:
            if campo in dados:
                setattr(self, campo, dados[campo])
        
        # Incrementar versão
        self.versao += 1


class HistoricoPersonagem(models.Model):
    """Histórico de mudanças no personagem"""
    
    TIPOS_MUDANCA = [
        ('subida_nivel', _("Subida de Nível")),
        ('mudanca_atributo', _("Mudança de Atributo")),
        ('nova_magia', _("Nova Magia")),
        ('novo_equipamento', _("Novo Equipamento")),
        ('dano', _("Dano Recebido")),
        ('cura', _("Cura Recebida")),
        ('outro', _("Outro")),
    ]
    
    personagem = models.ForeignKey(
        Personagem,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name=_("Personagem")
    )
    
    tipo = models.CharField(
        _("Tipo de Mudança"),
        max_length=20,
        choices=TIPOS_MUDANCA
    )
    
    descricao = models.TextField(
        _("Descrição"),
        help_text=_("Descrição da mudança")
    )
    
    dados_anteriores = models.JSONField(
        _("Dados Anteriores"),
        null=True,
        blank=True,
        help_text=_("Estado anterior do personagem")
    )
    
    dados_novos = models.JSONField(
        _("Dados Novos"),
        null=True,
        blank=True,
        help_text=_("Novo estado do personagem")
    )
    
    usuario_mudanca = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Usuário que fez a mudança")
    )
    
    data_mudanca = models.DateTimeField(
        _("Data da Mudança"),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("Histórico do Personagem")
        verbose_name_plural = _("Históricos dos Personagens")
        ordering = ['-data_mudanca']
    
    def __str__(self):
        return f"{self.personagem.nome} - {self.get_tipo_display()} ({self.data_mudanca.strftime('%d/%m/%Y')})"


class BackupPersonagem(models.Model):
    """Backups automáticos das fichas"""
    
    personagem = models.ForeignKey(
        Personagem,
        on_delete=models.CASCADE,
        related_name='backups',
        verbose_name=_("Personagem")
    )
    
    versao = models.PositiveSmallIntegerField(
        _("Versão"),
        help_text=_("Número da versão do backup")
    )
    
    dados_personagem = models.JSONField(
        _("Dados do Personagem"),
        help_text=_("Snapshot completo da ficha")
    )
    
    motivo_backup = models.CharField(
        _("Motivo do Backup"),
        max_length=100,
        help_text=_("Razão para criação do backup")
    )
    
    data_backup = models.DateTimeField(
        _("Data do Backup"),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("Backup de Personagem")
        verbose_name_plural = _("Backups de Personagens")
        ordering = ['-versao']
        unique_together = ['personagem', 'versao']
    
    def __str__(self):
        return f"Backup {self.versao} - {self.personagem.nome} ({self.data_backup.strftime('%d/%m/%Y')})"
