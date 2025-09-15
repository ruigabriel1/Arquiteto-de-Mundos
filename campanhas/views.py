"""
Views para gerenciamento de campanhas e participações
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.translation import gettext as _
from django.utils import timezone

from .models import Campanha, CampaignParticipant
from .utils import (
    CampaignParticipationManager, 
    get_campanhas_publicas,
    get_personagens_compativeis_campanha,
    get_campanhas_organizadas_pelo_usuario
)
from .notifications import (
    notify_participation_approved,
    notify_participation_rejected,
    notify_new_participant_request,
    notify_participant_left,
    notify_campaign_created
)
from personagens.models import Personagem


@login_required
def campanhas_publicas_view(request):
    """Lista todas as campanhas públicas disponíveis para participação"""
    
    # Filtros de busca
    search = request.GET.get('search', '').strip()
    sistema_jogo = request.GET.get('sistema', '')
    estado = request.GET.get('estado', '')
    
    # Obter campanhas públicas
    campanhas = get_campanhas_publicas(usuario=request.user)
    
    # Aplicar filtros
    if search:
        campanhas = campanhas.filter(
            Q(nome__icontains=search) | 
            Q(descricao__icontains=search) |
            Q(organizador__nome_completo__icontains=search)
        )
    
    if sistema_jogo:
        campanhas = campanhas.filter(sistema_jogo_id=sistema_jogo)
    
    if estado:
        campanhas = campanhas.filter(estado=estado)
    
    # Paginação
    paginator = Paginator(campanhas, 12)  # 12 campanhas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Adicionar status de participação para cada campanha
    for campanha in page_obj:
        status = CampaignParticipationManager.get_status_participacao(
            request.user, campanha
        )
        campanha.status_participacao = status
        
        pode_participar = CampaignParticipationManager.pode_usuario_participar(
            request.user, campanha
        )
        campanha.pode_participar_info = pode_participar
    
    # Opções para filtros
    from sistema_unificado.models import SistemaJogo
    sistemas = SistemaJogo.objects.filter(ativo=True)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'sistema_selecionado': sistema_jogo,
        'estado_selecionado': estado,
        'sistemas': sistemas,
        'estados': Campanha.ESTADOS_CAMPANHA,
    }
    
    return render(request, 'campanhas/campanhas_publicas.html', context)


@login_required
def detalhes_campanha_view(request, campanha_id):
    """Visualizar detalhes de uma campanha específica"""
    
    campanha = get_object_or_404(Campanha, id=campanha_id)
    
    # Status de participação do usuário
    status_participacao = CampaignParticipationManager.get_status_participacao(
        request.user, campanha
    )
    
    pode_participar = CampaignParticipationManager.pode_usuario_participar(
        request.user, campanha
    )
    
    # Participantes ativos
    participantes = CampaignParticipationManager.get_participantes_da_campanha(
        campanha, status_filter=['ativo']
    )
    
    # Personagens compatíveis do usuário (se pode participar)
    personagens_compativeis = []
    if pode_participar['pode_participar'] or status_participacao['pode_definir_personagem']:
        personagens_compativeis = get_personagens_compativeis_campanha(
            request.user, campanha
        )
    
    # Informações sobre sessões de IA GM
    sessoes_ia = []
    sessao_ativa = None
    try:
        # Importa o modelo de sessão IA
        from ia_gm.models import SessaoIA
        
        # Busca todas as sessões desta campanha
        sessoes_ia = SessaoIA.objects.filter(
            campanha=campanha
        ).order_by('-data_atualizacao')[:5]  # Últimas 5 sessões
        
        # Busca sessão ativa
        sessao_ativa = SessaoIA.objects.filter(
            campanha=campanha,
            ativa=True
        ).first()
        
    except ImportError:
        # Se o módulo IA GM não estiver disponível
        pass
    except Exception as e:
        # Log do erro mas não quebra a página
        import logging
        logging.getLogger(__name__).warning(f"Erro ao buscar sessões IA: {e}")
    
    context = {
        'campanha': campanha,
        'status_participacao': status_participacao,
        'pode_participar': pode_participar,
        'participantes': participantes,
        'personagens_compativeis': personagens_compativeis,
        'eh_organizador': campanha.organizador == request.user,
        'sessoes_ia': sessoes_ia,
        'sessao_ativa': sessao_ativa,
    }
    
    return render(request, 'campanhas/detalhes_campanha.html', context)


@login_required
@require_POST
def participar_campanha_view(request, campanha_id):
    """Inscrever-se em uma campanha"""
    
    campanha = get_object_or_404(Campanha, id=campanha_id)
    personagem_id = request.POST.get('personagem_id')
    
    try:
        # Obter personagem se especificado
        personagem = None
        if personagem_id:
            personagem = get_object_or_404(
                Personagem, 
                id=personagem_id, 
                usuario=request.user,
                ativo=True
            )
        
        # Tentar participar da campanha
        participacao = CampaignParticipationManager.participar_de_campanha(
            request.user, campanha, personagem
        )
        
        # Notificar organizador sobre nova solicitação
        notify_new_participant_request(campanha, participacao)
        
        if participacao.status == 'aguardando':
            messages.success(
                request, 
                _('Inscrição enviada! Aguarde a aprovação do organizador.')
            )
        elif participacao.status == 'pendente':
            messages.success(
                request, 
                _('Inscrição realizada! Agora você precisa definir um personagem.')
            )
        
        return redirect('campanhas:detalhes', campanha_id=campanha.id)
        
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect('campanhas:detalhes', campanha_id=campanha.id)


@login_required
@require_POST
def definir_personagem_view(request, campanha_id):
    """Definir personagem para uma participação pendente"""
    
    campanha = get_object_or_404(Campanha, id=campanha_id)
    personagem_id = request.POST.get('personagem_id')
    
    if not personagem_id:
        messages.error(request, _('Selecione um personagem.'))
        return redirect('campanhas:detalhes', campanha_id=campanha.id)
    
    try:
        # Obter personagem
        personagem = get_object_or_404(
            Personagem, 
            id=personagem_id, 
            usuario=request.user,
            ativo=True
        )
        
        # Obter participação do usuário
        participacao = CampaignParticipant.objects.get(
            usuario=request.user,
            campanha=campanha,
            status__in=['pendente', 'aguardando']
        )
        
        # Definir personagem
        CampaignParticipationManager.definir_personagem(
            participacao.id, personagem
        )
        
        messages.success(
            request, 
            _('Personagem definido! Aguarde a aprovação do organizador.')
        )
        
    except (CampaignParticipant.DoesNotExist, ValidationError) as e:
        messages.error(request, str(e))
    
    return redirect('campanhas:detalhes', campanha_id=campanha.id)


@login_required
@require_POST
def sair_campanha_view(request, campanha_id):
    """Sair de uma campanha"""
    
    campanha = get_object_or_404(Campanha, id=campanha_id)
    motivo = request.POST.get('motivo', '')
    
    sucesso = CampaignParticipationManager.sair_da_campanha(
        request.user, campanha, motivo
    )
    
    if sucesso:
        messages.success(request, _('Você saiu da campanha.'))
    else:
        messages.error(request, _('Você não está participando desta campanha.'))
    
    return redirect('campanhas:detalhes', campanha_id=campanha.id)


@login_required
def minhas_campanhas_view(request):
    """Lista campanhas do usuário (participando + organizando)"""
    
    # Campanhas onde está participando
    participacoes = CampaignParticipationManager.get_campanhas_do_usuario(
        request.user
    ).select_related('campanha__sistema_jogo', 'campanha__organizador')
    
    # Campanhas organizadas pelo usuário
    campanhas_organizadas = get_campanhas_organizadas_pelo_usuario(request.user)
    
    context = {
        'participacoes': participacoes,
        'campanhas_organizadas': campanhas_organizadas,
    }
    
    return render(request, 'campanhas/minhas_campanhas.html', context)


@login_required
def gerenciar_campanha_view(request, campanha_id):
    """Gerenciar uma campanha (apenas organizador)"""
    
    campanha = get_object_or_404(
        Campanha, 
        id=campanha_id, 
        organizador=request.user
    )
    
    # Participações por status
    participacoes_aguardando = CampaignParticipationManager.get_participantes_da_campanha(
        campanha, status_filter=['aguardando']
    )
    
    participacoes_ativas = CampaignParticipationManager.get_participantes_da_campanha(
        campanha, status_filter=['ativo']
    )
    
    participacoes_pendentes = CampaignParticipationManager.get_participantes_da_campanha(
        campanha, status_filter=['pendente']
    )
    
    context = {
        'campanha': campanha,
        'participacoes_aguardando': participacoes_aguardando,
        'participacoes_ativas': participacoes_ativas,
        'participacoes_pendentes': participacoes_pendentes,
    }
    
    return render(request, 'campanhas/gerenciar_campanha.html', context)


@login_required
@require_POST
def aprovar_participacao_view(request, participacao_id):
    """Aprovar uma participação (apenas organizador)"""
    
    try:
        participacao = CampaignParticipationManager.aprovar_participacao(
            participacao_id, request.user
        )
        
        # Notificar usuário sobre aprovação
        notify_participation_approved(participacao)
        
        messages.success(
            request, 
            _('Participação de {} aprovada!').format(participacao.usuario.nome_completo)
        )
        
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('campanhas:gerenciar', campanha_id=request.POST.get('campanha_id'))


@login_required
@require_POST
def rejeitar_participacao_view(request, participacao_id):
    """Rejeitar uma participação (apenas organizador)"""
    
    try:
        participacao = get_object_or_404(
            CampaignParticipant, 
            id=participacao_id, 
            campanha__organizador=request.user,
            status__in=['aguardando', 'pendente']
        )
        
        motivo = request.POST.get('motivo_rejeicao', '')
        
        # Rejeitar participação
        participacao.status = 'rejeitado'
        participacao.motivo_saida = motivo
        participacao.data_saida = timezone.now()
        participacao.save()
        
        # Notificar usuário sobre rejeição
        notify_participation_rejected(participacao, motivo)
        
        messages.success(
            request, 
            _('Participação de {} rejeitada.').format(participacao.usuario.nome_completo)
        )
        
    except Exception as e:
        messages.error(request, f'Erro ao rejeitar participação: {str(e)}')
    
    return redirect('campanhas:gerenciar', campanha_id=request.POST.get('campanha_id'))


@login_required
@require_POST
def remover_participante_view(request, participacao_id):
    """Remover um participante ativo (apenas organizador)"""
    
    try:
        participacao = get_object_or_404(
            CampaignParticipant, 
            id=participacao_id, 
            campanha__organizador=request.user,
            status='ativo'
        )
        
        motivo = request.POST.get('motivo_remocao', '')
        
        # Remover participante
        sucesso = CampaignParticipationManager.sair_da_campanha(
            participacao.usuario, 
            participacao.campanha, 
            motivo, 
            removido_por_organizador=True
        )
        
        if sucesso:
            # Notificar organizador sobre remoção
            notify_participant_left(participacao.campanha, participacao.usuario, motivo)
            
            messages.success(
                request, 
                _('Participante {} removido da campanha.').format(participacao.usuario.nome_completo)
            )
        else:
            messages.error(request, _('Erro ao remover participante.'))
        
    except Exception as e:
        messages.error(request, f'Erro ao remover participante: {str(e)}')
    
    return redirect('campanhas:gerenciar', campanha_id=request.POST.get('campanha_id'))


@login_required
def criar_campanha_view(request):
    """Criar uma nova campanha"""
    
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            nome = request.POST.get('nome', '').strip()
            descricao = request.POST.get('descricao', '').strip()
            sistema_jogo_id = request.POST.get('sistema_jogo')
            max_jogadores = request.POST.get('max_jogadores', '')
            data_inicio = request.POST.get('data_inicio', '')
            # regras_especiais = request.POST.get('regras_especiais', '').strip()  # Campo removido do modelo
            publica = request.POST.get('publica') == 'on'
            
            # Validações básicas
            if not nome:
                messages.error(request, _('O nome da campanha é obrigatório.'))
                return redirect('campanhas:criar')
            
            if not descricao:
                messages.error(request, _('A descrição da campanha é obrigatória.'))
                return redirect('campanhas:criar')
            
            if not sistema_jogo_id:
                messages.error(request, _('O sistema de jogo é obrigatório.'))
                return redirect('campanhas:criar')
            
            # Obter sistema de jogo
            from sistema_unificado.models import SistemaJogo
            try:
                sistema_jogo = SistemaJogo.objects.get(id=sistema_jogo_id, ativo=True)
            except SistemaJogo.DoesNotExist:
                messages.error(request, _('Sistema de jogo inválido.'))
                return redirect('campanhas:criar')
            
            # Processar max_jogadores
            max_jogadores_int = None
            if max_jogadores and max_jogadores.strip():
                try:
                    max_jogadores_int = int(max_jogadores)
                    if max_jogadores_int <= 0:
                        messages.error(request, _('O número máximo de jogadores deve ser maior que zero.'))
                        return redirect('campanhas:criar')
                except ValueError:
                    messages.error(request, _('Número máximo de jogadores deve ser um número válido.'))
                    return redirect('campanhas:criar')
            
            # Processar data_inicio - permitir início imediato
            data_inicio_obj = None
            if data_inicio:
                try:
                    from datetime import datetime
                    data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, _('Data de início inválida.'))
                    return redirect('campanhas:criar')
            else:
                # Se não especificar data, começar imediatamente
                data_inicio_obj = timezone.now().date()
            
            # Criar campanha
            campanha = Campanha.objects.create(
                nome=nome,
                descricao=descricao,
                organizador=request.user,
                sistema_jogo=sistema_jogo,
                max_jogadores=max_jogadores_int if max_jogadores_int else 6,
                data_inicio=data_inicio_obj,
                # publica=publica,  # Campo não existe no modelo atual
                estado='ativa' if data_inicio_obj == timezone.now().date() else 'planejamento'  # Ativar imediatamente se começar hoje
            )
            
            # Notificar criação da campanha
            notify_campaign_created(campanha)
            
            messages.success(request, _('Campanha "{}" criada com sucesso!').format(campanha.nome))
            return redirect('campanhas:detalhes', campanha_id=campanha.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar campanha: {str(e)}')
            return redirect('campanhas:criar')
    
    # GET - mostrar formulário
    from sistema_unificado.models import SistemaJogo
    sistemas = SistemaJogo.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'sistemas': sistemas,
    }
    
    return render(request, 'campanhas/criar_campanha.html', context)


@login_required
def ajax_personagens_compativeis(request, campanha_id):
    """Retorna personagens compatíveis via AJAX"""
    
    campanha = get_object_or_404(Campanha, id=campanha_id)
    personagens = get_personagens_compativeis_campanha(request.user, campanha)
    
    data = {
        'personagens': [
            {
                'id': p.id,
                'nome': p.nome,
                'nivel': p.nivel,
                'sistema': p.sistema_jogo.nome,
                'classes': [c.get('nome', 'N/A') for c in p.classes] if p.classes else [],
            }
            for p in personagens
        ]
    }
    
    return JsonResponse(data)
