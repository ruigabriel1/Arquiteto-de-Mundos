"""
Modelos para o sistema de Mestre IA - "Arquiteto de Mundos"
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import json

Usuario = get_user_model()


class TipoConteudo(models.TextChoices):
    """Tipos de conteúdo que a IA pode gerar"""
    NARRATIVA = 'NARRATIVA', 'Narrativa'
    NPC = 'NPC', 'Personagem Não Jogável'
    LOCAL = 'LOCAL', 'Local/Cenário'
    MISSAO = 'MISSAO', 'Missão/Quest'
    ITEM = 'ITEM', 'Item/Artefato'
    MONSTRO = 'MONSTRO', 'Criatura/Monstro'
    EVENTO = 'EVENTO', 'Evento/Acontecimento'
    DIALOGO = 'DIALOGO', 'Diálogo/Conversa'
    ENIGMA = 'ENIGMA', 'Enigma/Puzzle'
    RECOMPENSA = 'RECOMPENSA', 'Recompensa/Tesouro'


class EstiloNarrativo(models.TextChoices):
    """Estilos narrativos da IA"""
    EPICO = 'EPICO', 'Épico e Grandioso'
    MISTERIOSO = 'MISTERIOSO', 'Misterioso e Intrigante'
    SOMBRIO = 'SOMBRIO', 'Sombrio e Gótico'
    HEROICO = 'HEROICO', 'Heroico e Inspirador'
    COMICO = 'COMICO', 'Cômico e Leviano'
    REALISTA = 'REALISTA', 'Realista e Crível'
    ROMANTICO = 'ROMANTICO', 'Romântico e Emotivo'
    HORROR = 'HORROR', 'Terror e Suspense'


class SessaoIA(models.Model):
    """
    Representa uma sessão com o Mestre IA
    Mantém contexto e memória da interação
    """
    campanha = models.ForeignKey('campanhas.Campanha', on_delete=models.CASCADE, related_name='sessoes_ia')
    nome = models.CharField(max_length=200, help_text="Nome/título da sessão")
    descricao = models.TextField(blank=True, help_text="Descrição ou resumo da sessão")
    
    # Configurações de personalidade da IA
    estilo_narrativo = models.CharField(
        max_length=20, 
        choices=EstiloNarrativo.choices, 
        default=EstiloNarrativo.EPICO,
        help_text="Estilo narrativo predominante"
    )
    criatividade_nivel = models.IntegerField(
        default=7, 
        help_text="Nível de criatividade (1-10)"
    )
    dificuldade_nivel = models.IntegerField(
        default=5, 
        help_text="Nível de dificuldade dos desafios (1-10)"
    )
    
    # Estado da sessão
    ativa = models.BooleanField(default=False)
    contexto_atual = models.JSONField(
        default=dict, 
        help_text="Contexto atual da sessão (locais, NPCs presentes, etc.)"
    )
    memoria_curto_prazo = models.JSONField(
        default=list, 
        help_text="Memória de curto prazo (últimas 10-20 interações)"
    )
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    total_interacoes = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Sessão de IA"
        verbose_name_plural = "Sessões de IA"
        ordering = ['-data_atualizacao']
    
    def __str__(self):
        return f"{self.nome} - {self.campanha.nome}"
    
    def adicionar_memoria(self, evento):
        """Adiciona evento à memória de curto prazo"""
        if not isinstance(self.memoria_curto_prazo, list):
            self.memoria_curto_prazo = []
        
        self.memoria_curto_prazo.append({
            'timestamp': timezone.now().isoformat(),
            'evento': evento
        })
        
        # Manter apenas as últimas 20 interações
        if len(self.memoria_curto_prazo) > 20:
            self.memoria_curto_prazo = self.memoria_curto_prazo[-20:]
        
        self.save()
    
    def obter_contexto_completo(self):
        """Retorna contexto completo para a IA"""
        return {
            'campanha': {
                'nome': self.campanha.nome,
                'sistema': self.campanha.sistema,
                'descricao': self.campanha.descricao,
            },
            'personagens': [
                {
                    'nome': p.nome,
                    'classe': p.classe,
                    'raca': p.raca,
                    'historia': p.historia,
                } for p in self.campanha.personagens.all()
            ],
            'contexto_atual': self.contexto_atual,
            'memoria_recente': self.memoria_curto_prazo[-10:],  # Últimas 10
            'estilo': self.estilo_narrativo,
            'configuracoes': {
                'criatividade': self.criatividade_nivel,
                'dificuldade': self.dificuldade_nivel,
            }
        }


class NPCGerado(models.Model):
    """
    NPCs gerados pela IA com personalidade completa
    """
    sessao = models.ForeignKey(SessaoIA, on_delete=models.CASCADE, related_name='npcs')
    campanha = models.ForeignKey('campanhas.Campanha', on_delete=models.CASCADE, related_name='npcs_ia')
    
    # Informações básicas
    nome = models.CharField(max_length=100)
    titulo = models.CharField(max_length=100, blank=True, help_text="Título ou apelido")
    raca = models.CharField(max_length=50, blank=True)
    classe = models.CharField(max_length=50, blank=True)
    ocupacao = models.CharField(max_length=100, blank=True)
    
    # Descrição física
    descricao_fisica = models.TextField(help_text="Aparência física detalhada")
    idade_aparente = models.CharField(max_length=50, blank=True)
    
    # Personalidade (seguindo as diretrizes da IA)
    motivacao_principal = models.TextField(help_text="Motivação clara do NPC")
    falha_personalidade = models.TextField(help_text="Falha ou fraqueza de personalidade")
    segredo = models.TextField(help_text="Segredo que o NPC guarda")
    
    # Comportamento e fala
    maneirismos = models.TextField(blank=True, help_text="Maneirismos únicos")
    padrao_fala = models.TextField(blank=True, help_text="Como fala (sotaque, gírias, etc.)")
    vocabulario = models.TextField(blank=True, help_text="Palavras e frases características")
    
    # Relacionamentos
    aliados = models.TextField(blank=True, help_text="Aliados e amigos")
    inimigos = models.TextField(blank=True, help_text="Inimigos e rivais")
    familia = models.TextField(blank=True, help_text="Família e parentes")
    
    # Informações de jogo
    nivel_poder = models.IntegerField(default=1, help_text="Nível aproximado de poder")
    recursos = models.TextField(blank=True, help_text="Recursos disponíveis")
    influencia = models.TextField(blank=True, help_text="Influência política/social")
    
    # Estado atual
    localizacao_atual = models.CharField(max_length=100, blank=True)
    disposicao = models.CharField(
        max_length=20,
        choices=[
            ('AMIGAVEL', 'Amigável'),
            ('NEUTRO', 'Neutro'),
            ('HOSTIL', 'Hostil'),
            ('SUSPEITO', 'Suspeito'),
            ('INTERESSADO', 'Interessado'),
        ],
        default='NEUTRO'
    )
    
    # Metadados
    ativo = models.BooleanField(default=True)
    primeiro_encontro = models.BooleanField(default=True)
    interacoes_count = models.PositiveIntegerField(default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_ultima_interacao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "NPC Gerado"
        verbose_name_plural = "NPCs Gerados"
        ordering = ['-data_ultima_interacao', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.campanha.nome})"
    
    def registrar_interacao(self):
        """Registra uma nova interação com o NPC"""
        self.interacoes_count += 1
        self.data_ultima_interacao = timezone.now()
        if self.primeiro_encontro:
            self.primeiro_encontro = False
        self.save()
    
    def gerar_dialogo_contexto(self):
        """Gera contexto para diálogo baseado na personalidade"""
        return {
            'personalidade': {
                'motivacao': self.motivacao_principal,
                'falha': self.falha_personalidade,
                'segredo': self.segredo,
                'maneirismos': self.maneirismos,
                'fala': self.padrao_fala,
            },
            'estado': {
                'disposicao': self.disposicao,
                'primeiro_encontro': self.primeiro_encontro,
                'interacoes': self.interacoes_count,
            }
        }


class InteracaoIA(models.Model):
    """
    Registro de todas as interações com a IA
    """
    sessao = models.ForeignKey(SessaoIA, on_delete=models.CASCADE, related_name='interacoes')
    
    # Contexto da interação
    tipo_interacao = models.CharField(
        max_length=20,
        choices=TipoConteudo.choices
    )
    prompt_usuario = models.TextField(help_text="O que o usuário/jogador pediu")
    contexto = models.JSONField(default=dict, help_text="Contexto usado para gerar a resposta")
    
    # Resposta da IA
    resposta_ia = models.TextField(help_text="Resposta gerada pela IA")
    tokens_usados = models.PositiveIntegerField(default=0)
    tempo_geracao = models.FloatField(default=0.0, help_text="Tempo de geração em segundos")
    
    # Referências a conteúdo criado
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    conteudo_relacionado = GenericForeignKey('content_type', 'object_id')
    
    # Avaliação
    avaliacao_usuario = models.IntegerField(
        null=True, 
        blank=True,
        choices=[
            (1, '1 - Ruim'),
            (2, '2 - Regular'),
            (3, '3 - Bom'),
            (4, '4 - Muito Bom'),
            (5, '5 - Excelente'),
        ],
        help_text="Avaliação do usuário sobre a resposta"
    )
    feedback = models.TextField(blank=True, help_text="Feedback detalhado do usuário")
    
    # Metadados
    data_interacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='interacoes_ia')
    
    class Meta:
        verbose_name = "Interação com IA"
        verbose_name_plural = "Interações com IA"
        ordering = ['-data_interacao']
    
    def __str__(self):
        return f"{self.get_tipo_interacao_display()} - {self.data_interacao.strftime('%d/%m/%Y %H:%M')}"


class MemoriaLongoPrazo(models.Model):
    """
    Sistema de memória de longo prazo da IA
    Armazena eventos importantes e consequências
    """
    campanha = models.ForeignKey('campanhas.Campanha', on_delete=models.CASCADE, related_name='memorias_ia')
    
    # Informações do evento
    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    categoria = models.CharField(
        max_length=20,
        choices=[
            ('DECISAO', 'Decisão Importante'),
            ('CONSEQUENCIA', 'Consequência de Ação'),
            ('RELACIONAMENTO', 'Mudança de Relacionamento'),
            ('DESCOBERTA', 'Descoberta Significativa'),
            ('CONQUISTA', 'Conquista/Vitória'),
            ('PERDA', 'Perda/Derrota'),
            ('MUDANCA_MUNDO', 'Mudança no Mundo'),
        ]
    )
    
    # Contexto e impacto
    personagens_envolvidos = models.ManyToManyField('personagens.Personagem', blank=True)
    impacto_narrativo = models.TextField(help_text="Como este evento afeta a narrativa futura")
    consequencias_pendentes = models.TextField(blank=True, help_text="Consequências que ainda não se manifestaram")
    
    # Importância e relevância
    importancia = models.IntegerField(
        default=3,
        choices=[
            (1, 'Trivial'),
            (2, 'Menor'),
            (3, 'Moderada'),
            (4, 'Grande'),
            (5, 'Épica'),
        ]
    )
    
    # Estado
    resolvido = models.BooleanField(default=False)
    data_evento = models.DateTimeField()
    data_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Memória de Longo Prazo"
        verbose_name_plural = "Memórias de Longo Prazo"
        ordering = ['-importancia', '-data_evento']
    
    def __str__(self):
        return f"{self.titulo} ({self.get_categoria_display()})"
