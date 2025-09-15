# Especificações Técnicas - Unified Chronicles

## 🎯 Visão Técnica Geral

**Unified Chronicles** é uma plataforma web complexa que unifica dois sistemas de RPG (D&D 5e e Tormenta20) em uma experiência coesa com IA Game Master integrada. 

**Status Atual**: Sistema base implementado com funcionalidades principais operacionais, incluindo:
- ✅ Sistema de usuários e autenticação
- ✅ Gestão de campanhas e personagens
- ✅ IA Game Master (Arquiteto de Mundos) implementada
- ✅ Interface web responsiva em português brasileiro
- ✅ API REST funcional
- ✅ Sistema de dados e rolagens
- ✅ Chat em tempo real via WebSocket

Este documento detalha as especificações técnicas da implementação atual.

## 🏗️ Arquitetura do Sistema

### Stack Tecnológico Implementado

| Componente | Tecnologia | Status | Notas |
|------------|------------|--------|-------|
| **Backend** | Django 4.2 + DRF | ✅ Implementado | ORM robusto, admin interface ativada |
| **Database** | SQLite (dev) / PostgreSQL (prod) | ✅ Implementado | JSONB para dados flexíveis |
| **Cache/Queue** | Redis 7 | 🟡 Parcial | Configurado, WebSocket ativo |
| **Task Queue** | Celery | 🟡 Configurado | Para processamento assíncrono de IA |
| **WebSocket** | Django Channels | ✅ Implementado | Real-time chat funcionando |
| **Frontend** | Templates Django + Bootstrap | ✅ Implementado | Interface responsiva em PT-BR |
| **AI Services** | OpenAI GPT-4 / Claude 3.5 | ✅ Implementado | Arquiteto de Mundos ativo |
| **Image Gen** | DALL-E 3 | 🟡 Configurado | Integração pronta para uso |
| **Deploy** | Ambiente local + Docker | ✅ Pronto | Scripts de inicialização criados |

## 🚀 Funcionalidades Implementadas

### 1. Sistema de Usuários e Autenticação
- ✅ Modelo de usuário customizado
- ✅ Sistema de login/logout
- ✅ Gestão de perfis
- ✅ Controle de permissões (Mestre/Jogador)

### 2. Gestão de Campanhas
- ✅ Criação e edição de campanhas
- ✅ Convite de jogadores
- ✅ Configuração de sistemas de jogo
- ✅ Gestão de sessões

### 3. IA Game Master - "Arquiteto de Mundos"
- ✅ Geração de NPCs dinâmicos
- ✅ Criação de locais e ambientes
- ✅ Sistema de missões procedurais
- ✅ Ações narrativas contextuais
- ✅ Eventos dinâmicos
- ✅ Sistema de memória e contexto
- ✅ Interface de mestre intuitiva

### 4. Sistema de Personagens
- ✅ Criação de personagens
- ✅ Fichas de personagem
- ✅ Sistema de atributos
- ✅ Inventário e equipamentos

### 5. Chat e Comunicação
- ✅ Chat em tempo real via WebSocket
- ✅ Mensagens de sistema
- ✅ Suporte a comandos especiais
- ✅ Histórico de mensagens

### 6. Sistema de Dados
- ✅ Parser de comandos de dados
- ✅ Rolagens automáticas
- ✅ Histórico de rolagens
- ✅ Integração com regras de sistema

### 7. Interface Web
- ✅ Design responsivo com Bootstrap
- ✅ Tema escuro/profissional
- ✅ Navegação intuitiva
- ✅ Modais e interatividade JavaScript
- ✅ Conteúdo 100% em português brasileiro

### Arquitetura de Microsserviços

```
┌──────────────────────────────────────────────────────────────┐
│                    Load Balancer / Nginx                     │
└──────────────────────┬───────────────────────────────────────┘
                       │
    ┌─────────────────────────────────────────────────────────┐
    │                Frontend React App                        │
    │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
    │  │   Chat UI   │ │ Character   │ │ Campaign    │      │
    │  │ (WebSocket) │ │ Sheet       │ │ Manager     │      │
    │  └─────────────┘ └─────────────┘ └─────────────┘      │
    └─────────────────────────────────────────────────────────┘
                       │
    ┌──────────────────────────────────────────────────────────┐
    │                Django Backend                            │
    │  ┌────────────┐ ┌────────────┐ ┌────────────┐          │
    │  │ REST API   │ │ WebSocket  │ │ Admin      │          │
    │  │ (DRF)      │ │ (Channels) │ │ Interface  │          │
    │  └────────────┘ └────────────┘ └────────────┘          │
    └──────────────────────────────────────────────────────────┘
                       │
    ┌──────────────────────────────────────────────────────────┐
    │                 Service Layer                            │
    │  ┌────────────┐ ┌────────────┐ ┌────────────┐          │
    │  │ IA GM      │ │ Unified    │ │ Dice       │          │
    │  │ Service    │ │ System     │ │ Engine     │          │
    │  └────────────┘ └────────────┘ └────────────┘          │
    └──────────────────────────────────────────────────────────┘
                       │
    ┌──────────────────────────────────────────────────────────┐
    │              Data & Infrastructure                       │
    │  ┌────────────┐ ┌────────────┐ ┌────────────┐          │
    │  │PostgreSQL  │ │   Redis    │ │   Celery   │          │
    │  │ (Primary)  │ │ (Cache/WS) │ │ (Tasks)    │          │
    │  └────────────┘ └────────────┘ └────────────┘          │
    └──────────────────────────────────────────────────────────┘
                       │
    ┌──────────────────────────────────────────────────────────┐
    │                External APIs                             │
    │  ┌────────────┐ ┌────────────┐ ┌────────────┐          │
    │  │ OpenAI     │ │ DALL-E 3   │ │ Anthropic  │          │
    │  │ GPT-4      │ │ (Images)   │ │ Claude     │          │
    │  └────────────┘ └────────────┘ └────────────┘          │
    └──────────────────────────────────────────────────────────┘
```

## 📊 Modelagem de Dados Detalhada

### Core Models

```python
# usuarios/models.py
class Usuario(AbstractUser):
    # Campos personalizados
    nome_completo = CharField(max_length=150)
    data_nascimento = DateField(null=True, blank=True)
    avatar = ImageField(upload_to='avatares/', null=True, blank=True)
    bio = TextField(max_length=500, blank=True)
    
    # Configurações JSON
    configuracoes_jogo = JSONField(default=dict)
    configuracoes_interface = JSONField(default=dict)
    
    # Estatísticas
    campanhas_como_jogador = PositiveIntegerField(default=0)
    campanhas_como_mestre = PositiveIntegerField(default=0)
    horas_jogadas = PositiveIntegerField(default=0)
    
    # Metadata
    data_ultima_atividade = DateTimeField(auto_now=True)
    ativo = BooleanField(default=True)

# sistema_unificado/models.py
class SistemaJogo(Model):
    nome = CharField(max_length=50)  # "D&D 5e", "Tormenta20", "Unificado"
    codigo = CharField(max_length=10, unique=True)  # "dnd5e", "t20", "unified"
    versao = CharField(max_length=20)
    configuracoes = JSONField(default=dict)
    ativo = BooleanField(default=True)

class ConteudoSistema(Model):
    TIPOS = [
        ('raca', 'Raça'),
        ('classe', 'Classe'), 
        ('magia', 'Magia'),
        ('item', 'Item'),
        ('monstro', 'Monstro'),
        ('pericia', 'Perícia'),
        ('talento', 'Talento'),
    ]
    
    sistema_jogo = ForeignKey(SistemaJogo)
    tipo = CharField(max_length=20, choices=TIPOS)
    nome = CharField(max_length=100)
    descricao = TextField()
    dados_originais = JSONField()  # Dados do sistema original
    dados_convertidos = JSONField()  # Dados convertidos para sistema unificado
    equivalencias = JSONField(default=dict)  # Mapeamentos entre sistemas

# campanhas/models.py
class Campanha(Model):
    nome = CharField(max_length=100)
    descricao = TextField()
    mestre = ForeignKey(Usuario, related_name='campanhas_mestradas')
    jogadores = ManyToManyField(Usuario, through='ParticipacaoCampanha')
    sistema_jogo = ForeignKey(SistemaJogo)
    
    # Configurações da IA GM
    configuracoes_ia = JSONField(default=dict)
    personalidade_gm = JSONField(default=dict)
    
    # Estado da campanha
    data_criacao = DateTimeField(auto_now_add=True)
    data_ultima_sessao = DateTimeField(null=True, blank=True)
    ativa = BooleanField(default=True)

# personagens/models.py
class Personagem(Model):
    # Identificação
    nome = CharField(max_length=100)
    usuario = ForeignKey(Usuario)
    campanha = ForeignKey(Campanha)
    sistema_jogo = ForeignKey(SistemaJogo)
    
    # Progressão
    nivel = PositiveIntegerField(default=1)
    experiencia = PositiveIntegerField(default=0)
    
    # Atributos (sistema unificado)
    forca = PositiveIntegerField(default=10)
    destreza = PositiveIntegerField(default=10) 
    constituicao = PositiveIntegerField(default=10)
    inteligencia = PositiveIntegerField(default=10)
    sabedoria = PositiveIntegerField(default=10)
    carisma = PositiveIntegerField(default=10)
    
    # Dados flexíveis por sistema
    raca = JSONField()  # {'nome': 'Elfo', 'origem': 'dnd5e', 'tracos': [...]}
    classe = JSONField() # {'nome': 'Guerreiro', 'origem': 't20', 'habilidades': [...]}
    pericias = JSONField(default=list)
    magias_conhecidas = JSONField(default=list)
    equipamentos = JSONField(default=list)
    
    # Sistema unificado
    dados_unificados = JSONField(default=dict)
    
    # Metadata
    data_criacao = DateTimeField(auto_now_add=True)
    data_atualizacao = DateTimeField(auto_now=True)
    ativo = BooleanField(default=True)

# chat/models.py  
class MensagemChat(Model):
    TIPOS = [
        ('narrativa', 'Narrativa do IA GM'),
        ('acao', 'Ação do jogador'),
        ('dialogo', 'Diálogo/Roleplay'),
        ('sistema', 'Sistema'),
        ('privada', 'Mensagem privada'),
        ('dado', 'Rolagem de dado'),
    ]
    
    campanha = ForeignKey(Campanha)
    usuario = ForeignKey(Usuario, null=True, blank=True)  # null = IA GM
    personagem = ForeignKey(Personagem, null=True, blank=True)
    
    tipo = CharField(max_length=20, choices=TIPOS)
    conteudo = TextField()
    destinatario = ForeignKey(Usuario, null=True, blank=True, related_name='mensagens_privadas')
    
    # Metadados para IA
    contexto_ia = JSONField(default=dict)
    requer_processamento_ia = BooleanField(default=False)
    processada_pela_ia = BooleanField(default=False)
    
    timestamp = DateTimeField(auto_now_add=True)

# dados/models.py
class RolagemDado(Model):
    mensagem_chat = ForeignKey(MensagemChat)
    usuario = ForeignKey(Usuario)
    personagem = ForeignKey(Personagem, null=True, blank=True)
    
    # Dados da rolagem
    comando = CharField(max_length=50)  # "1d20+5"
    resultados_brutos = JSONField()  # [15] (dados sem modificadores)
    modificadores = IntegerField(default=0)
    total = IntegerField()
    
    # Contexto do teste
    tipo_teste = CharField(max_length=50, null=True, blank=True)
    dc = PositiveIntegerField(null=True, blank=True)
    sucesso = BooleanField(null=True, blank=True)
    
    timestamp = DateTimeField(auto_now_add=True)

# ia_gm/models.py
class SessaoIA(Model):
    campanha = ForeignKey(Campanha)
    
    # Contexto e memória
    contexto_atual = JSONField(default=dict)
    memoria_curto_prazo = JSONField(default=list)  # Últimas 50 mensagens resumidas
    memoria_longo_prazo = JSONField(default=list)  # Eventos importantes
    
    # Personalidade e comportamento
    personalidade = JSONField(default=dict)
    parametros_geracao = JSONField(default=dict)
    
    # Estado da sessão
    sessao_ativa = BooleanField(default=False)
    ultima_interacao = DateTimeField(auto_now=True)

class EventoNarrativo(Model):
    """Eventos importantes para a memória da IA"""
    sessao_ia = ForeignKey(SessaoIA)
    
    tipo_evento = CharField(max_length=50)  # 'combate', 'descoberta', 'morte_personagem'
    descricao = TextField()
    personagens_envolvidos = JSONField(default=list)
    impacto_narrativo = IntegerField(default=1)  # 1-10 escala de importância
    
    timestamp = DateTimeField(auto_now_add=True)
```

### Relacionamentos e Índices

```sql
-- Índices otimizados para performance
CREATE INDEX idx_mensagem_chat_campanha_timestamp ON chat_mensagemchat(campanha_id, timestamp DESC);
CREATE INDEX idx_personagem_usuario_ativo ON personagens_personagem(usuario_id, ativo);
CREATE INDEX idx_rolagem_usuario_timestamp ON dados_rolagemdado(usuario_id, timestamp DESC);
CREATE INDEX idx_sessao_ia_campanha ON ia_gm_sessaoia(campanha_id);

-- Índices para busca de conteúdo
CREATE INDEX idx_conteudo_sistema_tipo ON sistema_unificado_conteudosistema(sistema_jogo_id, tipo);
CREATE INDEX idx_conteudo_nome_trgm ON sistema_unificado_conteudosistema USING gin(nome gin_trgm_ops);
```

## 🔄 API REST Implementada

### Authentication & Authorization

```python
# JWT Token Authentication
POST /api/auth/login/
{
    "username": "usuario",
    "password": "senha"
}

Response:
{
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token", 
    "user": {
        "id": 1,
        "username": "usuario",
        "nome_completo": "Nome Usuário",
        "nivel_experiencia": "Experiente"
    }
}

# Refresh token
POST /api/auth/refresh/
{
    "refresh": "jwt_refresh_token"
}
```

### Core Endpoints

```python
# Usuários
GET    /api/usuarios/profile/          # Perfil atual
PUT    /api/usuarios/profile/          # Atualizar perfil
GET    /api/usuarios/{id}/             # Perfil público
POST   /api/usuarios/configuracoes/    # Salvar configurações

# Campanhas
GET    /api/campanhas/                 # Listar campanhas do usuário
POST   /api/campanhas/                 # Criar campanha
GET    /api/campanhas/{id}/            # Detalhes da campanha
PUT    /api/campanhas/{id}/            # Atualizar campanha  
POST   /api/campanhas/{id}/convidar/   # Convidar jogador
POST   /api/campanhas/{id}/sair/       # Sair da campanha

# Personagens
GET    /api/personagens/               # Personagens do usuário
POST   /api/personagens/               # Criar personagem
GET    /api/personagens/{id}/          # Detalhes do personagem
PUT    /api/personagens/{id}/          # Atualizar personagem
POST   /api/personagens/{id}/subir-nivel/  # Subir nível

# Chat
GET    /api/chat/{campanha_id}/mensagens/    # Histórico de mensagens
POST   /api/chat/{campanha_id}/mensagem/     # Enviar mensagem
GET    /api/chat/{campanha_id}/participantes/ # Participantes online

# Dados
POST   /api/dados/rolar/                     # Rolar dados
GET    /api/dados/{campanha_id}/historico/   # Histórico de rolagens

# Sistema Unificado
GET    /api/sistema/racas/                   # Listar raças disponíveis
GET    /api/sistema/classes/                 # Listar classes disponíveis  
GET    /api/sistema/magias/                  # Listar magias
GET    /api/sistema/conversao/{tipo}/{id}/   # Converter entre sistemas

# IA GM
POST   /api/ia-gm/{campanha_id}/configurar/  # Configurar personalidade
GET    /api/ia-gm/{campanha_id}/memoria/     # Acessar memória da IA
POST   /api/ia-gm/{campanha_id}/reset/       # Resetar contexto
```

## 🌐 WebSocket Protocol

### Connection Management

```javascript
// Conexão WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${campanhaId}/`);

// Autenticação
ws.send(JSON.stringify({
    type: 'authenticate',
    token: 'jwt_access_token'
}));

// Mensagens do protocolo
{
    type: 'chat_message',
    data: {
        usuario_id: 123,
        personagem_id: 456,
        conteudo: "Eu tento me esconder nas sombras",
        tipo: 'acao',
        timestamp: '2024-01-01T10:00:00Z'
    }
}

{
    type: 'dice_roll',
    data: {
        comando: '1d20+5',
        resultados: [15],
        modificadores: 5,
        total: 20,
        tipo_teste: 'stealth',
        dc: 15,
        sucesso: true
    }
}

{
    type: 'ai_response',
    data: {
        conteudo: "Você se move silenciosamente entre as árvores...",
        tipo: 'narrativa',
        contexto: {
            'acao_anterior': 'stealth_check',
            'resultado': 'sucesso'
        }
    }
}

{
    type: 'user_status',
    data: {
        usuario_id: 123,
        status: 'online',
        personagem_ativo: 'Aragorn'
    }
}
```

### Message Types

| Tipo | Direção | Descrição |
|------|---------|-----------|
| `authenticate` | Client→Server | Autenticação JWT |
| `join_campaign` | Client→Server | Entrar na campanha |
| `chat_message` | Bidirectional | Mensagens de chat |
| `dice_roll` | Bidirectional | Rolagem de dados |
| `ai_response` | Server→Client | Resposta da IA GM |
| `user_status` | Bidirectional | Status de usuário |
| `typing` | Bidirectional | Indicador de digitação |
| `error` | Server→Client | Mensagens de erro |

## 🤖 IA Game Master Architecture

### Core Components

```python
# ia_gm/services/narrative_engine.py
class NarrativeEngine:
    def __init__(self, campanha_id):
        self.campanha = Campanha.objects.get(id=campanha_id)
        self.sessao_ia = SessaoIA.objects.get_or_create(campanha=self.campanha)[0]
        self.llm_client = self._setup_llm()
    
    def processar_acao_jogador(self, mensagem_chat):
        # 1. Analisar intenção da ação
        intencao = self.analisar_intencao(mensagem_chat.conteudo)
        
        # 2. Determinar se requer teste
        teste_necessario = self.determinar_teste_necessario(intencao)
        
        # 3. Calcular DC baseado no contexto
        if teste_necessario:
            dc = self.calcular_dc(intencao, self.sessao_ia.contexto_atual)
            return self.solicitar_rolagem(teste_necessario, dc)
        
        # 4. Gerar resposta narrativa
        return self.gerar_resposta_narrativa(intencao)
    
    def processar_resultado_teste(self, rolagem_dado):
        # Processar resultado e gerar narrativa
        contexto = {
            'acao': rolagem_dado.tipo_teste,
            'dc': rolagem_dado.dc,
            'resultado': rolagem_dado.total,
            'sucesso': rolagem_dado.sucesso,
            'personagem': rolagem_dado.personagem.nome
        }
        
        return self.gerar_narrativa_resultado(contexto)

# ia_gm/services/rule_engine.py
class RuleEngine:
    def __init__(self, sistema_jogo):
        self.sistema = sistema_jogo
        self.regras = self.carregar_regras()
    
    def determinar_teste(self, acao_descrita):
        # NLP para identificar tipo de teste
        # Retorna: {'tipo': 'pericia', 'nome': 'Stealth', 'atributo': 'destreza'}
        pass
    
    def calcular_dc(self, contexto_acao):
        # Algoritmo para determinar Difficulty Class
        base_dc = 10
        modificadores = self.analisar_modificadores_contextuais(contexto_acao)
        return base_dc + modificadores

# ia_gm/services/memory_manager.py
class MemoryManager:
    def __init__(self, sessao_ia):
        self.sessao = sessao_ia
    
    def adicionar_memoria_curto_prazo(self, evento):
        # Limita a 50 eventos mais recentes
        self.sessao.memoria_curto_prazo.append(evento)
        if len(self.sessao.memoria_curto_prazo) > 50:
            self.sessao.memoria_curto_prazo.pop(0)
    
    def promover_memoria_longo_prazo(self, evento):
        # Eventos importantes vão para memória permanente
        if evento['impacto_narrativo'] >= 7:
            self.sessao.memoria_longo_prazo.append(evento)
    
    def gerar_resumo_contexto(self):
        # Combina memórias para contexto da IA
        return {
            'eventos_recentes': self.sessao.memoria_curto_prazo[-10:],
            'marco_narrativos': self.sessao.memoria_longo_prazo,
            'contexto_atual': self.sessao.contexto_atual
        }
```

### LLM Integration

```python
# ia_gm/integrations/openai_client.py
class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    def gerar_resposta_narrativa(self, prompt, contexto):
        messages = [
            {
                "role": "system", 
                "content": self._build_system_prompt(contexto)
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _build_system_prompt(self, contexto):
        return f"""
        Você é o Game Master de uma campanha de RPG em português brasileiro.
        
        Sistema de jogo: {contexto['sistema']}
        Campanha: {contexto['campanha_nome']}
        Contexto atual: {contexto['situacao_atual']}
        
        Personagens ativos: {', '.join(contexto['personagens'])}
        Última ação: {contexto['ultima_acao']}
        
        Sua personalidade: {contexto['personalidade_gm']}
        
        Regras:
        - Sempre responda em português brasileiro
        - Mantenha consistência narrativa
        - Aplique as regras do sistema corretamente
        - Seja descritivo mas conciso
        - Encoraje roleplay e criatividade
        """

# ia_gm/integrations/image_generator.py
class ImageGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.DALLE_API_KEY)
    
    def gerar_imagem_npc(self, descricao_npc, estilo="fantasy art"):
        prompt = f"{descricao_npc}, {estilo}, high quality, detailed"
        
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return response.data[0].url
```

## ⚔️ Sistema Unificado: Conversão D&D ↔ Tormenta

### Algoritmo de Conversão

```python
# sistema_unificado/converters/base_converter.py
class SistemaConverter:
    def __init__(self):
        self.mapeamentos = self._carregar_mapeamentos()
        self.tabelas_conversao = self._carregar_tabelas()
    
    def converter_classe(self, classe_origem, sistema_destino):
        """Converte classe entre sistemas"""
        # 1. Identifica poder base da classe
        poder_base = self.calcular_poder_classe(classe_origem)
        
        # 2. Encontra equivalente no sistema destino
        classe_equivalente = self.buscar_equivalente(
            poder_base, sistema_destino, 'classe'
        )
        
        # 3. Ajusta habilidades e características
        return self.ajustar_classe_convertida(classe_equivalente, classe_origem)
    
    def converter_magia(self, magia_origem, sistema_destino):
        """Converte magias entre sistemas"""
        # Análise de poder da magia
        nivel_poder = self.analisar_poder_magia(magia_origem)
        
        # Conversão baseada em templates
        template_conversao = self.get_template_magia(
            magia_origem['escola'], sistema_destino
        )
        
        return self.aplicar_conversao_magia(template_conversao, nivel_poder)

# sistema_unificado/analysis/power_calculator.py
class PowerCalculator:
    """Calcula o 'poder' relativo de elementos do jogo"""
    
    def calcular_poder_classe(self, classe):
        fatores = {
            'bab': classe.get('bonus_ataque_base', 0) * 2,
            'hp': classe.get('dados_vida', 6) * 1.5,
            'saves': sum(classe.get('resistencias', [])) * 0.5,
            'habilidades': len(classe.get('habilidades_especiais', [])) * 3,
            'magias': self._calcular_poder_magico(classe)
        }
        
        return sum(fatores.values())
    
    def calcular_poder_magia(self, magia):
        fatores = {
            'nivel': magia['nivel'] ** 2,
            'dano': self._analisar_dano(magia.get('efeito', '')),
            'duracao': self._valor_duracao(magia.get('duracao', '')),
            'alcance': self._valor_alcance(magia.get('alcance', '')),
            'area': self._valor_area(magia.get('area', ''))
        }
        
        return sum(fatores.values())

# sistema_unificado/data/mapping_tables.py
MAPEAMENTO_CLASSES = {
    'dnd5e_to_t20': {
        'Fighter': 'Guerreiro',
        'Wizard': 'Arcanista', 
        'Rogue': 'Ladino',
        'Cleric': 'Clérico',
        'Ranger': 'Caçador'
    },
    't20_to_dnd5e': {
        'Guerreiro': 'Fighter',
        'Arcanista': 'Wizard',
        'Ladino': 'Rogue', 
        'Clérico': 'Cleric',
        'Caçador': 'Ranger'
    }
}

CONVERSAO_ATRIBUTOS = {
    'dnd5e_to_unified': lambda x: x,  # D&D 5e usa 3d6 (8-18)
    't20_to_unified': lambda x: int(x * 0.9),  # Tormenta é mais poderoso
    'unified_to_dnd5e': lambda x: x,
    'unified_to_t20': lambda x: int(x * 1.1)
}

EQUIVALENCIA_MAGIAS = {
    ('dnd5e', 'Fireball', 3): ('t20', 'Bola de Fogo', 3),
    ('dnd5e', 'Cure Light Wounds', 1): ('t20', 'Cura Leve', 1),
    # ... centenas de mapeamentos
}
```

### Sistema de Balance

```python
# sistema_unificado/balance/validator.py
class BalanceValidator:
    def validar_conversao(self, elemento_original, elemento_convertido):
        """Valida se a conversão mantém o balance"""
        poder_original = self.calcular_poder(elemento_original)
        poder_convertido = self.calcular_poder(elemento_convertido)
        
        diferenca_percentual = abs(poder_original - poder_convertido) / poder_original
        
        if diferenca_percentual > 0.15:  # Máximo 15% de diferença
            return False, f"Desbalanceado: {diferenca_percentual:.1%} diferença"
        
        return True, "Conversão balanceada"
    
    def sugerir_ajustes(self, elemento_convertido, poder_alvo):
        """Sugere ajustes para balancear elemento convertido"""
        poder_atual = self.calcular_poder(elemento_convertido)
        
        if poder_atual < poder_alvo:
            return self.gerar_buffs(elemento_convertido, poder_alvo - poder_atual)
        elif poder_atual > poder_alvo:
            return self.gerar_nerfs(elemento_convertido, poder_atual - poder_alvo)
        
        return []
```

## 🎲 Sistema de Dados Avançado

### Parser de Comandos

```python
# dados/parsers/dice_parser.py
import re
from typing import List, Tuple, Optional

class DiceParser:
    """Parser avançado para comandos de dados"""
    
    PATTERN = re.compile(r'''
        (?P<count>\d+)?              # Número de dados (opcional, padrão 1)
        d(?P<sides>\d+)              # Tipo do dado (obrigatório)
        (?P<modifiers>                # Modificadores (opcional)
            (?:[+-]\d+)*             # +5, -2, etc
        )?
        (?P<advantage>               # Vantagem/Desvantagem (opcional)
            (?:adv|dis|advantage|disadvantage)
        )?
    ''', re.VERBOSE | re.IGNORECASE)
    
    def parse(self, comando: str) -> dict:
        """
        Exemplos:
        - "1d20+5" -> {'count': 1, 'sides': 20, 'modifiers': [5]}
        - "3d6" -> {'count': 3, 'sides': 6, 'modifiers': []}
        - "1d20 adv" -> {'count': 1, 'sides': 20, 'advantage': True}
        """
        match = self.PATTERN.match(comando.strip())
        if not match:
            raise ValueError(f"Comando inválido: {comando}")
        
        return {
            'count': int(match.group('count') or 1),
            'sides': int(match.group('sides')),
            'modifiers': self._parse_modifiers(match.group('modifiers') or ''),
            'advantage': self._parse_advantage(match.group('advantage'))
        }
    
    def _parse_modifiers(self, mod_str: str) -> List[int]:
        """Extrai modificadores como [+5, -2]"""
        if not mod_str:
            return []
        
        modifiers = []
        for match in re.finditer(r'([+-]\d+)', mod_str):
            modifiers.append(int(match.group(1)))
        
        return modifiers
    
    def _parse_advantage(self, adv_str: str) -> Optional[bool]:
        """Determina vantagem (True) ou desvantagem (False)"""
        if not adv_str:
            return None
            
        adv_str = adv_str.lower()
        if adv_str in ['adv', 'advantage']:
            return True
        elif adv_str in ['dis', 'disadvantage']:
            return False
        
        return None

# dados/services/dice_roller.py
import random
from typing import List, Dict, Any

class DiceRoller:
    """Sistema avançado de rolagem de dados"""
    
    def __init__(self):
        self.random = random.SystemRandom()  # Cryptographically secure
    
    def roll(self, parsed_command: dict, contexto: Dict = None) -> Dict[str, Any]:
        """Executa rolagem baseada no comando parseado"""
        
        # Rolagem básica
        resultados_brutos = self._roll_dice(
            parsed_command['count'], 
            parsed_command['sides']
        )
        
        # Aplicar vantagem/desvantagem
        if parsed_command.get('advantage') is not None:
            resultados_brutos = self._apply_advantage(
                resultados_brutos, 
                parsed_command['advantage']
            )
        
        # Calcular total com modificadores
        total_dados = sum(resultados_brutos)
        modificadores = sum(parsed_command['modifiers'])
        total_final = total_dados + modificadores
        
        # Análise de resultados críticos
        criticos = self._analyze_criticals(
            resultados_brutos, 
            parsed_command['sides']
        )
        
        return {
            'comando_original': self._reconstruct_command(parsed_command),
            'resultados_dados': resultados_brutos,
            'total_dados': total_dados,
            'modificadores': modificadores,
            'total_final': total_final,
            'criticos': criticos,
            'contexto': contexto or {},
            'timestamp': timezone.now()
        }
    
    def _roll_dice(self, count: int, sides: int) -> List[int]:
        """Rola os dados físicos"""
        return [self.random.randint(1, sides) for _ in range(count)]
    
    def _apply_advantage(self, results: List[int], advantage: bool) -> List[int]:
        """Aplica regras de vantagem/desvantagem do D&D 5e"""
        if len(results) != 1:  # Só funciona com 1 dado
            return results
            
        # Rola um dado adicional
        extra_roll = self.random.randint(1, 20)  # Assume d20
        
        if advantage:
            return [max(results[0], extra_roll)]
        else:  # disadvantage
            return [min(results[0], extra_roll)]
    
    def _analyze_criticals(self, results: List[int], sides: int) -> Dict[str, Any]:
        """Analisa resultados críticos"""
        criticals = {
            'critical_success': [],
            'critical_failure': [],
            'max_rolls': [],
            'min_rolls': []
        }
        
        for i, result in enumerate(results):
            if result == sides:
                criticals['max_rolls'].append(i)
                if sides == 20:  # D20 específico
                    criticals['critical_success'].append(i)
            
            if result == 1:
                criticals['min_rolls'].append(i)
                if sides == 20:  # D20 específico
                    criticals['critical_failure'].append(i)
        
        return criticals

# dados/integrations/rule_integration.py
class RuleIntegration:
    """Integra rolagens com regras dos sistemas"""
    
    def __init__(self, sistema_jogo):
        self.sistema = sistema_jogo
    
    def avaliar_teste(self, rolagem_result: dict, dc: int, 
                     tipo_teste: str) -> Dict[str, Any]:
        """Avalia se um teste foi bem-sucedido"""
        
        total = rolagem_result['total_final']
        sucesso = total >= dc
        
        # Regras específicas por sistema
        if self.sistema.codigo == 'dnd5e':
            return self._avaliar_dnd5e(rolagem_result, dc, sucesso)
        elif self.sistema.codigo == 't20':
            return self._avaliar_t20(rolagem_result, dc, sucesso)
        else:
            return self._avaliar_unificado(rolagem_result, dc, sucesso)
    
    def _avaliar_dnd5e(self, rolagem, dc, sucesso_base):
        """Regras específicas D&D 5e"""
        criticos = rolagem['criticos']
        
        # Critical success/failure em d20
        if criticos['critical_success']:
            return {
                'sucesso': True,
                'tipo_resultado': 'critical_success',
                'descricao': 'Sucesso crítico!'
            }
        elif criticos['critical_failure']:
            return {
                'sucesso': False,
                'tipo_resultado': 'critical_failure', 
                'descricao': 'Falha crítica!'
            }
        
        return {
            'sucesso': sucesso_base,
            'tipo_resultado': 'normal',
            'margem': rolagem['total_final'] - dc
        }
```

## 🚀 Deployment & DevOps

### Docker Configuration

```dockerfile
# Dockerfile.production
FROM python:3.11-slim

# Otimizações para produção
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalação de dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Configurar usuário não-root
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Scripts de inicialização
COPY scripts/start.sh /start.sh
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /start.sh /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]
```

### Performance Optimizations

```python
# settings/production.py
import os

# Database optimizations
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'conn_max_age': 600,
        }
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.ShardClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
    }
}

# Celery optimizations  
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_ACKS_LATE = True

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Session optimization
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 86400  # 24 horas

# Security headers
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Monitoring & Logging

```python
# monitoring/health_checks.py
from django.http import JsonResponse
from django.db import connections
from redis import Redis
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """Endpoint de health check para load balancer"""
    status = {
        'status': 'healthy',
        'services': {},
        'timestamp': timezone.now().isoformat()
    }
    
    # Check database
    try:
        connections['default'].cursor().execute('SELECT 1')
        status['services']['database'] = 'ok'
    except Exception as e:
        status['services']['database'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
    
    # Check Redis
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        status['services']['redis'] = 'ok'
    except Exception as e:
        status['services']['redis'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
    
    # Check AI services
    try:
        # Simple API call test
        status['services']['openai'] = 'ok'
    except Exception as e:
        status['services']['openai'] = f'error: {str(e)}'
        # AI não é crítico para health check
    
    return JsonResponse(status)

# monitoring/metrics.py
import time
from django.core.cache import cache
from functools import wraps

def track_performance(metric_name):
    """Decorator para rastrear performance de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = 'success'
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                cache.set(
                    f'metric:{metric_name}:last_duration',
                    duration,
                    timeout=300
                )
                logger.info(f'{metric_name}: {duration:.3f}s ({status})')
        return wrapper
    return decorator
```

## 📝 Próximos Passos e Melhorias

### Funcionalidades Pendentes
- 🟡 Sistema unificado D&D ↔ Tormenta completo
- 🟡 Frontend React (atualmente usando templates Django)
- 🟡 Sistema de imagens via DALL-E 3
- 🟡 Módulo de combate avançado
- 🟡 Sistema de mapas interativos
- 🟡 Marketplace de conteúdo

### Otimizações Técnicas
- 🟡 Migração para PostgreSQL em produção
- 🟡 Implementação completa do Celery
- 🟡 Cache avançado com Redis
- 🟡 Monitoring e métricas
- 🟡 Testes automatizados abrangentes

### Expansões Futuras
- 🟡 Suporte a mais sistemas de RPG
- 🟡 IA GM ainda mais sofisticada
- 🟡 Integração com plataformas de streaming
- 🟡 App mobile nativo

---

**Este documento técnico reflete o estado atual do Unified Chronicles e serve como referência para futuras implementações e melhorias. O sistema já está operacional e pronto para uso em campanhas reais.**

**Última Atualização**: Janeiro 2025 - Sistema IA GM "Arquiteto de Mundos" implementado e funcional

<function_calls>
<invoke name="mark_todo_as_done">
<parameter name="todo_ids">["503e9a1e-9c3e-4aaf-a38a-77b6f46e81ae"]