"""
Views web para autenticação de usuários - Interface HTML
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import Usuario
from campanhas.models import Campanha, ParticipacaoCampanha, ConviteCampanha
from personagens.models import Personagem
from ia_gm.models import SessaoIA


def index_view(request):
    """Página inicial - redireciona baseado no status de login"""
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    return render(request, 'usuarios/index.html')


@csrf_protect
def cadastro_view(request):
    """Página de cadastro de novo usuário"""
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    
    if request.method == 'POST':
        # Coleta dados do formulário
        username = request.POST.get('username', '').strip()
        nome_completo = request.POST.get('nome_completo', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        # Validações básicas
        errors = []
        
        if not username:
            errors.append('Nome de usuário é obrigatório.')
        elif len(username) < 3:
            errors.append('Nome de usuário deve ter pelo menos 3 caracteres.')
        elif Usuario.objects.filter(username=username).exists():
            errors.append('Nome de usuário já existe.')
        
        if not nome_completo:
            errors.append('Nome completo é obrigatório.')
        
        if not password:
            errors.append('Senha é obrigatória.')
        elif len(password) < 8:
            errors.append('Senha deve ter pelo menos 8 caracteres.')
        elif password != password_confirm:
            errors.append('Senhas não conferem.')
        
        # Validação de senha com Django
        if not errors:
            try:
                validate_password(password)
            except ValidationError as e:
                errors.extend(e.messages)
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'usuarios/cadastro.html', {
                'username': username,
                'nome_completo': nome_completo
            })
        
        # Criar usuário
        try:
            with transaction.atomic():
                # Gerar email temporário baseado no username
                temp_email = f"{username}@unified-chronicles.local"
                
                user = Usuario.objects.create_user(
                    username=username,
                    email=temp_email,
                    password=password,
                    nome_completo=nome_completo
                )
                
                # Login automático após cadastro
                login(request, user)
                messages.success(request, f'Bem-vindo ao Unified Chronicles, {user.nome_completo}!')
                return redirect('usuarios:dashboard')
                
        except Exception as e:
            messages.error(request, 'Erro ao criar conta. Tente novamente.')
            return render(request, 'usuarios/cadastro.html', {
                'username': username,
                'nome_completo': nome_completo,
                'email': email
            })
    
    return render(request, 'usuarios/cadastro.html')


@csrf_protect
def login_view(request):
    """Página de login"""
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        remember_me = request.POST.get('remember_me') == 'on'
        
        if not username or not password:
            messages.error(request, 'Nome de usuário e senha são obrigatórios.')
            return render(request, 'usuarios/login.html', {'username': username})
        
        # Tentar autenticar
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Configurar tempo de sessão
                if not remember_me:
                    request.session.set_expiry(0)  # Encerra com o navegador
                else:
                    request.session.set_expiry(1209600)  # 2 semanas
                
                # Atualizar última atividade
                user.data_ultima_atividade = timezone.now()
                user.save(update_fields=['data_ultima_atividade'])
                
                messages.success(request, f'Bem-vindo de volta, {user.nome_completo}!')
                
                # Redirecionar para próxima página ou dashboard
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('usuarios:dashboard')
            else:
                messages.error(request, 'Conta desativada. Contate o administrador.')
        else:
            messages.error(request, 'Nome de usuário ou senha incorretos.')
        
        return render(request, 'usuarios/login.html', {'username': username})
    
    return render(request, 'usuarios/login.html')


@require_http_methods(["POST"])
def logout_view(request):
    """Logout do usuário"""
    if request.user.is_authenticated:
        messages.info(request, f'Até logo, {request.user.nome_completo}!')
        logout(request)
    return redirect('usuarios:index')


@login_required
def dashboard_view(request):
    """Dashboard principal do usuário"""
    user = request.user
    
    # Estatísticas básicas
    personagens_count = user.personagens.filter(ativo=True).count()
    campanhas_como_jogador = user.campanhas_participando.filter(
        participacoes__ativo=True
    ).count()
    campanhas_como_mestre = user.campanhas_organizadas.filter(
        estado__in=['ativa', 'planejamento']
    ).count()
    
    # Campanhas recentes (como jogador)
    campanhas_recentes = Campanha.objects.filter(
        participacoes__usuario=user,
        participacoes__ativo=True
    ).select_related('organizador', 'sistema_jogo').order_by('-data_atualizacao')[:5]
    
    # Campanhas organizadas pelo usuário
    campanhas_organizadas = user.campanhas_organizadas.filter(
        estado__in=['ativa', 'planejamento']
    ).select_related('sistema_jogo').order_by('-data_atualizacao')[:5]
    
    # Personagens recentes
    personagens_recentes = user.personagens.filter(
        ativo=True
    ).select_related('sistema_jogo').order_by('-data_atualizacao')[:5]
    
    # Convites pendentes
    convites_pendentes = ConviteCampanha.objects.filter(
        convidado=user,
        estado='pendente'
    ).select_related('campanha', 'convidado_por').order_by('-data_convite')[:5]
    
    # Sessões de IA recentes (se for admin/mestre)
    sessoes_ia_recentes = []
    if user.is_staff or campanhas_como_mestre > 0:
        sessoes_ia_recentes = SessaoIA.objects.filter(
            campanha__organizador=user
        ).select_related('campanha').order_by('-data_criacao')[:3]
    
    context = {
        'user': user,
        'stats': {
            'personagens_count': personagens_count,
            'campanhas_como_jogador': campanhas_como_jogador,
            'campanhas_como_mestre': campanhas_como_mestre,
        },
        'campanhas_recentes': campanhas_recentes,
        'campanhas_organizadas': campanhas_organizadas,
        'personagens_recentes': personagens_recentes,
        'convites_pendentes': convites_pendentes,
        'sessoes_ia_recentes': sessoes_ia_recentes,
    }
    
    return render(request, 'usuarios/dashboard.html', context)


@login_required
def perfil_view(request):
    """Página de perfil do usuário"""
    user = request.user
    
    if request.method == 'POST':
        # Atualizar perfil
        nome_completo = request.POST.get('nome_completo', '').strip()
        email = request.POST.get('email', '').strip()
        bio = request.POST.get('bio', '').strip()
        
        errors = []
        
        if not nome_completo:
            errors.append('Nome completo é obrigatório.')
        
        if not email:
            errors.append('Email é obrigatório.')
        elif Usuario.objects.filter(email=email).exclude(pk=user.pk).exists():
            errors.append('Este email já está em uso.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            user.nome_completo = nome_completo
            user.email = email
            user.bio = bio
            
            # Avatar upload (se enviado)
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
            
            user.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('usuarios:perfil')
    
    return render(request, 'usuarios/perfil.html', {'user': user})


@login_required
def alterar_senha_view(request):
    """Página para alterar senha"""
    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual', '')
        nova_senha = request.POST.get('nova_senha', '')
        confirmar_senha = request.POST.get('confirmar_senha', '')
        
        errors = []
        
        # Verificar senha atual
        if not request.user.check_password(senha_atual):
            errors.append('Senha atual incorreta.')
        
        # Validar nova senha
        if not nova_senha:
            errors.append('Nova senha é obrigatória.')
        elif len(nova_senha) < 8:
            errors.append('Nova senha deve ter pelo menos 8 caracteres.')
        elif nova_senha != confirmar_senha:
            errors.append('Senhas não conferem.')
        
        # Validação com Django
        if not errors:
            try:
                validate_password(nova_senha, request.user)
            except ValidationError as e:
                errors.extend(e.messages)
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            request.user.set_password(nova_senha)
            request.user.save()
            messages.success(request, 'Senha alterada com sucesso! Faça login novamente.')
            logout(request)
            return redirect('usuarios:login')
    
    return render(request, 'usuarios/alterar_senha.html')


@login_required
def configuracoes_view(request):
    """Página de configurações do usuário"""
    user = request.user
    
    if request.method == 'POST':
        # Configurações de jogo
        config_jogo = {
            'notificacoes_email': request.POST.get('notificacoes_email') == 'on',
            'sons_interface': request.POST.get('sons_interface') == 'on',
            'tema_escuro': request.POST.get('tema_escuro') == 'on',
            'auto_save_personagem': request.POST.get('auto_save_personagem') == 'on',
            'mostrar_dicas': request.POST.get('mostrar_dicas') == 'on',
        }
        
        # Configurações de interface
        config_interface = {
            'tamanho_fonte': request.POST.get('tamanho_fonte', 'medium'),
            'contraste': request.POST.get('contraste', 'normal'),
            'reducao_animacoes': request.POST.get('reducao_animacoes') == 'on',
            'idioma': request.POST.get('idioma', 'pt-br'),
        }
        
        user.configuracoes_jogo = config_jogo
        user.configuracoes_interface = config_interface
        user.save(update_fields=['configuracoes_jogo', 'configuracoes_interface'])
        
        messages.success(request, 'Configurações salvas com sucesso!')
        return redirect('usuarios:configuracoes')
    
    return render(request, 'usuarios/configuracoes.html', {'user': user})


@login_required
def usuarios_list_view(request):
    """Página para listar usuários (para convites, etc)"""
    query = request.GET.get('q', '').strip()
    
    usuarios = Usuario.objects.filter(is_active=True)
    
    if query:
        usuarios = usuarios.filter(
            Q(nome_completo__icontains=query) | 
            Q(username__icontains=query)
        )
    
    # Paginação
    paginator = Paginator(usuarios.order_by('nome_completo'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'usuarios/usuarios_list.html', {
        'page_obj': page_obj,
        'query': query
    })


@login_required
def usuario_detail_view(request, user_id):
    """Página de detalhes públicos de um usuário"""
    usuario = get_object_or_404(Usuario, pk=user_id, is_active=True)
    
    # Estatísticas públicas
    personagens_publicos = usuario.personagens.filter(
        ativo=True,
        publico=True  # Assumindo que teremos este campo
    )[:5]
    
    campanhas_participando = Campanha.objects.filter(
        participacoes__usuario=usuario,
        participacoes__ativo=True,
        estado='ativa'
    ).count()
    
    return render(request, 'usuarios/usuario_detail.html', {
        'usuario': usuario,
        'personagens_publicos': personagens_publicos,
        'campanhas_participando': campanhas_participando,
    })