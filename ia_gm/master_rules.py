"""
Sistema de Regras Comportamentais do Mestre IA - Arquiteto de Mundos
Implementa os modos de operação, ciclo de jogo e regras de comportamento
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .models import SessaoIA


class ModoOperacao(Enum):
    """Modos de operação do Mestre IA"""
    CONFIGURACAO = "configuracao"  # Sessão Inativa - aceita comandos de barra
    JOGO = "jogo"                  # Sessão Ativa - modo narrativo completo


class FaseCicloJogo(Enum):
    """Fases do ciclo de jogo obrigatório"""
    DESCREVENDO_SITUACAO = "descrevendo_situacao"   # Mestre descreve e pergunta
    AGUARDANDO_TODAS_ACOES = "aguardando_acoes"     # Esperando TODOS os jogadores
    PROCESSANDO_CONSEQUENCIAS = "processando"        # Resolvendo e narrando


@dataclass
class RegraComportamental:
    """Define uma regra comportamental específica"""
    nome: str
    descricao: str
    modo_aplicacao: ModoOperacao
    obrigatoria: bool = True


class MasterRulesEngine:
    """
    Engine que governa o comportamento do Mestre IA
    Implementa as regras fundamentais de persona e fluxo de jogo
    """
    
    # Regras fundamentais invioláveis
    REGRAS_FUNDAMENTAIS = [
        RegraComportamental(
            nome="IDENTIDADE_MESTRE",
            descricao="Eu sou o Mestre. NUNCA chamo jogador de 'Mestre'. Dirijo-me aos jogadores pelos nomes dos personagens.",
            modo_aplicacao=ModoOperacao.JOGO,
            obrigatoria=True
        ),
        RegraComportamental(
            nome="CICLO_OBRIGATORIO",
            descricao="DEVO seguir: 1) Descrever situação + pergunta, 2) Aguardar TODAS as ações, 3) Resolver e narrar",
            modo_aplicacao=ModoOperacao.JOGO,
            obrigatoria=True
        ),
        RegraComportamental(
            nome="FILOSOFIA_SIM_E",
            descricao="Abordagem padrão é 'Sim, e...' para ações criativas. Nunca bloquear sem alternativa interessante.",
            modo_aplicacao=ModoOperacao.JOGO,
            obrigatoria=True
        ),
        RegraComportamental(
            nome="NARRACAO_CONCRETA",
            descricao="Narrar consequências diretas e sensoriais. PROIBIDO usar meta-linguagem como 'o destino aguarda' ou 'a situação evolui'. Foco nos 5 sentidos e em ações concretas.",
            modo_aplicacao=ModoOperacao.JOGO,
            obrigatoria=True
        ),
        RegraComportamental(
            nome="NPCS_COM_ALMA",
            descricao="NPCs são pessoas, não robôs. Cada um tem personalidade, motivações, falhas e voz única.",
            modo_aplicacao=ModoOperacao.JOGO,
            obrigatoria=True
        ),
        RegraComportamental(
            nome="DIALOGO_ESTRUTURADO",
            descricao="Diálogos devem seguir: [Nome] [Ação/Expressão] \"Fala\" (Tom/Maneirismo)",
            modo_aplicacao=ModoOperacao.JOGO,
            obrigatoria=True
        ),
        RegraComportamental(
            nome="VISUALIZACAO_DINAMICA", 
            descricao="Descrever primeiro, gerar imagem apenas se solicitado explicitamente",
            modo_aplicacao=ModoOperacao.JOGO,
            obrigatoria=True
        ),
        RegraComportamental(
            nome="COMANDO_BARRA_CONFIGURACAO",
            descricao="Em modo configuração, aceitar comandos /ambiente, /npc, etc. Posso chamar admin de 'Mestre'.",
            modo_aplicacao=ModoOperacao.CONFIGURACAO,
            obrigatoria=True
        )
    ]
    
    @classmethod
    def obter_regras_para_modo(cls, modo: ModoOperacao) -> List[RegraComportamental]:
        """Obtém regras aplicáveis para um modo específico"""
        return [regra for regra in cls.REGRAS_FUNDAMENTAIS 
                if regra.modo_aplicacao == modo or not hasattr(regra, 'modo_aplicacao')]
    
    @classmethod
    def gerar_prompt_comportamental(cls, modo: ModoOperacao, contexto_adicional: str = "") -> str:
        """Gera prompt com regras comportamentais para o modo especificado"""
        regras_aplicaveis = cls.obter_regras_para_modo(modo)
        
        if modo == ModoOperacao.CONFIGURACAO:
            prompt_modo = """
### MODO DE CONFIGURAÇÃO ATIVO ###

COMPORTAMENTO ATUAL:
- Você é uma ferramenta de assistência para o administrador da sessão
- PODE se dirigir ao administrador como "Mestre" ou "Admin" (ele está criando a sessão)
- Aceita e responde a comandos de barra: /ambiente, /npc, /missao, /item, etc.
- Seja eficiente e direto na preparação do cenário
- NÃO entre em modo narrativo - seja prático e útil

COMANDOS DISPONÍVEIS:
/ambiente [descrição] - Criar descrição de ambiente
/npc [nome] [características] - Criar NPC detalhado  
/missao [tipo] [detalhes] - Criar missão/quest
/item [nome] [descrição] - Criar item especial
/evento [tipo] - Criar evento/acontecimento
/dialogo [npc] [situação] - Gerar diálogo específico
"""
        else:  # MODO JOGO
            prompt_modo = """
### MODO DE JOGO ATIVO ###

COMPORTAMENTO OBRIGATÓRIO:
- Você assumiu a persona narrativa completa do MESTRE DO JOGO
- PARE de aceitar comandos de configuração
- Siga rigorosamente o CICLO DE JOGO em cada turno:

** CICLO OBRIGATÓRIO **:
1️⃣ DESCREVER: Inicie com descrição vívida + "O que vocês fazem?"
2️⃣ AGUARDAR: Entre em estado de espera até TODOS os jogadores declararem ações
3️⃣ RESOLVER: Processe todas as ações juntas, narre consequências

REGRAS INVIOLÁVEIS:
- JAMAIS continue a narrativa até receber TODAS as ações dos jogadores ativos
- Confirme cada ação individualmente: "Entendido, [Nome do Personagem]. Aguardando os outros."
- Após receber todas: processe tudo em UMA resposta coesa
- Use ordem de iniciativa em combate ou lógica narrativa fora dele

TRATAMENTO DE PERSONAGENS:
- Dirija-se SEMPRE pelos nomes dos personagens, nunca "Mestre"
- Se alguém tentar me chamar de subordinado, reafirme educadamente: "Eu sou o Mestre desta sessão"
"""
        
        # Adiciona regras específicas
        detalhes_regras = "\n".join([
            f"• {regra.nome}: {regra.descricao}" 
            for regra in regras_aplicaveis if regra.obrigatoria
        ])
        
        prompt_completo = f"""
{prompt_modo}

REGRAS ESPECÍFICAS DESTE MODO:
{detalhes_regras}

{contexto_adicional}

LEMBRE-SE: Estas regras são OBRIGATÓRIAS e devem ser seguidas rigorosamente.
"""
        return prompt_completo
    
    @classmethod  
    def validar_entrada_comando(cls, entrada: str, modo: ModoOperacao) -> Dict[str, Any]:
        """Valida se uma entrada está adequada ao modo atual"""
        entrada_normalizada = entrada.strip().lower()
        
        if modo == ModoOperacao.CONFIGURACAO:
            # Em configuração, comandos de barra são válidos
            if entrada_normalizada.startswith('/'):
                return {
                    "valida": True,
                    "tipo": "comando_configuracao",
                    "comando": entrada_normalizada.split()[0][1:],  # Remove /
                    "parametros": entrada[len(entrada_normalizada.split()[0]):].strip()
                }
            else:
                return {
                    "valida": True, 
                    "tipo": "pergunta_configuracao",
                    "conteudo": entrada
                }
        
        elif modo == ModoOperacao.JOGO:
            # Em jogo, comandos de barra não devem ser aceitos
            if entrada_normalizada.startswith('/'):
                return {
                    "valida": False,
                    "erro": "Comandos de configuração não são aceitos durante o jogo",
                    "sugestao": "Para configurar elementos, pause a sessão primeiro"
                }
            else:
                return {
                    "valida": True,
                    "tipo": "acao_jogador", 
                    "conteudo": entrada
                }
        
        return {"valida": False, "erro": "Modo não reconhecido"}
    
    @classmethod
    def gerar_resposta_erro_modo(cls, entrada: str, modo_atual: ModoOperacao) -> str:
        """Gera resposta apropriada quando entrada não é válida para o modo"""
        if modo_atual == ModoOperacao.JOGO and entrada.strip().startswith('/'):
            return """
🎭 **MODO DE JOGO ATIVO** 

Comandos de configuração não são aceitos durante a sessão de jogo. 

Para adicionar elementos ao jogo:
- Use ações narrativas dos personagens
- Ou pause a sessão para voltar ao modo configuração

**Aguardando as ações dos personagens para continuar a história...**
"""
        elif modo_atual == ModoOperacao.CONFIGURACAO:
            return """
🔧 **MODO DE CONFIGURAÇÃO ATIVO**

Para configurar elementos da sessão, use comandos:
- `/ambiente [descrição]` - Criar ambiente
- `/npc [nome]` - Criar NPC  
- `/missao [tipo]` - Criar missão
- `/item [nome]` - Criar item

Ou faça perguntas sobre preparação da sessão.
"""
        
        return "Entrada não reconhecida para o modo atual."


class CicloJogoValidator:
    """Valida se o ciclo de jogo está sendo seguido corretamente"""
    
    @staticmethod
    def validar_fase_atual(fase_esperada: FaseCicloJogo, ultima_resposta: str, acoes_pendentes: List[str]) -> Dict[str, Any]:
        """Valida se estamos na fase correta do ciclo"""
        
        if fase_esperada == FaseCicloJogo.DESCREVENDO_SITUACAO:
            # Deve terminar com pergunta
            termina_com_pergunta = (
                "o que vocês fazem" in ultima_resposta.lower() or
                "como vocês reagem" in ultima_resposta.lower() or
                ultima_resposta.endswith("?")
            )
            
            return {
                "valida": termina_com_pergunta,
                "feedback": "Descrição deve terminar perguntando o que os personagens fazem" if not termina_com_pergunta else "OK"
            }
        
        elif fase_esperada == FaseCicloJogo.AGUARDANDO_TODAS_ACOES:
            # Deve haver ações pendentes
            tem_pendencias = len(acoes_pendentes) > 0
            
            return {
                "valida": tem_pendencias,
                "pendentes": acoes_pendentes,
                "feedback": f"Aguardando ações de: {', '.join(acoes_pendentes)}" if tem_pendencias else "Todas as ações recebidas - deve processar"
            }
        
        elif fase_esperada == FaseCicloJogo.PROCESSANDO_CONSEQUENCIAS:
            # Deve processar todas as ações
            return {
                "valida": len(acoes_pendentes) == 0,
                "feedback": "Deve processar todas as ações antes de continuar" if acoes_pendentes else "OK para processar"
            }
        
        return {"valida": False, "feedback": "Fase não reconhecida"}


# Integração para compatibilidade com sistema existente
def obter_modo_operacao_sessao(sessao: SessaoIA) -> ModoOperacao:
    """Determina o modo de operação atual de uma sessão"""
    if not sessao.ativa:
        return ModoOperacao.CONFIGURACAO
    
    # Verifica se há estado de jogo ativo no cache
    from django.core.cache import cache
    estado_cache = cache.get(f"game_session_{sessao.id}_estado")
    
    if estado_cache == "ativa":
        return ModoOperacao.JOGO
    else:
        return ModoOperacao.CONFIGURACAO


def aplicar_regras_ao_prompt(prompt_base: str, sessao: SessaoIA, contexto_adicional: str = "") -> str:
    """Aplica as regras comportamentais ao prompt base"""
    modo_atual = obter_modo_operacao_sessao(sessao)
    prompt_comportamental = MasterRulesEngine.gerar_prompt_comportamental(modo_atual, contexto_adicional)
    
    return f"""
{prompt_base}

{prompt_comportamental}

=== CONTEXTO ADICIONAL ===
{contexto_adicional}
"""