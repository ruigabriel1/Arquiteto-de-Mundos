"""
Template tags para navegação e breadcrumbs
"""

from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag(takes_context=True)
def get_page_title(context):
    """Retorna o título da página baseado na URL atual"""
    request = context['request']
    path = request.resolver_match.url_name if request.resolver_match else ''
    namespace = request.resolver_match.namespace if request.resolver_match else ''
    
    # Mapeamento de URLs para títulos
    page_titles = {
        'usuarios:index': 'Início',
        'usuarios:dashboard': 'Dashboard',
        'usuarios:perfil': 'Perfil',
        'usuarios:configuracoes': 'Configurações',
        'usuarios:alterar_senha': 'Alterar Senha',
        'usuarios:login': 'Login',
        'usuarios:cadastro': 'Cadastro',
        
        'campanhas:publicas': 'Campanhas Públicas',
        'campanhas:minhas': 'Minhas Campanhas',
        'campanhas:criar': 'Nova Campanha',
        'campanhas:detalhes': 'Detalhes da Campanha',
        'campanhas:gerenciar': 'Gerenciar Campanha',
        
        'personagens_web:listar': 'Meus Personagens',
        'personagens_web:criar': 'Novo Personagem',
        'personagens_web:detalhes': 'Detalhes do Personagem',
        'personagens_web:editar': 'Editar Personagem',
        
        'ia_gm:painel': 'Arquiteto IA',
        'ia_gm:criar_sessao': 'Nova Sessão IA',
        'ia_gm:sessao': 'Sessão IA GM',
        'ia_gm:historico': 'Histórico da Sessão',
    }
    
    full_name = f"{namespace}:{path}" if namespace else path
    return page_titles.get(full_name, 'Unified Chronicles')

@register.simple_tag(takes_context=True)
def get_breadcrumbs(context):
    """Retorna breadcrumbs baseado na URL atual"""
    request = context['request']
    
    if not request.resolver_match:
        return []
        
    path = request.resolver_match.url_name
    namespace = request.resolver_match.namespace
    kwargs = request.resolver_match.kwargs
    
    breadcrumbs = [
        {'name': 'Início', 'url': reverse('usuarios:index'), 'icon': 'fas fa-home'}
    ]
    
    # Breadcrumbs baseados no namespace
    if namespace == 'campanhas':
        breadcrumbs.append({
            'name': 'Campanhas', 
            'url': reverse('campanhas:publicas'),
            'icon': 'fas fa-users'
        })
        
        if path == 'detalhes' and 'campanha_id' in kwargs:
            breadcrumbs.append({
                'name': 'Detalhes',
                'url': None,
                'icon': 'fas fa-info-circle'
            })
        elif path == 'criar':
            breadcrumbs.append({
                'name': 'Nova Campanha',
                'url': None,
                'icon': 'fas fa-plus'
            })
            
    elif namespace == 'personagens_web':
        breadcrumbs.append({
            'name': 'Personagens',
            'url': reverse('personagens_web:listar'),
            'icon': 'fas fa-user-circle'
        })
        
        if path == 'criar':
            breadcrumbs.append({
                'name': 'Novo Personagem',
                'url': None,
                'icon': 'fas fa-plus'
            })
        elif path == 'detalhes' and 'personagem_id' in kwargs:
            breadcrumbs.append({
                'name': 'Detalhes',
                'url': None,
                'icon': 'fas fa-info-circle'
            })
            
    elif namespace == 'ia_gm':
        breadcrumbs.append({
            'name': 'Arquiteto IA',
            'url': reverse('ia_gm:painel'),
            'icon': 'fas fa-robot'
        })
        
        if path == 'sessao' and 'sessao_id' in kwargs:
            breadcrumbs.append({
                'name': 'Sessão IA GM',
                'url': None,
                'icon': 'fas fa-dice-d20'
            })
        elif path == 'criar_sessao':
            breadcrumbs.append({
                'name': 'Nova Sessão',
                'url': None,
                'icon': 'fas fa-plus'
            })
    
    return breadcrumbs

@register.simple_tag(takes_context=True)
def is_active_nav(context, url_name, namespace=None):
    """Verifica se um item de navegação está ativo"""
    request = context['request']
    
    if not request.resolver_match:
        return False
        
    current_namespace = request.resolver_match.namespace
    current_url = request.resolver_match.url_name
    
    if namespace:
        return current_namespace == namespace
    else:
        full_name = f"{current_namespace}:{current_url}" if current_namespace else current_url
        return full_name == url_name

@register.inclusion_tag('components/breadcrumbs.html', takes_context=True)
def show_breadcrumbs(context):
    """Renderiza breadcrumbs"""
    return {
        'breadcrumbs': get_breadcrumbs(context),
        'current_title': get_page_title(context)
    }