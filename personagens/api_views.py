from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from sistema_unificado.models import SistemaJogo, ConteudoSistema

@require_GET
def sistema_conteudo(request, sistema_slug):
    """
    API endpoint que retorna as raças e classes disponíveis para um sistema de jogo.
    Se o slug for 'hibrido', retorna de todos os sistemas.
    """
    try:
        if sistema_slug == 'hibrido':
            racas = ConteudoSistema.objects.filter(tipo='raca', ativo=True).values('id', 'nome', 'descricao').order_by('nome')
            classes = ConteudoSistema.objects.filter(tipo='classe', ativo=True).values('id', 'nome', 'descricao').order_by('nome')
        else:
            sistema = get_object_or_404(SistemaJogo, slug=sistema_slug)
            racas = ConteudoSistema.objects.filter(sistema_jogo=sistema, tipo='raca', ativo=True).values('id', 'nome', 'descricao').order_by('nome')
            classes = ConteudoSistema.objects.filter(sistema_jogo=sistema, tipo='classe', ativo=True).values('id', 'nome', 'descricao').order_by('nome')

        return JsonResponse({
            'racas': list(racas),
            'classes': list(classes)
        })
    except SistemaJogo.DoesNotExist:
        return JsonResponse({'error': f'Sistema com slug "{sistema_slug}" não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Erro interno do servidor', 'detalhes': str(e)}, status=500)

# Manter as outras views como estão...
@require_GET  
def listar_sistemas(request):
    """
    API endpoint que lista todos os sistemas disponíveis.
    """
    try:
        sistemas = SistemaJogo.objects.all().order_by('nome')
        sistemas_data = []
        
        for sistema in sistemas:
            total_racas = ConteudoSistema.objects.filter(sistema_jogo=sistema, tipo='raca', ativo=True).count()
            total_classes = ConteudoSistema.objects.filter(sistema_jogo=sistema, tipo='classe', ativo=True).count()
            
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
    """
    try:
        raca = get_object_or_404(ConteudoSistema, id=raca_id, tipo='raca', ativo=True)
        
        raca_data = {
            'id': raca.id,
            'nome': raca.nome,
            'descricao': raca.descricao or '',
            'dados_originais': raca.dados_originais or {},
            'sistema': {
                'nome': raca.sistema_jogo.nome,
                'slug': raca.sistema_jogo.slug
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
    """
    try:
        classe = get_object_or_404(ConteudoSistema, id=classe_id, tipo='classe', ativo=True)
        
        classe_data = {
            'id': classe.id,
            'nome': classe.nome,
            'descricao': classe.descricao or '',
            'dados_originais': classe.dados_originais or {},
            'sistema': {
                'nome': classe.sistema_jogo.nome,
                'slug': classe.sistema_jogo.slug
            }
        }
        
        return JsonResponse({'classe': classe_data})
        
    except ConteudoSistema.DoesNotExist:
        return JsonResponse({'error': 'Classe não encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)