"""
Sistema de Gerenciamento de Sessão de Jogo - Arquiteto de Mundos
Implementa o comportamento de Mestre IA durante sessões ativas
"""

import json
import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import timezone, datetime

from django.core.cache import cache
from django.db import models

from .models import SessaoIA, InteracaoIA, NPCGerado
from personagens.models import Personagem
from .master_rules import (
    MasterRulesEngine, ModoOperacao, FaseCicloJogo, 
    CicloJogoValidator, obter_modo_operacao_sessao, aplicar_regras_ao_prompt
)

logger = logging.getLogger(__name__)


class EstadoSessao(Enum):
    """Estados possíveis de uma sessão"""
    CONFIGURACAO = "configuracao"
    ATIVA = "ativa"
    PAUSADA = "pausada"
    ENCERRADA = "encerrada"


class FaseJogo(Enum):
    """Fases do ciclo de jogo"""
    DESCREVENDO_SITUACAO = "descrevendo_situacao"
    AGUARDANDO_ACOES = "aguardando_acoes"
    PROCESSANDO_TURNO = "processando_turno"


@dataclass
class AcaoJogador:
    """Representa uma ação declarada por um jogador"""
    personagem_nome: str
    usuario_id: int
    acao: str
    timestamp: datetime
    processada: bool = False


@dataclass
class EstadoTurno:
    """Estado atual do turno de jogo"""
    numero_turno: int
    fase: FaseJogo
    descricao_situacao: str
    acoes_recebidas: List[AcaoJogador]
    personagens_esperados: List[str]
    aguardando_personagens: List[str]
    narrativa_resultado: Optional[str] = None


class GameSessionManager:
    """Gerenciador principal do modo de jogo"""
    
    def __init__(self, sessao: SessaoIA):
        self.sessao = sessao
        self.cache_key_estado = f"game_session_{sessao.id}_estado"
        self.cache_key_turno = f"game_session_{sessao.id}_turno"
        self.cache_timeout = 3600  # 1 hora
    
    @property
    def estado_sessao(self) -> EstadoSessao:
        """Obtém o estado atual da sessão"""
        if not self.sessao.ativa:
            return EstadoSessao.ENCERRADA
        
        estado_cache = cache.get(self.cache_key_estado)
        if estado_cache:
            return EstadoSessao(estado_cache)
        
        # Se não há cache, assume que é configuração
        return EstadoSessao.CONFIGURACAO
    
    def ativar_modo_jogo(self) -> Dict[str, Any]:
        """Ativa o modo de jogo e inicia primeira situação"""
        # Marca sessão como ativa no cache
        cache.set(self.cache_key_estado, EstadoSessao.ATIVA.value, self.cache_timeout)
        
        # Obtém personagens da campanha
        personagens = self._obter_personagens_ativos()
        
        # Cria primeiro turno
        estado_turno = EstadoTurno(
            numero_turno=1,
            fase=FaseJogo.DESCREVENDO_SITUACAO,
            descricao_situacao="",
            acoes_recebidas=[],
            personagens_esperados=[p.nome for p in personagens],
            aguardando_personagens=[]
        )
        
        # Salva no cache
        cache.set(self.cache_key_turno, estado_turno.__dict__, self.cache_timeout)
        
        # Gera primeira descrição de situação
        primeira_situacao = self._gerar_situacao_inicial()
        
        return {
            "modo": "jogo_ativo",
            "turno": 1,
            "fase": "descrevendo_situacao",
            "personagens": [p.nome for p in personagens],
            "situacao": primeira_situacao,
            "mensagem_sistema": "🎲 **MODO DE JOGO ATIVADO** - Eu agora sou o Mestre da sessão!"
        }
    
    def processar_entrada_jogador(self, entrada: str, usuario_id: int) -> Dict[str, Any]:
        """Processa entrada de um jogador no modo de jogo"""
        if self.estado_sessao != EstadoSessao.ATIVA:
            return {"erro": "Sessão não está ativa"}
        
        estado_turno = self._obter_estado_turno()
        if not estado_turno:
            return {"erro": "Erro ao obter estado do turno"}
        
        # Identifica o personagem do jogador
        personagem = self._obter_personagem_do_usuario(usuario_id)
        if not personagem:
            return {"erro": "Personagem não encontrado para este usuário"}
        
        if estado_turno.fase == FaseJogo.AGUARDANDO_ACOES:
            return self._processar_acao_jogador(entrada, personagem, estado_turno)
        else:
            return {"mensagem": f"Aguardando sua ação, {personagem.nome}!"}
    
    def iniciar_aguardo_acoes(self, situacao: str) -> Dict[str, Any]:
        """Inicia a fase de aguardo de ações dos jogadores"""
        estado_turno = self._obter_estado_turno()
        if not estado_turno:
            return {"erro": "Erro ao obter estado do turno"}
        
        # Atualiza estado
        estado_turno.fase = FaseJogo.AGUARDANDO_ACOES
        estado_turno.descricao_situacao = situacao
        estado_turno.aguardando_personagens = estado_turno.personagens_esperados.copy()
        estado_turno.acoes_recebidas = []
        
        # Salva no cache
        cache.set(self.cache_key_turno, estado_turno.__dict__, self.cache_timeout)
        
        personagens_str = ", ".join(estado_turno.personagens_esperados)
        
        return {
            "fase": "aguardando_acoes",
            "situacao": situacao,
            "personagens_aguardando": estado_turno.aguardando_personagens,
            "mensagem_chamada": f"**{personagens_str}**, o que vocês fazem?",
            "instrucoes": "Aguardando as ações de todos os personagens antes de continuar..."
        }
    
    def _processar_acao_jogador(self, acao: str, personagem: Personagem, estado_turno: EstadoTurno) -> Dict[str, Any]:
        """Processa a ação de um jogador específico"""
        nome_personagem = personagem.nome
        
        # Verifica se já declarou ação neste turno
        for acao_existente in estado_turno.acoes_recebidas:
            if acao_existente.personagem_nome == nome_personagem:
                return {
                    "mensagem": f"**{nome_personagem}** já declarou sua ação neste turno.",
                    "acao_anterior": acao_existente.acao
                }
        
        # Verifica se este personagem estava sendo esperado
        if nome_personagem not in estado_turno.aguardando_personagens:
            return {"mensagem": f"**{nome_personagem}** não precisa declarar ação neste momento."}
        
        # Registra a ação
        nova_acao = AcaoJogador(
            personagem_nome=nome_personagem,
            usuario_id=personagem.usuario.id,
            acao=acao,
            timestamp=datetime.now(timezone.utc)
        )
        
        estado_turno.acoes_recebidas.append(nova_acao.__dict__)
        estado_turno.aguardando_personagens.remove(nome_personagem)
        
        # Atualiza cache
        cache.set(self.cache_key_turno, estado_turno.__dict__, self.cache_timeout)
        
        # Registra interação
        self._registrar_interacao_jogador(personagem, acao)
        
        # Verifica se todos já declararam
        if len(estado_turno.aguardando_personagens) == 0:
            return self._processar_turno_completo(estado_turno)
        else:
            aguardando_str = ", ".join(estado_turno.aguardando_personagens)
            return {
                "acao_confirmada": f"**{nome_personagem}**: {acao}",
                "aguardando": aguardando_str,
                "mensagem": f"Ação de **{nome_personagem}** registrada! Aguardando: **{aguardando_str}**"
            }
    
    def _processar_turno_completo(self, estado_turno: EstadoTurno) -> Dict[str, Any]:
        """Processa o turno quando todas as ações foram recebidas"""
        # Valida ciclo de jogo antes de processar
        validacao = CicloJogoValidator.validar_fase_atual(
            FaseCicloJogo.PROCESSANDO_CONSEQUENCIAS, 
            "", 
            estado_turno.aguardando_personagens
        )
        
        if not validacao['valida']:
            logger.warning(f"Violação do ciclo de jogo: {validacao['feedback']}")
        
        estado_turno.fase = FaseJogo.PROCESSANDO_TURNO
        cache.set(self.cache_key_turno, estado_turno.__dict__, self.cache_timeout)
        
        # Gera narrativa das consequências
        narrativa = self._gerar_narrativa_consequencias(estado_turno)
        
        # Gera nova situação para o próximo turno
        proximo_numero_turno = estado_turno.numero_turno + 1
        nova_situacao = self.gerar_nova_situacao(proximo_numero_turno)
        
        # Prepara próximo turno com a nova situação
        novo_estado = EstadoTurno(
            numero_turno=proximo_numero_turno,
            fase=FaseJogo.AGUARDANDO_ACOES,  # Já começa aguardando ações
            descricao_situacao=nova_situacao['situacao'],
            acoes_recebidas=[],
            personagens_esperados=estado_turno.personagens_esperados,
            aguardando_personagens=estado_turno.personagens_esperados.copy()
        )
        
        cache.set(self.cache_key_turno, novo_estado.__dict__, self.cache_timeout)
        
        return {
            "turno_processado": True,
            "numero_turno": estado_turno.numero_turno,
            "acoes_processadas": [
                f"**{acao['personagem_nome']}**: {acao['acao']}" 
                for acao in estado_turno.acoes_recebidas
            ],
            "narrativa_resultado": narrativa,
            "proximo_turno": novo_estado.numero_turno,
            "nova_situacao": nova_situacao,
            "mensagem": "✅ **Turno processado!** Todas as ações foram resolvidas."
        }
    
    def _gerar_situacao_inicial(self) -> str:
        """Gera a primeira descrição de situação da sessão - VERSÃO OTIMIZADA"""
        personagens = self._obter_personagens_ativos()
        personagens_nomes = [p.nome for p in personagens]
        personagens_str = ", ".join(personagens_nomes)
        
        # OTIMIZAÇÃO: Usa fallback inteligente imediatamente para melhor UX
        # Em produção, pode-se configurar para tentar IA com timeout curto
        
        logger.info("Gerando situação inicial otimizada (fallback inteligente)")
        
        # Coleta contexto básico da campanha
        nome_campanha = self.sessao.campanha.nome
        descricao_campanha = self.sessao.campanha.descricao or ""
        nome_sessao = self.sessao.nome
        descricao_sessao = self.sessao.descricao or ""
        
        # Verifica sessões anteriores para contexto
        sessoes_anteriores = SessaoIA.objects.filter(
            campanha=self.sessao.campanha
        ).exclude(id=self.sessao.id).order_by('-data_criacao')[:2]
        
        tem_historico = sessoes_anteriores.exists()
        
        # Gera situação contextualizada sem IA externa
        situacao = self._gerar_situacao_inteligente(
            personagens_str, nome_campanha, descricao_campanha,
            nome_sessao, descricao_sessao, tem_historico
        )
        
        # Registra como interação rápida
        InteracaoIA.objects.create(
            sessao=self.sessao,
            usuario=self.sessao.campanha.organizador,
            tipo_interacao='SITUACAO_INICIAL',
            prompt_usuario='Geração de situação inicial otimizada',
            resposta_ia=situacao[:2000],
            tokens_usados=0,
            contexto={
                'modo': 'jogo_ativo', 
                'tipo': 'situacao_inicial_otimizada',
                'personagens_count': len(personagens),
                'tem_historico': tem_historico
            }
        )
        
        return situacao
    
    def _gerar_situacao_inteligente(self, personagens_str: str, nome_campanha: str, 
                                    descricao_campanha: str, nome_sessao: str, 
                                    descricao_sessao: str, tem_historico: bool) -> str:
        """Gera situação inicial inteligente sem IA externa - OTIMIZADA"""
        import random
        
        # Lista de aberturas envolventes baseadas no estilo da sessão
        aberturas = [
            f"🏰 **Bem-vindos à {nome_sessao}!**\n\nHeróis de **{nome_campanha}**, uma nova aventura os aguarda...",
            f"⚙️ **{nome_sessao}** - Capítulo {'Novo' if not tem_historico else 'Seguinte'} em **{nome_campanha}**\n\nBravos aventureiros, o destino os convoca...",
            f"🎆 A história de **{nome_campanha}** continua em **{nome_sessao}**\n\n{personagens_str}, vossa jornada épica prossegue..."
        ]
        
        # Ganchos narrativos variados
        ganchos = [
            "Uma estranha névoa dourada se dissipa à vossa frente, revelando um caminho antes oculto.",
            "O som de cascos se aproxima pela estrada empoeirada - alguém vem em vossa direção.",
            "Uma carta lacrada com selo real chegou durante a madrugada. O conteúdo pode mudar tudo.",
            "Rumores de uma descoberta antiga ecoam pela taverna onde descansais.",
            "O céu se escurece repentinamente, e uma sombra gigantesca cruza sobre vossas cabeças.",
            "Uma música melancólica ecoa das profundezas da floresta próxima."
        ]
        
        # Elementos ambientais imersivos
        ambientes = [
            "O ar carrega o aroma de chuva recente misturado com especiarias exóticas.",
            "Uma brisa gelada faz as folhas sussurrarem segredos ancestrais.",
            "O sol poente pinta o horizonte com tons dourados e carmesim.",
            "Tochas crepitam nas paredes, criando sombras dançantes ao vosso redor.",
            "O som distante de água corrente promete descanso e renovação."
        ]
        
        # Seleciona elementos aleatórios para variedade
        abertura = random.choice(aberturas)
        gancho = random.choice(ganchos)
        ambiente = random.choice(ambientes)
        
        # Incorpora descrição da sessão se disponível
        contexto_sessao = ""
        if descricao_sessao:
            contexto_sessao = f"\n\n📜 **Contexto da Sessão:**\n{descricao_sessao}\n"
        
        # Adiciona contexto da campanha se disponível
        contexto_campanha = ""
        if descricao_campanha and len(descricao_campanha) > 20:
            contexto_reducido = descricao_campanha[:150] + "..." if len(descricao_campanha) > 150 else descricao_campanha
            contexto_campanha = f"\n🌍 **Mundo de {nome_campanha}:**\n{contexto_reducido}\n"
        
        # Constrói a situação final
        situacao = f"""{abertura}
{contexto_campanha}{contexto_sessao}
🎭 **A Aventura Começa:**
**{personagens_str}**, vocês se encontram em um momento decisivo. {ambiente}

{gancho}

Um momento de expectativa paira no ar. As possibilidades se estendem diante de vocês como caminhos em uma encruzilhada do destino.

{'🎯 **Continuando vossa jornada épica...**' if tem_historico else '✨ **Iniciando vossa lenda...**'}

**O que vocês fazem?**"""
        
        return situacao
    
    def _gerar_situacao_fallback(self, personagens_str: str) -> str:
        """Gera uma situação inicial de fallback simples (método legado)"""
        # Obtém algumas informações básicas da campanha para personalizar
        nome_campanha = self.sessao.campanha.nome
        descricao_campanha = self.sessao.campanha.descricao
        
        # Usa informações da sessão se disponível
        nome_sessao = self.sessao.nome
        descricao_sessao = self.sessao.descricao
        
        situacao = f"""🏰 **{nome_sessao}** - Sessão iniciada no mundo de **{nome_campanha}**!

**{personagens_str}**, vocês se encontram no início de uma nova aventura. 

{descricao_sessao if descricao_sessao else 'A situação se desenrola diante de vocês...'}

{descricao_campanha[:200] + '...' if len(descricao_campanha or '') > 200 else descricao_campanha or 'O mundo aguarda suas ações.'}

Com expectativas e curiosidade no ar, é hora de decidir como proceder nesta jornada.

O que vocês fazem?"""
        
        return situacao
    
    def _gerar_narrativa_consequencias(self, estado_turno: EstadoTurno) -> str:
        """Gera a narrativa das consequências das ações usando IA"""
        # Prepara as ações dos jogadores para o contexto
        acoes_detalhadas = []
        for acao_dict in estado_turno.acoes_recebidas:
            nome = acao_dict['personagem_nome']
            acao = acao_dict['acao']
            acoes_detalhadas.append(f"**{nome}**: {acao}")
        
        acoes_texto = "\n".join(acoes_detalhadas)
        
        # Obtém contexto da situação atual
        situacao_anterior = estado_turno.descricao_situacao
        
        # OTIMIZAÇÃO: Usa narrativa inteligente imediata para melhor UX
        logger.info(f"Gerando narrativa de consequências otimizada para turno {estado_turno.numero_turno}")
        
        # Gera narrativa contextualizada sem IA externa
        narrativa = self._gerar_narrativa_inteligente(estado_turno, acoes_detalhadas, situacao_anterior)
        
        # Registra a geração como interação rápida
        InteracaoIA.objects.create(
            sessao=self.sessao,
            usuario=self.sessao.campanha.organizador,
            tipo_interacao='NARRATIVA_CONSEQUENCIAS',
            prompt_usuario=f'Consequências do Turno {estado_turno.numero_turno} (Otimizada)',
            resposta_ia=narrativa[:2000],
            tokens_usados=0,
            contexto={
                'turno': estado_turno.numero_turno,
                'num_acoes': len(estado_turno.acoes_recebidas),
                'tipo': 'narrativa_otimizada'
            }
        )
        
        return narrativa
    
    def _gerar_narrativa_inteligente(self, estado_turno: EstadoTurno, acoes_detalhadas: list, situacao_anterior: str) -> str:
        """Gera narrativa de consequências inteligente sem IA externa - OTIMIZADA"""
        import random
        
        # Templates de transição narrativa
        transicoes = [
            "Com determinação e coragem, os heróis agem:",
            "O destino responde às escolhas dos aventureiros:",
            "As ações dos personagens ecoam pelo mundo:",
            "A aventura se desenrola conforme os heróis decidem:",
            "O mundo reage às decisões dos protagonistas:"
        ]
        
        # Consequencias narrativas variadas
        consequencias = [
            "Os eventos se alinham de forma inesperada, revelando novas possibilidades.",
            "Uma cadeia de acontecimentos é desencadeada pelas ações tomadas.",
            "O ambiente ao redor responde de maneira surpreendente às escolhas feitas.",
            "As consequências das decisões começam a se manifestar no mundo.",
            "Novos caminhos se abrem enquanto outros se fecham para sempre."
        ]
        
        # Elementos de continuidade
        continuidades = [
            "A jornada continua com novas questões surgindo no horizonte.",
            "Novos desafios e oportunidades aguardam os heróis adiante.",
            "O próximo capítulo desta épica aventura está prestes a começar.",
            "A história se aprofunda com cada decisão corajosa tomada.",
            "O mundo continua a evoluir em resposta às ações heróicas."
        ]
        
        # Seleciona elementos aleatórios
        transicao = random.choice(transicoes)
        consequencia = random.choice(consequencias)
        continuidade = random.choice(continuidades)
        
        # Constrói a narrativa
        acoes_formatadas = "\n".join([f"  • {acao}" for acao in acoes_detalhadas])
        
        narrativa = f"""🎭 **Turno {estado_turno.numero_turno} - Resolvendo Ações dos Heróis**

{transicao}

{acoes_formatadas}

⚔️ **Consequências:**
{consequencia}

Com base nas escolhas dos personagens, a situação evolui naturalmente. {continuidade}

✨ As decisões tomadas pelos heróis ecoam pelo tecido da realidade, moldando o destino que os aguarda...

📜 *Preparando nova situação...*"""
        
        return narrativa
    
    def _gerar_narrativa_fallback(self, estado_turno: EstadoTurno, acoes_detalhadas: list) -> str:
        """Gera uma narrativa de fallback simples (método legado)"""
        narrativa_fallback = f"""🎭 **Turno {estado_turno.numero_turno} - Resolvendo Ações:**

{chr(10).join(acoes_detalhadas)}

**Resultado**: As ações dos personagens se desenrolam de forma coordenada. O mundo responde às suas escolhas, criando novas possibilidades e revelando consequências interessantes.

A narrativa se desenvolve naturalmente a partir das decisões tomadas pelos heróis, e a aventura continua com novos desafios e oportunidades surgindo no horizonte...

🎯 *Aguardando próxima situação...*"""
        
        return narrativa_fallback
    
    def gerar_nova_situacao(self, turno_numero: int) -> Dict[str, Any]:
        """Gera nova situação após processar um turno"""
        personagens = self._obter_personagens_ativos()
        personagens_nomes = [p.nome for p in personagens]
        personagens_str = ", ".join(personagens_nomes)
        
        # Obtém últimas interações para contexto
        interacoes_recentes = InteracaoIA.objects.filter(
            sessao=self.sessao
        ).order_by('-data_interacao')[:5]
        
        contexto_recente = ""
        if interacoes_recentes.exists():
            contexto_recente = "\n".join([
                f"- {i.tipo_interacao}: {i.resposta_ia[:100]}..." 
                for i in interacoes_recentes
            ])
        
        # Tenta gerar situação contextual usando IA
        try:
            from .ai_client import get_ia_client
            from .prompts import ArquitetoDeMundosPrompts
            import asyncio
            
            prompt = f"""
            {ArquitetoDeMundosPrompts.get_sistema_base(
                self.sessao.estilo_narrativo,
                self.sessao.criatividade_nivel,
                self.sessao.dificuldade_nivel
            )}
            
            TAREFA: Criar uma nova situação após processar as ações dos jogadores
            
            CONTEXTO DA CAMPANHA:
            - Nome: {self.sessao.campanha.nome}
            - Descrição: {self.sessao.campanha.descricao}
            - Sessão: {self.sessao.nome}
            
            PERSONAGENS ATIVOS:
            {personagens_str}
            
            TURNO ATUAL:
            {turno_numero}
            
            CONTEXTO RECENTE DA SESSÃO:
            {contexto_recente if contexto_recente else "Início da sessão."}
            
            CRIE UMA NOVA SITUAÇÃO QUE:
            
            1. EVOLUA NATURALMENTE:
               - Reflita as consequências das ações anteriores
               - Mantenha consistência com o que já aconteceu
               - Introduza novos elementos interessantes
            
            2. CRIE OPORTUNIDADES:
               - Apresente novos desafios ou possibilidades
               - Dê opções interessantes para os personagens
               - Permita que cada personagem possa contribuir
            
            3. MANTENHA O RITMO:
               - Não seja muito longa ou muito curta
               - Crie tensão ou expectativa apropriada
               - Mantenha o interesse dos jogadores
            
            4. SEJA IMERSIVA:
               - Use descrições sensoriais
               - Crie uma atmosfera vívida
               - Torne o mundo real e tangível
            
            FORMATO DA RESPOSTA:
            Escreva uma descrição de situação (150-300 palavras) que:
            - Descreva como a situação evoluiu
            - Apresente o novo cenário ou desafio
            - Termine perguntando o que os personagens fazem
            
            Use o estilo narrativo definido e seja criativo mas coerente.
            """
            
            # Executa geração de forma síncrona
            ia_client = get_ia_client()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                resultado = loop.run_until_complete(
                    ia_client.gerar_conteudo(prompt, usar_cache=False)
                )
                nova_situacao = resultado['conteudo']
                
                # Registra a geração como interação
                InteracaoIA.objects.create(
                    sessao=self.sessao,
                    usuario=self.sessao.campanha.organizador,
                    tipo_interacao='NOVA_SITUACAO',
                    prompt_usuario=f'Nova situação para Turno {turno_numero}',
                    resposta_ia=nova_situacao[:2000],
                    tokens_usados=resultado.get('tokens_usados', 0),
                    contexto={'turno': turno_numero}
                )
                
                return {
                    'situacao': nova_situacao,
                    'chamada_jogadores': f"**{personagens_str}**, o que vocês fazem agora?",
                    'gerada_por_ia': True
                }
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.warning(f"Falha ao gerar nova situação com IA: {e}")
            # Fallback para situação genérica
            return self._gerar_situacao_generica_fallback(turno_numero, personagens_str)
    
    def _gerar_situacao_generica_fallback(self, turno_numero: int, personagens_str: str) -> Dict[str, Any]:
        """Gera situação genérica quando a IA falha"""
        situacao_generica = f"""🎭 **Turno {turno_numero} - A Aventura Continua**

Com base nas ações anteriores, a situação se desenvolve naturalmente. O mundo de **{self.sessao.campanha.nome}** responde às escolhas dos personagens, revelando novas possibilidades e desafios.

O ambiente ao redor dos heróis muda sutilmente, criando oportunidades para exploração, interação e descoberta. Cada decisão tomada ecoa no tecido da realidade, moldando o curso da aventura.

Com expectativa no ar, é hora de decidir como proceder nesta jornada épica."""
        
        return {
            'situacao': situacao_generica,
            'chamada_jogadores': f"**{personagens_str}**, como vocês reagem à nova situação?",
            'gerada_por_ia': False
        }
    
    def _obter_personagens_ativos(self) -> List[Personagem]:
        """Obtém lista de personagens ativos na campanha"""
        return list(Personagem.objects.filter(
            campanha=self.sessao.campanha,
            ativo=True
        ).select_related('usuario'))
    
    def _obter_personagem_do_usuario(self, usuario_id: int) -> Optional[Personagem]:
        """Obtém o personagem de um usuário específico nesta campanha"""
        try:
            return Personagem.objects.get(
                campanha=self.sessao.campanha,
                usuario_id=usuario_id,
                ativo=True
            )
        except Personagem.DoesNotExist:
            return None
    
    def _obter_estado_turno(self) -> Optional[EstadoTurno]:
        """Obtém o estado atual do turno do cache"""
        dados_turno = cache.get(self.cache_key_turno)
        if not dados_turno:
            return None
        
        # Reconstrói objetos AcaoJogador
        acoes_reconstruidas = []
        for acao_dict in dados_turno.get('acoes_recebidas', []):
            acao = AcaoJogador(**acao_dict)
            acoes_reconstruidas.append(acao)
        
        dados_turno['acoes_recebidas'] = acoes_reconstruidas
        
        return EstadoTurno(**dados_turno)
    
    def _registrar_interacao_jogador(self, personagem: Personagem, acao: str):
        """Registra a interação do jogador no banco de dados"""
        InteracaoIA.objects.create(
            sessao=self.sessao,
            usuario=personagem.usuario,
            tipo_interacao='ACAO_JOGADOR',
            prompt_usuario=f"{personagem.nome}: {acao}",
            resposta_ia="Ação registrada - aguardando outros jogadores",
            contexto={'personagem': personagem.nome, 'turno': 'aguardando'},
            tokens_usados=0
        )
    
    def pausar_sessao(self) -> Dict[str, Any]:
        """Pausa a sessão atual"""
        cache.set(self.cache_key_estado, EstadoSessao.PAUSADA.value, self.cache_timeout)
        
        return {
            "sessao_pausada": True,
            "mensagem": "⏸️ **Sessão pausada**. Use 'retomar' para continuar."
        }
    
    def retomar_sessao(self) -> Dict[str, Any]:
        """Retoma uma sessão pausada"""
        cache.set(self.cache_key_estado, EstadoSessao.ATIVA.value, self.cache_timeout)
        
        estado_turno = self._obter_estado_turno()
        if estado_turno:
            return {
                "sessao_retomada": True,
                "turno_atual": estado_turno.numero_turno,
                "fase_atual": estado_turno.fase.value,
                "mensagem": "▶️ **Sessão retomada**! Continuando a aventura..."
            }
        else:
            return self.ativar_modo_jogo()
    
    def encerrar_sessao(self, resumo: str = "") -> Dict[str, Any]:
        """Encerra a sessão de jogo"""
        self.sessao.ativa = False
        self.sessao.save()
        
        cache.delete(self.cache_key_estado)
        cache.delete(self.cache_key_turno)
        
        return {
            "sessao_encerrada": True,
            "resumo": resumo,
            "mensagem": "🏁 **Sessão encerrada**. Obrigado por jogarem!"
        }
    
    def obter_status_sessao(self) -> Dict[str, Any]:
        """Obtém status completo da sessão"""
        estado = self.estado_sessao
        estado_turno = self._obter_estado_turno()
        
        if estado_turno:
            return {
                "estado_sessao": estado.value,
                "turno_atual": estado_turno.numero_turno,
                "fase_atual": estado_turno.fase.value,
                "personagens_esperados": estado_turno.personagens_esperados,
                "aguardando_personagens": estado_turno.aguardando_personagens,
                "acoes_recebidas": len(estado_turno.acoes_recebidas)
            }
        else:
            return {
                "estado_sessao": estado.value,
                "pronto_para_iniciar": estado == EstadoSessao.CONFIGURACAO
            }