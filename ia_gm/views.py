from django.shortcuts import render

"""
Views para o sistema "Arquiteto de Mundos" - Interface de Mestre IA
Implementa interface web para interação durante as sessões
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q
from asgiref.sync import sync_to_async
import logging
from django.utils import timezone

from campanhas.models import Campanha
from .models import (
    SessaoIA, NPCGerado, InteracaoIA, 
    MemoriaLongoPrazo, EstiloNarrativo, TipoConteudo
)
from .content_generators import ArquitetoDeMundosOrchestrator
from .memory_manager import get_memory_manager
from .ai_client import get_ia_client
from .game_session_manager import GameSessionManager

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class ArquitetoPainelView(TemplateView):
    """Painel principal do Arquiteto de Mundos"""
    template_name = 'ia_gm/painel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Campanhas do usuário (apenas como organizador)
        campanhas = Campanha.objects.filter(organizador=self.request.user)
        
        # Sessões recentes
        try:
            sessoes_recentes = SessaoIA.objects.filter(
                campanha__in=campanhas
            ).select_related('campanha').order_by('-data_criacao')[:5]
        except Exception:
            sessoes_recentes = []
        
        # Estatísticas
        try:
            total_campanhas = campanhas.count()
            total_personagens = 0
            total_sessoes = SessaoIA.objects.filter(campanha__in=campanhas).count()
            total_interacoes = InteracaoIA.objects.filter(sessao__campanha__in=campanhas).count()
            
            # Contar personagens das campanhas
            from personagens.models import Personagem
            total_personagens = Personagem.objects.filter(campanha__in=campanhas).count()
            
        except Exception as e:
            logger.warning(f"Erro ao carregar estatísticas: {e}")
            total_campanhas = campanhas.count()
            total_personagens = 0
            total_sessoes = 0
            total_interacoes = 0
        
        context.update({
            'campanhas': campanhas,
            'sessoes_recentes': sessoes_recentes,
            'total_campanhas': total_campanhas,
            'total_personagens': total_personagens,
            'total_sessoes': total_sessoes,
            'total_interacoes': total_interacoes,
        })
        
        return context


@method_decorator(login_required, name='dispatch')
class SessaoGMView(TemplateView):
    """Interface principal para condução de sessão com IA"""
    template_name = 'ia_gm/sessao.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sessao_id = self.kwargs.get('sessao_id')
        
        try:
            sessao = get_object_or_404(SessaoIA, id=sessao_id)
            
            # Verifica permissão
            if not (sessao.campanha.organizador == self.request.user or 
                   self.request.user in sessao.campanha.jogadores.all()):
                messages.error(self.request, "Você não tem permissão para acessar esta sessão.")
                return redirect('ia_gm:painel')
            
            # Personagens da campanha
            from personagens.models import Personagem
            personagens = Personagem.objects.filter(
                campanha=sessao.campanha, 
                ativo=True
            ).select_related('usuario')
            
            # NPCs da sessão
            npcs = NPCGerado.objects.filter(sessao=sessao).order_by('-data_criacao')
            
            # Interações recentes
            interacoes = InteracaoIA.objects.filter(sessao=sessao).order_by('-data_interacao')[:10]
            
            # Memórias recentes da campanha
            memorias_recentes = MemoriaLongoPrazo.objects.filter(
                campanha=sessao.campanha
            ).order_by('-data_evento')[:10]
            
            context.update({
                'sessao': sessao,
                'personagens': personagens,
                'npcs': npcs,
                'interacoes': interacoes,
                'memorias_recentes': memorias_recentes,
                'estilos_narrativos': EstiloNarrativo.choices,
                'tipos_conteudo': TipoConteudo.choices,
            })
            
        except Exception as e:
            logger.error(f"Erro ao carregar sessão GM: {e}")
            messages.error(self.request, f"Erro ao carregar sessão: {e}")
            context['erro'] = str(e)
        
        return context


@login_required
def criar_sessao_gm(request, campanha_id):
    """Cria uma nova sessão do Arquiteto de Mundos"""
    # Permitir campanha_id = 0 para seleção
    if campanha_id == 0:
        # Redirecionar para seleção de campanha
        campanhas = Campanha.objects.filter(organizador=request.user)
        if campanhas.count() == 1:
            campanha = campanhas.first()
        else:
            messages.info(request, "Selecione uma campanha para criar a sessão.")
            return redirect('ia_gm:painel')
    else:
        campanha = get_object_or_404(Campanha, id=campanha_id)
    
    # Verifica permissão
    if campanha.organizador != request.user:
        messages.error(request, "Apenas o organizador pode criar sessões de IA.")
        return redirect('ia_gm:painel')
    
    if request.method == 'POST':
        try:
            # Dados do formulário
            nome_sessao = request.POST.get('nome_sessao')
            descricao = request.POST.get('descricao', '')
            estilo_narrativo = request.POST.get('estilo_narrativo', EstiloNarrativo.EPICO)
            nivel_criatividade = int(request.POST.get('nivel_criatividade', 7))
            nivel_dificuldade = int(request.POST.get('nivel_dificuldade', 5))
            
            # Cria sessão
            sessao = SessaoIA.objects.create(
                campanha=campanha,
                nome=nome_sessao,
                descricao=descricao,
                estilo_narrativo=estilo_narrativo,
                criatividade_nivel=nivel_criatividade,
                dificuldade_nivel=nivel_dificuldade,
                ativa=True
            )
            
            messages.success(request, f"Sessão '{nome_sessao}' criada com sucesso!")
            return redirect('ia_gm:sessao', sessao_id=sessao.id)
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão GM: {e}")
            messages.error(request, f"Erro ao criar sessão: {e}")
    
    # GET request - mostra formulário
    context = {
        'campanha': campanha,
        'estilos_narrativos': EstiloNarrativo.choices,
    }
    return render(request, 'ia_gm/criar_sessao.html', context)


@csrf_exempt
@require_POST
async def api_gerar_conteudo(request: HttpRequest) -> JsonResponse:
    """
    API endpoint para gerar conteúdo usando IA (Versão Simplificada)
    Suporta NPCs, locais, missões, itens e narrativa
    """
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Usuário não autenticado'}, status=401)
    
    try:
        dados = json.loads(request.body)
        sessao_id = dados.get('sessao_id')
        tipo_conteudo = dados.get('tipo')
        parametros = dados.get('parametros', {})
        
        # Verifica sessão
        try:
            sessao = await sync_to_async(get_object_or_404)(SessaoIA, id=sessao_id)
        except:
            return JsonResponse({'erro': 'Sessão não encontrada'}, status=404)
        
        # Verifica permissão
        campanha_organizador = await sync_to_async(lambda: sessao.campanha.organizador)()
        jogadores = await sync_to_async(list)(sessao.campanha.jogadores.all())
        
        if not (campanha_organizador == request.user or request.user in jogadores):
            return JsonResponse({'erro': 'Sem permissão'}, status=403)
        
        # Gera conteúdo usando IA real
        try:
            ia_client = get_ia_client()
            orchestrator = ArquitetoDeMundosOrchestrator(ia_client)
            
            # Processa solicitação usando IA
            resultado = await orchestrator.processar_solicitacao(
                sessao=sessao,
                tipo_solicitacao=tipo_conteudo,
                parametros=parametros
            )
            
            if resultado['sucesso']:
                return JsonResponse({
                    'sucesso': True,
                    'tipo': resultado['tipo'],
                    'conteudo': resultado['conteudo_ia'].conteudo,
                    'metadata': resultado['conteudo_ia'].metadata,
                    'tokens_usados': resultado['conteudo_ia'].tokens_usados,
                    'custo_estimado': resultado.get('custo_estimado', 0),
                    'objeto_id': resultado.get('id')
                })
            else:
                return JsonResponse({
                    'sucesso': False,
                    'erro': resultado['erro']
                }, status=400)
                
        except Exception as e:
            # Fallback para conteúdo de exemplo se a IA falhar
            logger.warning(f"IA falhou, usando fallback: {e}")
            
            conteudo_exemplo = {
                'NPC': 'Um mercador misterioso chamado Aldric, com olhos verde-esmeralda.',
                'LOCAL': 'Uma taverna acolhedora com lareiras crepitantes e música suave.',
                'MISSAO': 'Investigar os estranhos ruídos vindos da floresta à noite.',
                'NARRATIVA': 'A neblina se dissipa revelando um caminho antes oculto...',
            }
            
            # Registra interação de fallback
            InteracaoIA.objects.create(
                sessao=sessao,
                usuario=request.user,
                tipo_interacao=tipo_conteudo,
                prompt_usuario=f"Gerar {tipo_conteudo}: {parametros} [FALLBACK]",
                resposta_ia=conteudo_exemplo.get(tipo_conteudo, 'Conteúdo não implementado'),
                contexto={**parametros, 'erro_ia': str(e)},
                tokens_usados=0
            )
            
            return JsonResponse({
                'sucesso': True,
                'tipo': tipo_conteudo,
                'conteudo': conteudo_exemplo.get(tipo_conteudo, 'Conteúdo não implementado'),
                'metadata': {'tipo': tipo_conteudo, 'gerado_em': timezone.now().isoformat(), 'fallback': True},
                'tokens_usados': 0,
                'aviso': 'IA indisponível, usando conteúdo de exemplo'
            })
    
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro na API de geração: {e}")
        return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_registrar_evento(request: HttpRequest) -> JsonResponse:
    """API para registrar eventos importantes na memória"""
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Usuário não autenticado'}, status=401)
    
    try:
        dados = json.loads(request.body)
        sessao_id = dados.get('sessao_id')
        evento = dados.get('evento')
        participantes = dados.get('participantes', [])
        locais = dados.get('locais', [])
        importancia = dados.get('importancia', 5)
        tags = dados.get('tags', [])
        
        sessao = get_object_or_404(SessaoIA, id=sessao_id)
        
        # Verifica permissão
        if not (sessao.campanha.organizador == request.user or 
               request.user in sessao.campanha.jogadores.all()):
            return JsonResponse({'erro': 'Sem permissão'}, status=403)
        
        # Por enquanto, apenas registra na memória simples
        memoria = MemoriaLongoPrazo.objects.create(
            campanha=sessao.campanha,
            titulo=evento[:100],  # Limita o título
            descricao=evento,
            categoria='DECISAO',
            impacto_narrativo=f"Evento de importância {importancia}",
            importancia=min(importancia, 5),
            data_evento=timezone.now()
        )
        
        return JsonResponse({
            'sucesso': True,
            'memoria_id': memoria.id,
            'mensagem': 'Evento registrado na memória'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao registrar evento: {e}")
        return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET'])
async def api_obter_sugestoes(request: HttpRequest, sessao_id: int) -> JsonResponse:
    """API para obter sugestões contextuais"""
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Usuário não autenticado'}, status=401)
    
    try:
        sessao = await sync_to_async(get_object_or_404)(SessaoIA, id=sessao_id)
        
        # Verifica permissão
        campanha_organizador = await sync_to_async(lambda: sessao.campanha.organizador)()
        jogadores = await sync_to_async(list)(sessao.campanha.jogadores.all())
        
        if not (campanha_organizador == request.user or request.user in jogadores):
            return JsonResponse({'erro': 'Sem permissão'}, status=403)
        
        # Obtém sugestões usando IA
        try:
            ia_client = get_ia_client()
            orchestrator = ArquitetoDeMundosOrchestrator(ia_client)
            
            sugestoes = await orchestrator.obter_sugestoes_contextuais(
                sessao=sessao,
                situacao_atual=request.GET.get('situacao', 'Sessão em andamento')
            )
        except Exception as e:
            logger.warning(f"Falha ao obter sugestões da IA: {e}")
            # Fallback para sugestões estáticas
            sugestoes = [
                {'tipo': 'NPC', 'descricao': 'Introduzir um comerciante local com informações importantes'},
                {'tipo': 'LOCAL', 'descricao': 'Adicionar uma biblioteca antiga com segredos'},
                {'tipo': 'EVENTO', 'descricao': 'Uma estranha tempestade se aproxima'},
                {'tipo': 'MISSAO', 'descricao': 'Alguém precisa de ajuda na praça da cidade'},
            ]
        
        return JsonResponse({
            'sucesso': True,
            'sugestoes': sugestoes
        })
    
    except Exception as e:
        logger.error(f"Erro ao obter sugestões: {e}")
        return JsonResponse({'erro': str(e)}, status=500)


@login_required
def historico_interacoes(request, sessao_id):
    """Mostra histórico de interações com IA"""
    sessao = get_object_or_404(SessaoIA, id=sessao_id)
    
    # Verifica permissão
    if not (sessao.campanha.organizador == request.user or 
           request.user in sessao.campanha.jogadores.all()):
        messages.error(request, "Você não tem permissão para acessar este histórico.")
        return redirect('ia_gm:painel')
    
    # Paginação das interações
    interacoes = InteracaoIA.objects.filter(
        sessao=sessao
    ).order_by('-data_interacao')
    
    paginator = Paginator(interacoes, 20)  # 20 por página
    page = request.GET.get('page')
    interacoes_paginadas = paginator.get_page(page)
    
    context = {
        'sessao': sessao,
        'interacoes': interacoes_paginadas,
        'total_tokens': sum(i.tokens_usados for i in interacoes),
    }
    
    return render(request, 'ia_gm/historico_interacoes.html', context)


@login_required
def analise_personagem(request, sessao_id):
    """Interface para análise profunda de personagens"""
    sessao = get_object_or_404(SessaoIA, id=sessao_id)
    
    # Verifica permissão
    if not (sessao.campanha.organizador == request.user or 
           request.user in sessao.campanha.jogadores.all()):
        messages.error(request, "Você não tem permissão para acessar esta análise.")
        return redirect('ia_gm:painel')
    
    nome_personagem = request.GET.get('personagem')
    analise = None
    
    if nome_personagem:
        analise = f"Análise de {nome_personagem}: Personagem interessante com potencial narrativo."
    
    # Lista de personagens da campanha
    personagens_campanha = sessao.campanha.personagens.all()
    todos_personagens = [p.nome for p in personagens_campanha]
    
    context = {
        'sessao': sessao,
        'personagens_disponiveis': sorted(todos_personagens),
        'personagem_selecionado': nome_personagem,
        'analise': analise
    }
    
    return render(request, 'ia_gm/analise_personagem.html', context)


@login_required
def biblioteca_conteudo(request, sessao_id):
    """Biblioteca de conteúdo gerado para a sessão"""
    sessao = get_object_or_404(SessaoIA, id=sessao_id)
    
    # Verifica permissão
    if not (sessao.campanha.organizador == request.user or 
           request.user in sessao.campanha.jogadores.all()):
        messages.error(request, "Você não tem permissão para acessar esta biblioteca.")
        return redirect('ia_gm:painel')
    
    # Filtros
    tipo_filtro = request.GET.get('tipo', 'todos')
    busca = request.GET.get('busca', '')
    
    # NPCs
    npcs_query = NPCGerado.objects.filter(sessao=sessao)
    if busca:
        npcs_query = npcs_query.filter(
            Q(nome__icontains=busca) | 
            Q(descricao_fisica__icontains=busca)
        )
    npcs = npcs_query.order_by('-data_criacao')
    
    # Interações (em lugar de locais/missões/itens por enquanto)
    interacoes_query = InteracaoIA.objects.filter(sessao=sessao)
    if busca:
        interacoes_query = interacoes_query.filter(
            Q(prompt_usuario__icontains=busca) |
            Q(resposta_ia__icontains=busca)
        )
    interacoes = interacoes_query.order_by('-data_interacao')
    
    context = {
        'sessao': sessao,
        'npcs': npcs,
        'interacoes': interacoes,
        'tipo_filtro': tipo_filtro,
        'busca': busca,
        'total_conteudo': npcs.count() + interacoes.count()
    }
    
    return render(request, 'ia_gm/biblioteca_conteudo.html', context)


@csrf_exempt
@require_POST
def api_atualizar_configuracoes_sessao(request: HttpRequest) -> JsonResponse:
    """API para atualizar configurações da sessão"""
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Usuário não autenticado'}, status=401)
    
    try:
        dados = json.loads(request.body)
        sessao_id = dados.get('sessao_id')
        
        sessao = get_object_or_404(SessaoIA, id=sessao_id)
        
        # Verifica permissão (apenas organizador pode alterar configurações)
        if sessao.campanha.organizador != request.user:
            return JsonResponse({'erro': 'Apenas o organizador pode alterar as configurações'}, status=403)
        
        # Atualiza configurações
        if 'estilo_narrativo' in dados:
            sessao.estilo_narrativo = dados['estilo_narrativo']
        if 'criatividade_nivel' in dados:
            sessao.criatividade_nivel = int(dados['criatividade_nivel'])
        if 'dificuldade_nivel' in dados:
            sessao.dificuldade_nivel = int(dados['dificuldade_nivel'])
        
        sessao.save()
        
        return JsonResponse({
            'sucesso': True,
            'mensagem': 'Configurações atualizadas com sucesso'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao atualizar configurações: {e}")
        return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_encerrar_sessao(request: HttpRequest) -> JsonResponse:
    """API para encerrar uma sessão"""
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Usuário não autenticado'}, status=401)
    
    try:
        dados = json.loads(request.body)
        sessao_id = dados.get('sessao_id')
        resumo_final = dados.get('resumo_final', '')
        
        sessao = get_object_or_404(SessaoIA, id=sessao_id)
        
        # Verifica permissão
        if sessao.campanha.organizador != request.user:
            return JsonResponse({'erro': 'Apenas o organizador pode encerrar a sessão'}, status=403)
        
        # Encerra sessão
        sessao.ativa = False
        sessao.save()
        
        # Registra na memória
        MemoriaLongoPrazo.objects.create(
            campanha=sessao.campanha,
            titulo=f"Sessão {sessao.nome} encerrada",
            descricao=f"Sessão encerrada. Resumo: {resumo_final}",
            categoria='CONQUISTA',
            impacto_narrativo='Sessão finalizada',
            importancia=4,
            data_evento=timezone.now()
        )
        
        return JsonResponse({
            'sucesso': True,
            'mensagem': 'Sessão encerrada com sucesso'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao encerrar sessão: {e}")
        return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_ativar_modo_jogo(request: HttpRequest) -> JsonResponse:
    """API para ativar o modo de jogo da sessão"""
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Usuário não autenticado'}, status=401)
    
    try:
        dados = json.loads(request.body)
        sessao_id = dados.get('sessao_id')
        
        sessao = get_object_or_404(SessaoIA, id=sessao_id)
        
        # Verifica permissão (apenas organizador pode ativar)
        if sessao.campanha.organizador != request.user:
            return JsonResponse({'erro': 'Apenas o organizador pode ativar o modo de jogo'}, status=403)
        
        # Ativa modo de jogo
        game_manager = GameSessionManager(sessao)
        resultado = game_manager.ativar_modo_jogo()
        
        # Inicia aguardo de ações
        aguardo_resultado = game_manager.iniciar_aguardo_acoes(resultado['situacao'])
        
        return JsonResponse({
            'sucesso': True,
            'modo_jogo': resultado,
            'aguardo_acoes': aguardo_resultado
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao ativar modo de jogo: {e}")
        return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_processar_acao_jogador(request: HttpRequest) -> JsonResponse:
    """API para processar ação de um jogador"""
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Usuário não autenticado'}, status=401)
    
    try:
        dados = json.loads(request.body)
        sessao_id = dados.get('sessao_id')
        acao = dados.get('acao')
        
        if not acao:
            return JsonResponse({'erro': 'Ação é obrigatória'}, status=400)
        
        sessao = get_object_or_404(SessaoIA, id=sessao_id)
        
        # Verifica se usuário pode participar
        if not (sessao.campanha.organizador == request.user or 
               request.user in sessao.campanha.jogadores.all()):
            return JsonResponse({'erro': 'Sem permissão para participar desta sessão'}, status=403)
        
        # Processa ação do jogador
        game_manager = GameSessionManager(sessao)
        resultado = game_manager.processar_entrada_jogador(acao, request.user.id)
        
        return JsonResponse({
            'sucesso': True,
            'resultado': resultado
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao processar ação: {e}")
        return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET'])
def api_status_sessao(request: HttpRequest, sessao_id: int) -> JsonResponse:
    """API para obter status da sessão de jogo"""
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Usuário não autenticado'}, status=401)
    
    try:
        sessao = get_object_or_404(SessaoIA, id=sessao_id)
        
        # Verifica permissão
        if not (sessao.campanha.organizador == request.user or 
               request.user in sessao.campanha.jogadores.all()):
            return JsonResponse({'erro': 'Sem permissão para acessar esta sessão'}, status=403)
        
        # Obtém status
        game_manager = GameSessionManager(sessao)
        status = game_manager.obter_status_sessao()
        
        return JsonResponse({
            'sucesso': True,
            'status': status
        })
    
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_pausar_sessao(request: HttpRequest) -> JsonResponse:
    """API para pausar sessão de jogo"""
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Usuário não autenticado'}, status=401)
    
    try:
        dados = json.loads(request.body)
        sessao_id = dados.get('sessao_id')
        
        sessao = get_object_or_404(SessaoIA, id=sessao_id)
        
        # Verifica permissão (apenas organizador)
        if sessao.campanha.organizador != request.user:
            return JsonResponse({'erro': 'Apenas o organizador pode pausar a sessão'}, status=403)
        
        game_manager = GameSessionManager(sessao)
        resultado = game_manager.pausar_sessao()
        
        return JsonResponse({
            'sucesso': True,
            'resultado': resultado
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao pausar sessão: {e}")
        return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_retomar_sessao(request: HttpRequest) -> JsonResponse:
    """API para retomar sessão pausada"""
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Usuário não autenticado'}, status=401)
    
    try:
        dados = json.loads(request.body)
        sessao_id = dados.get('sessao_id')
        
        sessao = get_object_or_404(SessaoIA, id=sessao_id)
        
        # Verifica permissão (apenas organizador)
        if sessao.campanha.organizador != request.user:
            return JsonResponse({'erro': 'Apenas o organizador pode retomar a sessão'}, status=403)
        
        game_manager = GameSessionManager(sessao)
        resultado = game_manager.retomar_sessao()
        
        return JsonResponse({
            'sucesso': True,
            'resultado': resultado
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao retomar sessão: {e}")
        return JsonResponse({'erro': str(e)}, status=500)
