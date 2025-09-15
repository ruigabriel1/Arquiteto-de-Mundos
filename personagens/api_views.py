from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import json

from sistema_unificado.models import SistemaJogo, ConteudoSistema


@require_GET
def sistema_conteudo(request, sistema_slug):
    """
    API endpoint que retorna as raças e classes disponíveis para um sistema específico.
    
    Args:
        sistema_slug (str): Slug do sistema (dnd5e, t20, unified)
    
    Returns:
        JsonResponse: JSON com raças e classes do sistema
    """
    # Mapear slugs para códigos de sistemas
    sistema_map = {
        'dnd5e': 'dnd5e',
        't20': 't20',
        'unified': 'unified'
    }
    
    if sistema_slug not in sistema_map:
        return JsonResponse({
            'error': 'Sistema inválido',
            'sistemas_disponíveis': list(sistema_map.keys())
        }, status=400)
    
    try:
        # Buscar o sistema no banco de dados
        sistema = get_object_or_404(SistemaJogo, codigo=sistema_map[sistema_slug])
        
        # Buscar raças do sistema
        racas = ConteudoSistema.objects.filter(
            sistema_jogo=sistema, 
            tipo='raca', 
            ativo=True
        ).order_by('nome')
        racas_data = []
        
        for raca in racas:
            # Processar dados originais
            dados_originais = raca.dados_originais or {}
            
            raca_data = {
                'id': raca.id,
                'nome': raca.nome,
                'descricao': raca.descricao or '',
                'bonus': dados_originais.get('bonus_atributos', {}),
                'tracos': dados_originais.get('tracos', []),
                'dados_originais': dados_originais,
                'sistema': sistema.nome
            }
            racas_data.append(raca_data)
        
        # Buscar classes do sistema
        classes = ConteudoSistema.objects.filter(
            sistema_jogo=sistema, 
            tipo='classe', 
            ativo=True
        ).order_by('nome')
        classes_data = []
        
        for classe in classes:
            # Processar dados originais
            dados_originais = classe.dados_originais or {}
            
            classe_data = {
                'id': classe.id,
                'nome': classe.nome,
                'descricao': classe.descricao or '',
                'pv': dados_originais.get('pontos_vida', dados_originais.get('pv', None)),
                'proficiencias': dados_originais.get('proficiencias', []),
                'caracteristicas': dados_originais.get('caracteristicas', []),
                'dados_originais': dados_originais,
                'sistema': sistema.nome
            }
            classes_data.append(classe_data)
        
        return JsonResponse({
            'sistema': {
                'slug': sistema_slug,
                'nome': sistema.nome,
                'descricao': sistema.descricao or ''
            },
            'races': racas_data,
            'classes': classes_data,
            'total_racas': len(racas_data),
            'total_classes': len(classes_data)
        })
        
    except SistemaJogo.DoesNotExist:
        return JsonResponse({
            'error': f'Sistema com código "{sistema_map[sistema_slug]}" não encontrado no banco de dados',
            'sugestao': 'Execute o comando populate_sistemas_completo para carregar os dados'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'error': 'Erro interno do servidor',
            'detalhes': str(e)
        }, status=500)


@require_GET  
def listar_sistemas(request):
    """
    API endpoint que lista todos os sistemas disponíveis.
    
    Returns:
        JsonResponse: Lista de sistemas com suas informações básicas
    """
    try:
        sistemas = SistemaJogo.objects.all().order_by('nome')
        sistemas_data = []
        
        for sistema in sistemas:
            # Contar raças e classes
            total_racas = ConteudoSistema.objects.filter(
                sistema_jogo=sistema, tipo='raca', ativo=True
            ).count()
            total_classes = ConteudoSistema.objects.filter(
                sistema_jogo=sistema, tipo='classe', ativo=True
            ).count()
            
            sistema_data = {
                'id': sistema.id,
                'nome': sistema.nome,
                'slug': sistema.codigo,  # Usar código como slug
                'descricao': sistema.descricao or '',
                'total_racas': total_racas,
                'total_classes': total_classes,
                'ativo': sistema.ativo
            }
            sistemas_data.append(sistema_data)
        
        return JsonResponse({
            'sistemas': sistemas_data,
            'total': len(sistemas_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'Erro ao carregar sistemas',
            'detalhes': str(e)
        }, status=500)


@require_GET
def detalhes_raca(request, raca_id):
    """
    API endpoint que retorna detalhes completos de uma raça específica.
    
    Args:
        raca_id (int): ID da raça
        
    Returns:
        JsonResponse: Detalhes completos da raça
    """
    try:
        raca = get_object_or_404(
            ConteudoSistema,
            id=raca_id,
            tipo='raca',
            ativo=True
        )
        
        # Processar dados originais
        dados_originais = raca.dados_originais or {}
        dados_convertidos = raca.dados_convertidos or {}
        
        raca_data = {
            'id': raca.id,
            'nome': raca.nome,
            'descricao': raca.descricao or '',
            'bonus_atributos': dados_originais.get('bonus_atributos', {}),
            'tracos': dados_originais.get('tracos', []),
            'dados_originais': dados_originais,
            'dados_convertidos': dados_convertidos,
            'tags': raca.tags or [],
            'sistema': {
                'id': raca.sistema_jogo.id,
                'nome': raca.sistema_jogo.nome,
                'codigo': raca.sistema_jogo.codigo
            }
        }
        
        return JsonResponse({'raca': raca_data})
        
    except ConteudoSistema.DoesNotExist:
        return JsonResponse({'error': 'Raça não encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def detalhes_classe(request, classe_id):
    """
    API endpoint que retorna detalhes completos de uma classe específica.
    
    Args:
        classe_id (int): ID da classe
        
    Returns:
        JsonResponse: Detalhes completos da classe
    """
    try:
        classe = get_object_or_404(
            ConteudoSistema,
            id=classe_id,
            tipo='classe',
            ativo=True
        )
        
        # Processar dados originais
        dados_originais = classe.dados_originais or {}
        dados_convertidos = classe.dados_convertidos or {}
        
        classe_data = {
            'id': classe.id,
            'nome': classe.nome,
            'descricao': classe.descricao or '',
            'pontos_vida': dados_originais.get('pontos_vida', dados_originais.get('pv', None)),
            'proficiencias': dados_originais.get('proficiencias', []),
            'caracteristicas': dados_originais.get('caracteristicas', []),
            'dados_originais': dados_originais,
            'dados_convertidos': dados_convertidos,
            'tags': classe.tags or [],
            'sistema': {
                'id': classe.sistema_jogo.id,
                'nome': classe.sistema_jogo.nome,
                'codigo': classe.sistema_jogo.codigo
            }
        }
        
        return JsonResponse({'classe': classe_data})
        
    except ConteudoSistema.DoesNotExist:
        return JsonResponse({'error': 'Classe não encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
