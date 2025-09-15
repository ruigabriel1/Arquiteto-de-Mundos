"""
Middleware para aplicar regras de autenticação e sessão única por usuário
"""

import re
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import SessionParticipant


class SessionUniqueMiddleware:
    """
    Middleware que aplica a regra: Um usuário só pode estar ativo em uma sessão por vez.
    
    Funcionalidades:
    1. Intercepta tentativas de entrar em sessões
    2. Verifica se usuário já está em outra sessão ativa
    3. Redireciona para tela de seleção de personagem quando necessário
    4. Bloqueia acesso a sessões quando usuário já está ativo em outra
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que devem ser interceptadas
        self.session_url_patterns = [
            re.compile(r'^/ia_gm/sessao/(\d+)/$'),  # Acessar sessão de IA GM
            re.compile(r'^/sessoes/(\d+)/$'),       # Acessar sessão de jogo
            re.compile(r'^/campanhas/(\d+)/sessao/$'),  # Nova sessão de campanha
        ]
        
        # URLs que devem ser excluídas da verificação
        self.excluded_patterns = [
            re.compile(r'^/usuarios/'),           # Sistema de usuários
            re.compile(r'^/admin/'),              # Django admin
            re.compile(r'^/api/'),               # APIs REST
            re.compile(r'^/static/'),            # Arquivos estáticos
            re.compile(r'^/media/'),             # Arquivos de mídia
            re.compile(r'^/selecionar-personagem/'),  # Tela de seleção
        ]
        
        # URLs de API que precisam de verificação especial
        self.api_session_patterns = [
            re.compile(r'^/api/sessoes/(\d+)/iniciar-modo-jogo/$'),
            re.compile(r'^/api/sessoes/(\d+)/processar-turno/$'),
        ]
    
    def __call__(self, request):
        # Processar apenas usuários autenticados
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Verificar se URL deve ser interceptada
        should_check = self._should_check_session(request)
        
        if should_check:
            # Verificar se usuário está tentando acessar sessão
            session_id = self._extract_session_id(request)
            
            if session_id:
                # Aplicar regras de sessão única
                response = self._apply_session_rules(request, session_id)
                if response:
                    return response
        
        # Continuar normalmente
        response = self.get_response(request)
        
        # Pós-processamento se necessário
        return response
    
    def _should_check_session(self, request):
        """Verifica se esta URL precisa de verificação de sessão"""
        path = request.path_info
        
        # Verificar exclusões primeiro
        for pattern in self.excluded_patterns:
            if pattern.match(path):
                return False
        
        # Verificar se é URL de sessão
        for pattern in self.session_url_patterns + self.api_session_patterns:
            if pattern.match(path):
                return True
        
        return False
    
    def _extract_session_id(self, request):
        """Extrai ID da sessão da URL"""
        path = request.path_info
        
        for pattern in self.session_url_patterns + self.api_session_patterns:
            match = pattern.match(path)
            if match:
                return int(match.group(1))
        
        return None
    
    def _apply_session_rules(self, request, session_id):
        """
        Aplica as regras de sessão única.
        Retorna response se deve interceptar, None se pode continuar.
        """
        user = request.user
        
        try:
            # Verificar se usuário já está em alguma sessão
            sessao_ativa = SessionParticipant.get_usuario_sessao_ativa(user)
            
            if sessao_ativa:
                # Se está na mesma sessão, permitir
                if sessao_ativa.sessao.id == session_id:
                    return None
                
                # Está em sessão diferente - bloquear
                return self._handle_session_conflict(request, sessao_ativa, session_id)
            
            else:
                # Não está em nenhuma sessão - verificar se pode entrar nesta
                return self._handle_session_entry(request, session_id)
                
        except Exception as e:
            # Em caso de erro, logar e permitir acesso
            import logging
            logging.error(f'Erro no middleware de sessão: {e}')
            return None
    
    def _handle_session_conflict(self, request, sessao_ativa, session_id_tentativa):
        """Usuário tentando acessar sessão diferente da que está ativo"""
        
        # Se é requisição AJAX/API, retornar JSON
        if self._is_ajax_request(request):
            return JsonResponse({
                'erro': True,
                'codigo': 'sessao_conflito',
                'mensagem': f'Você já está ativo na sessão {sessao_ativa.sessao.id}.',
                'sessao_atual': {
                    'id': sessao_ativa.sessao.id,
                    'nome': getattr(sessao_ativa.sessao, 'nome', f'Sessão {sessao_ativa.sessao.id}'),
                    'personagem': sessao_ativa.personagem.nome if sessao_ativa.personagem else None,
                    'desde': sessao_ativa.data_entrada.isoformat(),
                }
            }, status=409)  # HTTP 409 Conflict
        
        # Para requisições web, redirecionar com mensagem
        messages.warning(
            request,
            f'Você já está ativo na Sessão {sessao_ativa.sessao.id}. '
            f'Saia desta sessão primeiro ou use o link abaixo para retornar.'
        )
        
        # Redirecionar para a sessão atual
        return redirect('ia_gm:sessao', sessao_id=sessao_ativa.sessao.id)
    
    def _handle_session_entry(self, request, session_id):
        """Usuário tentando entrar em nova sessão"""
        
        # Verificar se sessão existe e se usuário pode entrar
        try:
            from ia_gm.models import SessaoIA
            sessao = SessaoIA.objects.get(id=session_id)
            
            # Verificar se usuário pode entrar nesta sessão
            pode_entrar, motivo = SessionParticipant.pode_usuario_entrar_sessao(
                request.user, sessao
            )
            
            if not pode_entrar:
                # Bloquear entrada
                if self._is_ajax_request(request):
                    return JsonResponse({
                        'erro': True,
                        'codigo': 'entrada_bloqueada',
                        'mensagem': motivo
                    }, status=403)
                else:
                    messages.error(request, motivo)
                    return redirect('usuarios:dashboard')
            
            # Verificar se usuário tem personagens disponíveis
            personagens_disponiveis = self._get_personagens_disponiveis(request.user)
            
            if not personagens_disponiveis:
                # Usuário não tem personagens - redirecionar para criação
                messages.info(
                    request,
                    'Você precisa criar um personagem antes de entrar em uma sessão.'
                )
                return redirect('personagens_web:criar')
            
            # Verificar se usuário já selecionou personagem para esta sessão
            participacao = SessionParticipant.objects.filter(
                usuario=request.user,
                sessao=sessao
            ).first()
            
            if not participacao:
                # Primeira vez entrando - redirecionar para seleção de personagem
                return redirect('usuarios:selecionar_personagem', sessao_id=session_id)
            
            elif participacao.estado == 'aguardando':
                # Ainda não selecionou personagem
                return redirect('usuarios:selecionar_personagem', sessao_id=session_id)
            
            # Usuário já configurado - permitir acesso normal
            return None
            
        except Exception as e:
            # Erro ao verificar sessão
            if self._is_ajax_request(request):
                return JsonResponse({
                    'erro': True,
                    'codigo': 'erro_verificacao',
                    'mensagem': 'Erro ao verificar sessão.'
                }, status=500)
            else:
                messages.error(request, 'Erro ao acessar sessão.')
                return redirect('usuarios:dashboard')
    
    def _get_personagens_disponiveis(self, user):
        """Retorna personagens disponíveis do usuário (não em uso)"""
        try:
            from personagens.models import Personagem
            
            # Personagens do usuário que estão ativos
            personagens_usuario = Personagem.objects.filter(
                criador=user,
                ativo=True
            )
            
            # Excluir personagens que estão em uso em outras sessões
            personagens_em_uso = SessionParticipant.objects.filter(
                estado__in=['ativo', 'pausado']
            ).values_list('personagem_id', flat=True)
            
            return personagens_usuario.exclude(id__in=personagens_em_uso)
            
        except:
            return []
    
    def _is_ajax_request(self, request):
        """Verifica se é requisição AJAX"""
        return (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.content_type == 'application/json' or
            'api/' in request.path_info
        )


class AdminContextMiddleware:
    """
    Middleware para gerenciar contexto duplo do administrador.
    
    Administradores podem atuar como:
    1. Gestor - Configurando campanhas, usando Arquiteto IA
    2. Jogador - Participando de sessões com personagem
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que são contexto de gestor (admin não precisa de personagem)
        self.admin_context_patterns = [
            re.compile(r'^/admin/'),
            re.compile(r'^/ia_gm/painel/'),          # Painel do Arquiteto
            re.compile(r'^/campanhas/criar/'),       # Criar campanha
            re.compile(r'^/campanhas/\d+/editar/'), # Editar campanha
            re.compile(r'^/usuarios/dashboard/'),    # Dashboard
            re.compile(r'^/usuarios/configuracoes/'),# Configurações
        ]
    
    def __call__(self, request):
        # Aplicar apenas para staff/admin
        if request.user.is_authenticated and request.user.is_staff:
            self._set_admin_context(request)
        
        return self.get_response(request)
    
    def _set_admin_context(self, request):
        """Define contexto do admin baseado na URL"""
        path = request.path_info
        
        # Verificar se está em contexto de gestor
        is_admin_context = any(
            pattern.match(path) for pattern in self.admin_context_patterns
        )
        
        # Adicionar informação ao request
        request.admin_context = 'gestor' if is_admin_context else 'jogador'
        
        # Adicionar mensagem informativa se necessário
        if hasattr(request, 'user') and not is_admin_context:
            # Admin entrando como jogador - verificar se já tem sessão ativa
            sessao_ativa = SessionParticipant.get_usuario_sessao_ativa(request.user)
            if sessao_ativa and not request.session.get('admin_mode_notified'):
                messages.info(
                    request,
                    'Modo Jogador: Você está participando como jogador. '
                    'Para voltar ao modo gestor, saia desta sessão.'
                )
                request.session['admin_mode_notified'] = True


class SessionActivityMiddleware:
    """
    Middleware para rastrear atividade dos usuários em sessões.
    Atualiza automaticamente timestamp de última atividade.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Atualizar atividade se usuário está em sessão
        if (request.user.is_authenticated and 
            request.method in ['GET', 'POST'] and
            not self._is_static_request(request)):
            
            self._update_session_activity(request)
        
        return response
    
    def _update_session_activity(self, request):
        """Atualiza timestamp de atividade do usuário"""
        try:
            participacao = SessionParticipant.get_usuario_sessao_ativa(request.user)
            if participacao:
                participacao.marcar_atividade()
        except:
            pass  # Falha silenciosa
    
    def _is_static_request(self, request):
        """Verifica se é requisição de arquivo estático"""
        path = request.path_info
        return any(path.startswith(prefix) for prefix in ['/static/', '/media/', '/favicon'])


# Função para adicionar ao settings.py
def get_session_middleware_classes():
    """
    Retorna lista de classes de middleware para adicionar ao MIDDLEWARE no settings.py
    """
    return [
        'usuarios.middleware.SessionUniqueMiddleware',
        'usuarios.middleware.AdminContextMiddleware', 
        'usuarios.middleware.SessionActivityMiddleware',
    ]