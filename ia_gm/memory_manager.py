"""
Gerenciador de Memória Simplificado para o Arquiteto de Mundos
"""

from typing import Dict, Any, List, Optional
from .models import SessaoIA, MemoriaLongoPrazo, InteracaoIA
from django.utils import timezone


class MemoryManager:
    """Gerenciador simplificado de memória para IA GM"""
    
    def __init__(self):
        pass
    
    def compilar_contexto_narrativo(self, sessao: SessaoIA) -> Dict[str, Any]:
        """Compila contexto narrativo para a sessão"""
        # Busca últimas memórias importantes
        memorias_recentes = MemoriaLongoPrazo.objects.filter(
            campanha=sessao.campanha
        ).order_by('-data_evento')[:10]
        
        # Últimas interações
        interacoes_recentes = InteracaoIA.objects.filter(
            sessao=sessao
        ).order_by('-data_interacao')[:5]
        
        return {
            'campanha': {
                'nome': sessao.campanha.nome,
                'descricao': sessao.campanha.descricao,
            },
            'memorias_importantes': [
                {
                    'titulo': m.titulo,
                    'descricao': m.descricao,
                    'importancia': m.importancia,
                    'data': m.data_evento.isoformat()
                } for m in memorias_recentes
            ],
            'interacoes_recentes': [
                {
                    'tipo': i.tipo_interacao,
                    'prompt': i.prompt_usuario[:200],
                    'resposta': i.resposta_ia[:200]
                } for i in interacoes_recentes
            ],
            'configuracao': {
                'estilo': sessao.estilo_narrativo,
                'criatividade': sessao.criatividade_nivel,
                'dificuldade': sessao.dificuldade_nivel
            }
        }
    
    def identificar_oportunidades_narrativas(self, sessao: SessaoIA) -> List[Dict[str, str]]:
        """Identifica oportunidades narrativas baseadas na memória"""
        # Por enquanto, retorna oportunidades genéricas
        return [
            {
                'tipo': 'CONSEQUENCIA',
                'descricao': 'Desenvolver consequências de ações passadas',
                'prioridade': 'media'
            },
            {
                'tipo': 'GANCHO_PESSOAL',
                'descricao': 'Criar conexões com histórias dos personagens',
                'prioridade': 'alta'
            },
            {
                'tipo': 'REVELACAO',
                'descricao': 'Revelar informações sobre mistérios anteriores',
                'prioridade': 'baixa'
            }
        ]
    
    def registrar_evento_importante(
        self, 
        sessao: SessaoIA, 
        titulo: str, 
        descricao: str, 
        importancia: int = 3
    ) -> MemoriaLongoPrazo:
        """Registra um evento importante na memória de longo prazo"""
        return MemoriaLongoPrazo.objects.create(
            campanha=sessao.campanha,
            titulo=titulo,
            descricao=descricao,
            categoria='DECISAO',  # Categoria padrão
            impacto_narrativo=f"Evento registrado com importância {importancia}",
            importancia=min(importancia, 5),
            data_evento=timezone.now()
        )


# Instância singleton
_memory_manager_instance = None

def get_memory_manager() -> MemoryManager:
    """Obtém instância singleton do gerenciador de memória"""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance