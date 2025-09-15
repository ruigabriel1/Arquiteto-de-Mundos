"""
Gestores de Conteúdo para o Sistema "Arquiteto de Mundos"
Integra com APIs de IA para gerar elementos narrativos dinâmicos
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache

from .models import (
    SessaoIA, NPCGerado, InteracaoIA,
    MemoriaLongoPrazo, TipoConteudo, EstiloNarrativo
)
from .prompts import PromptGenerator, ArquitetoDeMundosPrompts
from .ai_client import IAClient  # Cliente genérico para APIs de IA


@dataclass
class ConteudoGerado:
    """Resultado da geração de conteúdo pela IA"""
    tipo: str
    conteudo: str
    metadata: Dict[str, Any]
    qualidade: float = 0.0  # 0-1, avaliação automática da qualidade
    tokens_usados: int = 0
    tempo_geracao: float = 0.0
    modelo_usado: str = ""


class BaseContentManager:
    """Classe base para todos os geradores de conteúdo"""
    
    def __init__(self, ia_client: IAClient):
        self.ia_client = ia_client
        self.cache_timeout = 3600  # 1 hora
    
    def _get_cache_key(self, tipo: str, **kwargs) -> str:
        """Gera chave para cache baseada no tipo e parâmetros"""
        key_data = f"{tipo}:{hash(str(sorted(kwargs.items())))}"
        return f"arquiteto_mundos:{key_data}"
    
    def _avaliar_qualidade(self, conteudo: str, tipo: str) -> float:
        """Avalia automaticamente a qualidade do conteúdo gerado"""
        if not conteudo or len(conteudo.strip()) < 100:
            return 0.2
        
        # Critérios básicos de qualidade
        pontuacao = 0.5  # Base
        
        # Verifica se tem estrutura narrativa
        if any(palavra in conteudo.lower() for palavra in 
               ['porque', 'porém', 'então', 'assim', 'portanto']):
            pontuacao += 0.1
        
        # Verifica elementos específicos por tipo
        if tipo == 'npc':
            if all(palavra in conteudo.lower() for palavra in 
                   ['motivação', 'personalidade', 'história']):
                pontuacao += 0.2
        elif tipo == 'local':
            if all(palavra in conteudo.lower() for palavra in 
                   ['história', 'atmosfera', 'segredos']):
                pontuacao += 0.2
        elif tipo == 'missao':
            if all(palavra in conteudo.lower() for palavra in 
                   ['objetivo', 'desafio', 'recompensa']):
                pontuacao += 0.2
        
        # Verifica riqueza descritiva
        if len(conteudo) > 500:
            pontuacao += 0.1
        if len(conteudo) > 1000:
            pontuacao += 0.1
        
        return min(1.0, pontuacao)
    
    async def _gerar_com_retry(self, prompt: str, max_tentativas: int = 3) -> ConteudoGerado:
        """Gera conteúdo com sistema de retry e fallback"""
        ultima_excecao = None
        
        for tentativa in range(max_tentativas):
            try:
                inicio = asyncio.get_event_loop().time()
                resposta = await self.ia_client.gerar_conteudo(prompt)
                fim = asyncio.get_event_loop().time()
                
                conteudo_gerado = ConteudoGerado(
                    tipo=resposta.get('tipo', 'desconhecido'),
                    conteudo=resposta.get('conteudo', ''),
                    metadata=resposta.get('metadata', {}),
                    tokens_usados=resposta.get('tokens_usados', 0),
                    tempo_geracao=fim - inicio,
                    modelo_usado=resposta.get('modelo', 'desconhecido')
                )
                
                # Avalia qualidade
                conteudo_gerado.qualidade = self._avaliar_qualidade(
                    conteudo_gerado.conteudo, 
                    conteudo_gerado.tipo
                )
                
                # Se qualidade muito baixa, tenta novamente
                if conteudo_gerado.qualidade < 0.3 and tentativa < max_tentativas - 1:
                    continue
                
                return conteudo_gerado
                
            except Exception as e:
                ultima_excecao = e
                if tentativa < max_tentativas - 1:
                    await asyncio.sleep(2 ** tentativa)  # Backoff exponencial
        
        # Se chegou aqui, todas as tentativas falharam
        raise ultima_excecao


class NPCManager(BaseContentManager):
    """Gerenciador especializado na criação de NPCs"""
    
    async def gerar_npc(
        self,
        sessao: SessaoIA,
        contexto: Dict[str, Any],
        salvar_automaticamente: bool = True
    ) -> Tuple[NPCGerado, ConteudoGerado]:
        """
        Gera um NPC completo usando IA
        
        Args:
            sessao: Sessão GM ativa
            contexto: Contexto para geração (campanha, situação, etc.)
            salvar_automaticamente: Se deve salvar no banco automaticamente
        """
        # Prepara contexto expandido
        contexto_completo = {
            'campanha_nome': sessao.campanha.nome,
            'campanha_descricao': sessao.campanha.descricao,
            'sistema': 'D&D 5e',  # Padrão por enquanto
            'estilo': sessao.estilo_narrativo,
            'criatividade': sessao.criatividade_nivel,
            'dificuldade': sessao.dificuldade_nivel,
            **contexto
        }
        
        # Verifica cache primeiro
        cache_key = self._get_cache_key('npc', **contexto_completo)
        resultado_cache = cache.get(cache_key)
        if resultado_cache:
            return resultado_cache
        
        # Gera prompt
        prompt = PromptGenerator.gerar_npc(contexto_completo)
        
        # Gera conteúdo
        conteudo = await self._gerar_com_retry(prompt)
        
        # Cria objeto NPC
        npc = self._criar_npc_do_conteudo(conteudo, sessao)
        
        if salvar_automaticamente:
            npc.save()
            
            # Registra interação com IA
            InteracaoIA.objects.create(
                sessao=sessao,
                usuario=sessao.campanha.organizador,  # Assume que o organizador está gerando
                tipo_interacao=TipoConteudo.NPC,
                prompt_usuario=prompt[:2000],  # Limita tamanho
                resposta_ia=conteudo.conteudo[:2000],
                tokens_usados=conteudo.tokens_usados,
                tempo_geracao=conteudo.tempo_geracao,
                contexto={'qualidade': conteudo.qualidade, 'modelo': conteudo.modelo_usado}
            )
        
        # Cache resultado
        cache.set(cache_key, (npc, conteudo), self.cache_timeout)
        
        return npc, conteudo
    
    def _criar_npc_do_conteudo(self, conteudo: ConteudoGerado, sessao: SessaoIA) -> NPCGerado:
        """Converte conteúdo gerado em objeto NPC"""
        # Aqui você faria parsing inteligente do conteúdo
        # Por simplicidade, assumindo que a IA retorna JSON estruturado
        try:
            dados_npc = json.loads(conteudo.metadata.get('dados_estruturados', '{}'))
        except:
            # Fallback: parsing básico do texto
            dados_npc = self._extrair_dados_npc_texto(conteudo.conteudo)
        
        return NPCGerado(
            sessao=sessao,
            campanha=sessao.campanha,
            nome=dados_npc.get('nome', 'NPC Gerado'),
            descricao_fisica=dados_npc.get('aparencia', conteudo.conteudo[:500]),
            motivacao_principal=dados_npc.get('motivacao', 'Motivado por interesses pessoais'),
            falha_personalidade=dados_npc.get('falha', 'Tem seus próprios defeitos'),
            segredo=dados_npc.get('segredo', 'Guarda um segredo interessante'),
            maneirismos=dados_npc.get('maneirismos', 'Tem maneirismos únicos'),
            padrao_fala=dados_npc.get('padrao_fala', 'Fala de forma distinta'),
            recursos=dados_npc.get('recursos', 'Possui alguns recursos'),
            localizacao_atual=dados_npc.get('localizacao', 'Em algum lugar do mundo'),
            disposicao='NEUTRO'
        )
    
    def _extrair_dados_npc_texto(self, texto: str) -> Dict[str, Any]:
        """Extrai dados estruturados de texto livre (fallback)"""
        # Implementação básica de extração por regex/palavras-chave
        # Em um sistema real, você poderia usar NLP mais sofisticado
        linhas = texto.split('\n')
        dados = {}
        
        for linha in linhas:
            if 'nome:' in linha.lower():
                dados['nome'] = linha.split(':', 1)[1].strip()
            elif 'motivação:' in linha.lower():
                dados['motivacao'] = linha.split(':', 1)[1].strip()
            # ... mais extrações
        
        return dados
    
    async def gerar_dialogo_npc(
        self, 
        npc: NPCGerado, 
        contexto_dialogo: Dict[str, Any]
    ) -> ConteudoGerado:
        """Gera diálogo específico para um NPC existente"""
        contexto_completo = {
            'estilo': npc.sessao.estilo_narrativo,
            'criatividade': npc.sessao.criatividade_nivel,
            'dificuldade': npc.sessao.dificuldade_nivel,
            'npc': {
                'nome': npc.nome,
                'motivacao': npc.motivacao_principal,
                'falha': npc.falha_personalidade,
                'segredo': npc.segredo,
                'maneirismos': npc.maneirismos,
                'padrao_fala': npc.padrao_fala,
                'disposicao': npc.disposicao,
                'primeiro_encontro': npc.primeiro_encontro
            },
            **contexto_dialogo
        }
        
        prompt = PromptGenerator.gerar_dialogo(contexto_completo)
        conteudo = await self._gerar_com_retry(prompt)
        
        # Atualiza primeiro encontro se necessário
        if npc.primeiro_encontro:
            npc.primeiro_encontro = False
            npc.save()
        
        return conteudo




class ArquitetoDeMundosOrchestrator:
    """Orquestrador simplificado do Arquiteto de Mundos"""
    
    def __init__(self, ia_client):
        self.ia_client = ia_client
        self.npc_manager = NPCManager(ia_client)
        # Outros managers podem ser adicionados quando implementados
    
    async def processar_solicitacao(
        self, 
        sessao: SessaoIA, 
        tipo_solicitacao: str, 
        parametros: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Processa solicitação de geração de conteúdo"""
        try:
            if tipo_solicitacao == TipoConteudo.NPC:
                npc, conteudo = await self.npc_manager.gerar_npc(
                    sessao=sessao,
                    contexto=parametros
                )
                return {
                    'sucesso': True,
                    'tipo': TipoConteudo.NPC,
                    'conteudo_ia': conteudo,
                    'objeto_criado': npc,
                    'id': npc.id if npc.id else None
                }
            
            elif tipo_solicitacao in [TipoConteudo.NARRATIVA, TipoConteudo.LOCAL, TipoConteudo.MISSAO]:
                # Para outros tipos, gera conteúdo genérico
                conteudo = await self._gerar_conteudo_generico(
                    sessao=sessao,
                    tipo=tipo_solicitacao,
                    contexto=parametros
                )
                return {
                    'sucesso': True,
                    'tipo': tipo_solicitacao,
                    'conteudo_ia': conteudo
                }
            
            else:
                return {
                    'sucesso': False,
                    'erro': f'Tipo de conteúdo não suportado: {tipo_solicitacao}'
                }
                
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    async def _gerar_conteudo_generico(
        self, 
        sessao: SessaoIA, 
        tipo: str, 
        contexto: Dict[str, Any]
    ) -> ConteudoGerado:
        """Gera conteúdo genérico para tipos não especializados"""
        from .prompts import PromptGenerator
        
        # Prepara contexto
        contexto_completo = {
            'campanha_nome': sessao.campanha.nome,
            'campanha_descricao': sessao.campanha.descricao,
            'sistema': 'D&D 5e',
            'estilo': sessao.estilo_narrativo,
            'criatividade': sessao.criatividade_nivel,
            'dificuldade': sessao.dificuldade_nivel,
            **contexto
        }
        
        # Seleciona prompt baseado no tipo
        if tipo == TipoConteudo.NARRATIVA:
            prompt = PromptGenerator.gerar_narrativa(contexto_completo)
        elif tipo == TipoConteudo.LOCAL:
            prompt = PromptGenerator.gerar_local(contexto_completo)
        elif tipo == TipoConteudo.MISSAO:
            prompt = PromptGenerator.gerar_missao(contexto_completo)
        else:
            prompt = f"Crie um {tipo} interessante para a campanha baseado no contexto: {contexto_completo}"
        
        # Gera conteúdo
        resposta = await self.ia_client.gerar_conteudo(prompt)
        
        # Registra interação
        InteracaoIA.objects.create(
            sessao=sessao,
            usuario=sessao.campanha.organizador,
            tipo_interacao=tipo,
            prompt_usuario=prompt[:2000],
            resposta_ia=resposta.get('conteudo', '')[:2000],
            tokens_usados=resposta.get('tokens_usados', 0),
            contexto={'tipo': tipo, 'modelo': resposta.get('modelo', 'desconhecido')}
        )
        
        return ConteudoGerado(
            tipo=tipo,
            conteudo=resposta.get('conteudo', ''),
            metadata=resposta.get('metadata', {}),
            tokens_usados=resposta.get('tokens_usados', 0),
            tempo_geracao=resposta.get('tempo_resposta', 0.0),
            modelo_usado=resposta.get('modelo', 'desconhecido')
        )
    
    async def obter_sugestoes_contextuais(
        self, 
        sessao: SessaoIA, 
        situacao_atual: str = "Sessão em andamento"
    ) -> List[Dict[str, str]]:
        """Obtém sugestões contextuais da IA"""
        try:
            prompt = f"""
            Baseado na campanha "{sessao.campanha.nome}" e na situação atual "{situacao_atual}",
            sugira 4 elementos narrativos interessantes que o mestre poderia introduzir:
            1. Um NPC
            2. Um local
            3. Um evento
            4. Uma missão
            
            Seja criativo mas mantenha coerência com o tom da campanha.
            """
            
            resposta = await self.ia_client.gerar_conteudo(prompt)
            
            # Parse simples das sugestões
            linhas = resposta.get('conteudo', '').split('\n')
            sugestoes = []
            
            tipos = ['NPC', 'LOCAL', 'EVENTO', 'MISSAO']
            for i, linha in enumerate(linhas[:4]):
                if linha.strip():
                    sugestoes.append({
                        'tipo': tipos[i] if i < len(tipos) else 'GERAL',
                        'descricao': linha.strip()
                    })
            
            return sugestoes
            
        except Exception as e:
            # Fallback para sugestões estáticas
            return [
                {'tipo': 'NPC', 'descricao': 'Um comerciante com informações importantes'},
                {'tipo': 'LOCAL', 'descricao': 'Uma biblioteca antiga com segredos'},
                {'tipo': 'EVENTO', 'descricao': 'Uma estranha tempestade se aproxima'},
                {'tipo': 'MISSAO', 'descricao': 'Alguém precisa de ajuda na cidade'}
            ]
