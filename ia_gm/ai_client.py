"""
Cliente genérico para integração com APIs de IA
Suporta OpenAI, Anthropic Claude e outros provedores
"""

import asyncio
import aiohttp
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from django.conf import settings
from django.core.cache import cache


logger = logging.getLogger(__name__)


@dataclass
class RespostaIA:
    """Resposta padronizada de qualquer provedor de IA"""
    conteudo: str
    tipo: str
    metadata: Dict[str, Any]
    tokens_usados: int = 0
    modelo: str = "desconhecido"
    tempo_resposta: float = 0.0


class BaseIAProvider(ABC):
    """Interface base para todos os provedores de IA"""
    
    def __init__(self, api_key: str, modelo: str):
        self.api_key = api_key
        self.modelo = modelo
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def gerar_conteudo(self, prompt: str, **kwargs) -> RespostaIA:
        """Gera conteúdo usando o provedor específico"""
        pass
    
    @abstractmethod
    def calcular_custo_estimado(self, tokens_entrada: int, tokens_saida: int) -> float:
        """Calcula custo estimado em USD"""
        pass


class OpenAIProvider(BaseIAProvider):
    """Provedor OpenAI (GPT-4, GPT-3.5, etc.)"""
    
    BASE_URL = "https://api.openai.com/v1"
    
    # Preços por 1K tokens (USD) - Atualize conforme necessário
    PRECOS = {
        "gpt-4": {"entrada": 0.03, "saida": 0.06},
        "gpt-4-turbo": {"entrada": 0.01, "saida": 0.03},
        "gpt-3.5-turbo": {"entrada": 0.001, "saida": 0.002},
    }
    
    def __init__(self, api_key: str, modelo: str = "gpt-4"):
        super().__init__(api_key, modelo)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def gerar_conteudo(self, prompt: str, **kwargs) -> RespostaIA:
        """Gera conteúdo usando OpenAI"""
        inicio = asyncio.get_event_loop().time()
        
        payload = {
            "model": self.modelo,
            "messages": [
                {"role": "system", "content": "Você é um assistente especializado em RPG e narrativa."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get('max_tokens', 2000),
            "temperature": kwargs.get('temperature', 0.8),
            "top_p": kwargs.get('top_p', 0.9),
        }
        
        try:
            async with self.session.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    erro_texto = await response.text()
                    raise Exception(f"Erro OpenAI ({response.status}): {erro_texto}")
                
                dados = await response.json()
                fim = asyncio.get_event_loop().time()
                
                conteudo = dados['choices'][0]['message']['content']
                tokens_usados = dados['usage']['total_tokens']
                
                return RespostaIA(
                    conteudo=conteudo,
                    tipo="texto",
                    metadata={
                        "finish_reason": dados['choices'][0]['finish_reason'],
                        "prompt_tokens": dados['usage']['prompt_tokens'],
                        "completion_tokens": dados['usage']['completion_tokens'],
                        "custo_estimado": self.calcular_custo_estimado(
                            dados['usage']['prompt_tokens'],
                            dados['usage']['completion_tokens']
                        )
                    },
                    tokens_usados=tokens_usados,
                    modelo=self.modelo,
                    tempo_resposta=fim - inicio
                )
        
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo OpenAI: {e}")
            raise
    
    def calcular_custo_estimado(self, tokens_entrada: int, tokens_saida: int) -> float:
        """Calcula custo estimado para OpenAI"""
        precos = self.PRECOS.get(self.modelo, self.PRECOS["gpt-4"])
        
        custo_entrada = (tokens_entrada / 1000) * precos["entrada"]
        custo_saida = (tokens_saida / 1000) * precos["saida"]
        
        return custo_entrada + custo_saida


class AnthropicProvider(BaseIAProvider):
    """Provedor Anthropic (Claude)"""
    
    BASE_URL = "https://api.anthropic.com/v1"
    
    # Preços por 1K tokens (USD)
    PRECOS = {
        "claude-3-opus-20240229": {"entrada": 0.015, "saida": 0.075},
        "claude-3-sonnet-20240229": {"entrada": 0.003, "saida": 0.015},
        "claude-3-haiku-20240307": {"entrada": 0.00025, "saida": 0.00125},
    }
    
    def __init__(self, api_key: str, modelo: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key, modelo)
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
    
    async def gerar_conteudo(self, prompt: str, **kwargs) -> RespostaIA:
        """Gera conteúdo usando Anthropic Claude"""
        inicio = asyncio.get_event_loop().time()
        
        payload = {
            "model": self.modelo,
            "max_tokens": kwargs.get('max_tokens', 2000),
            "temperature": kwargs.get('temperature', 0.8),
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            async with self.session.post(
                f"{self.BASE_URL}/messages",
                headers=self.headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    erro_texto = await response.text()
                    raise Exception(f"Erro Anthropic ({response.status}): {erro_texto}")
                
                dados = await response.json()
                fim = asyncio.get_event_loop().time()
                
                conteudo = dados['content'][0]['text']
                tokens_entrada = dados['usage']['input_tokens']
                tokens_saida = dados['usage']['output_tokens']
                tokens_total = tokens_entrada + tokens_saida
                
                return RespostaIA(
                    conteudo=conteudo,
                    tipo="texto",
                    metadata={
                        "stop_reason": dados.get('stop_reason'),
                        "input_tokens": tokens_entrada,
                        "output_tokens": tokens_saida,
                        "custo_estimado": self.calcular_custo_estimado(tokens_entrada, tokens_saida)
                    },
                    tokens_usados=tokens_total,
                    modelo=self.modelo,
                    tempo_resposta=fim - inicio
                )
        
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo Anthropic: {e}")
            raise
    
    def calcular_custo_estimado(self, tokens_entrada: int, tokens_saida: int) -> float:
        """Calcula custo estimado para Anthropic"""
        precos = self.PRECOS.get(self.modelo, self.PRECOS["claude-3-sonnet-20240229"])
        
        custo_entrada = (tokens_entrada / 1000) * precos["entrada"]
        custo_saida = (tokens_saida / 1000) * precos["saida"]
        
        return custo_entrada + custo_saida


class LocalProvider(BaseIAProvider):
    """Provedor para modelos locais (Ollama, LM Studio, etc.)"""
    
    def __init__(self, base_url: str, modelo: str, api_key: str = ""):
        super().__init__(api_key, modelo)
        self.base_url = base_url.rstrip('/')
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    async def gerar_conteudo(self, prompt: str, **kwargs) -> RespostaIA:
        """Gera conteúdo usando modelo local"""
        inicio = asyncio.get_event_loop().time()
        
        # Formato compatível com Ollama
        payload = {
            "model": self.modelo,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', 0.8),
                "top_p": kwargs.get('top_p', 0.9),
                "max_tokens": kwargs.get('max_tokens', 2000)
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                headers=self.headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    erro_texto = await response.text()
                    raise Exception(f"Erro Modelo Local ({response.status}): {erro_texto}")
                
                dados = await response.json()
                fim = asyncio.get_event_loop().time()
                
                return RespostaIA(
                    conteudo=dados.get('response', ''),
                    tipo="texto",
                    metadata={
                        "eval_count": dados.get('eval_count', 0),
                        "eval_duration": dados.get('eval_duration', 0),
                        "custo_estimado": 0.0  # Modelo local = gratuito
                    },
                    tokens_usados=dados.get('eval_count', 0),
                    modelo=self.modelo,
                    tempo_resposta=fim - inicio
                )
        
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo modelo local: {e}")
            raise
    
    def calcular_custo_estimado(self, tokens_entrada: int, tokens_saida: int) -> float:
        """Modelos locais são gratuitos"""
        return 0.0


class IAClient:
    """
    Cliente principal que abstrai diferentes provedores de IA
    Implementa balanceamento de carga, fallback e cache
    """
    
    def __init__(self):
        self.provedores = []
        self.provedor_principal = None
        self.configurar_provedores()
    
    def configurar_provedores(self):
        """Configura provedores baseado nas configurações Django"""
        
        # OpenAI
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            openai_modelo = getattr(settings, 'OPENAI_MODELO', 'gpt-4')
            provedor = OpenAIProvider(settings.OPENAI_API_KEY, openai_modelo)
            self.provedores.append(('openai', provedor))
            if not self.provedor_principal:
                self.provedor_principal = provedor
        
        # Anthropic
        if hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
            anthropic_modelo = getattr(settings, 'ANTHROPIC_MODELO', 'claude-3-sonnet-20240229')
            provedor = AnthropicProvider(settings.ANTHROPIC_API_KEY, anthropic_modelo)
            self.provedores.append(('anthropic', provedor))
            if not self.provedor_principal:
                self.provedor_principal = provedor
        
        # Modelo Local (Ollama, etc.)
        if hasattr(settings, 'LOCAL_AI_URL') and settings.LOCAL_AI_URL:
            local_modelo = getattr(settings, 'LOCAL_AI_MODELO', 'llama2')
            local_api_key = getattr(settings, 'LOCAL_AI_API_KEY', '')
            provedor = LocalProvider(settings.LOCAL_AI_URL, local_modelo, local_api_key)
            self.provedores.append(('local', provedor))
            if not self.provedor_principal:
                self.provedor_principal = provedor
        
        if not self.provedores:
            raise Exception("Nenhum provedor de IA configurado! Verifique settings.py")
        
        logger.info(f"Configurados {len(self.provedores)} provedores de IA")
    
    async def gerar_conteudo(
        self, 
        prompt: str, 
        usar_cache: bool = True,
        provedor_preferido: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Gera conteúdo usando o melhor provedor disponível
        
        Args:
            prompt: Prompt para geração
            usar_cache: Se deve usar cache para esta solicitação
            provedor_preferido: Nome do provedor específico ('openai', 'anthropic', 'local')
            **kwargs: Parâmetros adicionais (temperature, max_tokens, etc.)
        """
        
        # Verifica cache primeiro
        if usar_cache:
            cache_key = f"ia_gm:prompt:{hash(prompt)}"
            resultado_cache = cache.get(cache_key)
            if resultado_cache:
                logger.info("Resultado obtido do cache")
                return resultado_cache
        
        # Seleciona provedor
        provedor_selecionado = None
        
        if provedor_preferido:
            for nome, provedor in self.provedores:
                if nome == provedor_preferido:
                    provedor_selecionado = provedor
                    break
        
        if not provedor_selecionado:
            provedor_selecionado = self.provedor_principal
        
        # Tenta gerar conteúdo
        ultima_excecao = None
        
        for nome, provedor in self.provedores:
            if provedor != provedor_selecionado and provedor_preferido:
                continue  # Só tenta o preferido se especificado
            
            try:
                async with provedor:
                    logger.info(f"Gerando conteúdo com {nome}")
                    resposta = await provedor.gerar_conteudo(prompt, **kwargs)
                    
                    resultado = {
                        'conteudo': resposta.conteudo,
                        'tipo': resposta.tipo,
                        'metadata': resposta.metadata,
                        'tokens_usados': resposta.tokens_usados,
                        'modelo': resposta.modelo,
                        'tempo_resposta': resposta.tempo_resposta,
                        'provedor': nome,
                        'custo_estimado': resposta.metadata.get('custo_estimado', 0.0)
                    }
                    
                    # Salva no cache
                    if usar_cache:
                        cache.set(cache_key, resultado, 3600)  # 1 hora
                    
                    return resultado
            
            except Exception as e:
                logger.warning(f"Falha no provedor {nome}: {e}")
                ultima_excecao = e
                
                # Se não foi especificado provedor preferido, tenta o próximo
                if not provedor_preferido:
                    continue
                else:
                    break
        
        # Se chegou aqui, todos falharam
        raise Exception(f"Todos os provedores de IA falharam. Última exceção: {ultima_excecao}")
    
    async def listar_modelos_disponiveis(self) -> Dict[str, List[str]]:
        """Lista todos os modelos disponíveis por provedor"""
        modelos = {}
        
        for nome, provedor in self.provedores:
            if nome == 'openai':
                modelos[nome] = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
            elif nome == 'anthropic':
                modelos[nome] = [
                    'claude-3-opus-20240229', 
                    'claude-3-sonnet-20240229',
                    'claude-3-haiku-20240307'
                ]
            elif nome == 'local':
                modelos[nome] = [provedor.modelo]  # Modelo configurado
        
        return modelos
    
    async def estimar_custo(self, prompt: str, max_tokens: int = 2000) -> Dict[str, float]:
        """Estima custo para cada provedor disponível"""
        custos = {}
        
        # Estimativa rough de tokens de entrada
        tokens_entrada = len(prompt.split()) * 1.3  # Aproximação
        tokens_saida = max_tokens
        
        for nome, provedor in self.provedores:
            custo = provedor.calcular_custo_estimado(int(tokens_entrada), tokens_saida)
            custos[nome] = custo
        
        return custos
    
    def obter_estatisticas_uso(self) -> Dict[str, Any]:
        """Obtém estatísticas de uso dos provedores (se disponível)"""
        # Implementação básica - poderia ser expandida com métricas reais
        return {
            'provedores_configurados': len(self.provedores),
            'provedor_principal': self.provedor_principal.__class__.__name__ if self.provedor_principal else None,
            'provedores_disponiveis': [nome for nome, _ in self.provedores]
        }


# Instância global do cliente (singleton)
_ia_client_instance = None

def get_ia_client() -> IAClient:
    """Obtém instância singleton do cliente de IA"""
    global _ia_client_instance
    if _ia_client_instance is None:
        _ia_client_instance = IAClient()
    return _ia_client_instance


# Factory functions para facilitar uso
async def gerar_conteudo_ia(prompt: str, **kwargs) -> Dict[str, Any]:
    """Função de conveniência para gerar conteúdo"""
    client = get_ia_client()
    return await client.gerar_conteudo(prompt, **kwargs)


async def gerar_com_fallback(prompts: List[str], **kwargs) -> Dict[str, Any]:
    """
    Tenta múltiplos prompts até um funcionar
    Útil para quando o primeiro prompt pode falhar
    """
    client = get_ia_client()
    ultima_excecao = None
    
    for prompt in prompts:
        try:
            return await client.gerar_conteudo(prompt, **kwargs)
        except Exception as e:
            ultima_excecao = e
            continue
    
    raise Exception(f"Todos os prompts falharam. Última exceção: {ultima_excecao}")