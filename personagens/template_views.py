from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q # Adicionado

from campanhas.models import Campanha, ParticipacaoCampanha # Adicionado ParticipacaoCampanha
from .models import Personagem
from sistema_unificado.models import SistemaJogo, ConteudoSistema
from .forms import PersonagemForm


@login_required
def listar_personagens(request):
    """Lista todos os personagens do usuário atual."""
    personagens = Personagem.objects.filter(usuario=request.user).select_related(
        'campanha', 'sistema_jogo'
    ).order_by('-data_criacao')
    
    context = {
        'personagens': personagens,
        'total_personagens': personagens.count(),
    }
    return render(request, 'personagens/listar_personagens.html', context)


@login_required
def criar_personagem(request):
    """Criar personagem usando formulário simples."""
    if request.method == 'POST':
        form = PersonagemForm(request.POST, request.FILES, user=request.user) # Passar o user aqui também
        print(f"DEBUG: criar_personagem - request.POST: {request.POST}") # Adicionado para depuração
        if form.is_valid():
            print(f"DEBUG: criar_personagem - Formulário é válido.") # Adicionado para depuração
            personagem = form.save(commit=False)
            personagem.usuario = request.user
            personagem.save()
            messages.success(request, f'Personagem "{personagem.nome}" criado com sucesso!')
            return redirect('personagens:listar')
        else:
            print(f"DEBUG: criar_personagem - Erros do Formulário: {form.errors}") # Adicionado para depuração
    else:
        form = PersonagemForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Criar Novo Personagem'
    }
    return render(request, 'personagens/criar_personagem.html', context)


@login_required
def criar_personagem_avancado(request):
    """Criar personagem usando o construtor avançado step-by-step."""
    if request.method == 'POST':
        return processar_personagem_avancado(request)
    
    # Carregar dados necessários para o template
    campanhas_organizadas = Campanha.objects.filter(organizador=request.user)
    campanhas_publicas = Campanha.objects.filter(publica=True)
    campanhas_participadas = Campanha.objects.filter(participacoes__usuario=request.user, participacoes__ativo=True)

    # Combinar e remover duplicatas
    campanhas_disponiveis = (campanhas_organizadas | campanhas_publicas | campanhas_participadas).distinct().order_by('nome')
    print(f"DEBUG: criar_personagem_avancado - Campanhas Disponíveis: {campanhas_disponiveis}") # Adicionado para depuração

    sistemas = SistemaJogo.objects.all().order_by('nome')
    
    context = {
        'campanhas': campanhas_disponiveis, # Alterado para campanhas_disponiveis
        'sistemas': sistemas,
        'title': 'Construtor de Personagem Avançado'
    }
    return render(request, 'personagens/criar_personagem_avancado.html', context)


def processar_personagem_avancado(request):
    """Processa o formulário do construtor avançado."""
    try:
        # Extrair dados do formulário
        nome = request.POST.get('nome', '').strip()
        campanha_id = request.POST.get('campanha')
        print(f"DEBUG: processar_personagem_avancado - Campanha ID recebido: {campanha_id}") # Adicionado para depuração
        sistema_slug = request.POST.get('sistema', '')
        raca_id = request.POST.get('raca')
        classe_id = request.POST.get('classe')
        historia = request.POST.get('historia', '')
        personalidade = request.POST.get('personalidade', '')
        avatar = request.FILES.get('avatar')
        
        # Atributos
        forca = int(request.POST.get('forca', 10))
        destreza = int(request.POST.get('destreza', 10))
        constituicao = int(request.POST.get('constituicao', 10))
        inteligencia = int(request.POST.get('inteligencia', 10))
        sabedoria = int(request.POST.get('sabedoria', 10))
        carisma = int(request.POST.get('carisma', 10))
        
        # Validações
        if not nome:
            messages.error(request, 'Nome do personagem é obrigatório.')
            return redirect('personagens:criar_avancado')
        
        if not campanha_id:
            messages.error(request, 'Selecione uma campanha.')
            return redirect('personagens:criar_avancado')
            
        # Buscar objetos do banco de dados
        # Primeiro, tenta buscar a campanha pelo ID
        campanha = get_object_or_404(Campanha, id=campanha_id)
        print(f"DEBUG: processar_personagem_avancado - Campanha encontrada: {campanha}") # Adicionado para depuração
        
        # Depois, verifica se o usuário tem permissão para usar esta campanha
        # (organizador, pública ou participante ativo)
        if not (campanha.organizador == request.user or 
                campanha.publica or 
                campanha.participacoes.filter(usuario=request.user, ativo=True).exists()):
            messages.error(request, 'Você não tem permissão para criar um personagem nesta campanha.')
            return redirect('personagens:criar_avancado')
        
        # Mapear sistema
        sistema_map = {
            'dnd5e': 'D&D 5e',
            't20': 'Tormenta20', 
            'unified': 'Sistema Unificado'
        }
        sistema_nome = sistema_map.get(sistema_slug)
        if not sistema_nome:
            messages.error(request, 'Sistema de jogo inválido.')
            return redirect('personagens:criar_avancado')
            
        sistema = get_object_or_404(SistemaJogo, nome=sistema_nome)
        
        raca = None
        if raca_id:
            raca = get_object_or_404(
                ConteudoSistema, 
                id=raca_id, 
                sistema_jogo=sistema, 
                tipo='raca',
                ativo=True
            )
        
        classe = None
        if classe_id:
            classe = get_object_or_404(
                ConteudoSistema, 
                id=classe_id, 
                sistema_jogo=sistema, 
                tipo='classe',
                ativo=True
            )
        
        # Criar o personagem
        personagem = Personagem.objects.create(
            nome=nome,
            usuario=request.user,
            campanha=campanha,
            sistema=sistema,
            raca=raca,
            classe=classe,
            forca=forca,
            destreza=destreza,
            constituicao=constituicao,
            inteligencia=inteligencia,
            sabedoria=sabedoria,
            carisma=carisma,
            historia=historia,
            personalidade=personalidade,
            avatar=avatar
        )
        
        # Aplicar bônus raciais e de classe (se implementado)
        aplicar_bonus_personagem(personagem)
        
        messages.success(request, f'Personagem "{personagem.nome}" criado com sucesso!')
        return redirect('personagens:detalhe', pk=personagem.pk)
        
    except Exception as e:
        messages.error(request, f'Erro ao criar personagem: {str(e)}')
        return redirect('personagens:criar_avancado')


def aplicar_bonus_personagem(personagem):
    """Aplica bônus raciais e de classe ao personagem."""
    # Esta função pode ser expandida para aplicar bônus automaticamente
    # baseado nos dados da raça e classe
    if personagem.raca:
        # Aplicar bônus raciais (implementar lógica específica)
        pass
    
    if personagem.classe:
        # Aplicar características de classe (implementar lógica específica)  
        pass
    
    personagem.save()


@login_required
def detalhe_personagem(request, pk):
    """Exibe detalhes completos de um personagem."""
    personagem = get_object_or_404(
        Personagem.objects.select_related(
            'usuario', 'campanha', 'sistema_jogo'
        ),
        pk=pk,
        usuario=request.user
    )
    
    # Calcular modificadores de atributos
    modificadores = {
        'forca': (personagem.forca - 10) // 2,
        'destreza': (personagem.destreza - 10) // 2,
        'constituicao': (personagem.constituicao - 10) // 2,
        'inteligencia': (personagem.inteligencia - 10) // 2,
        'sabedoria': (personagem.sabedoria - 10) // 2,
        'carisma': (personagem.carisma - 10) // 2,
    }
    
    # Calcular pontos de vida máximos (lógica básica)
    pv_max = calcular_pv_maximo(personagem)
    
    context = {
        'personagem': personagem,
        'modificadores': modificadores,
        'pv_max': pv_max,
    }
    return render(request, 'personagens/detalhe_personagem.html', context)


def calcular_pv_maximo(personagem):
    """Calcula pontos de vida máximos baseado na classe e constituição."""
    pv_base = 10  # Valor padrão
    
    if personagem.classe_principal:
        # Mapear classes para PV base (implementar lógica específica do sistema)
        pv_map = {
            'Guerreiro': 10,
            'Bárbaro': 12,
            'Paladino': 10,
            'Ranger': 10,
            'Mago': 6,
            'Feiticeiro': 6,
            'Bruxo': 8,
            'Clérigo': 8,
            'Druida': 8,
            'Ladino': 8,
            'Monge': 8,
            'Bardo': 8,
        }
        pv_base = pv_map.get(personagem.classe_principal.get('nome'), 8)
    
    # Adicionar modificador de constituição
    mod_con = (personagem.constituicao - 10) // 2
    pv_total = pv_base + mod_con
    
    return max(1, pv_total)  # Mínimo de 1 PV


@login_required
def editar_personagem(request, pk):
    """Editar dados de um personagem existente."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = PersonagemForm(request.POST, request.FILES, instance=personagem)
        if form.is_valid():
            form.save()
            messages.success(request, f'Personagem "{personagem.nome}" atualizado com sucesso!')
            return redirect('personagens:detalhe', pk=personagem.pk)
    else:
        form = PersonagemForm(instance=personagem)
    
    context = {
        'form': form,
        'personagem': personagem,
        'title': f'Editar {personagem.nome}'
    }
    return render(request, 'personagens/editar_personagem.html', context)


@login_required
@require_POST
def deletar_personagem(request, pk):
    """Deletar um personagem (com confirmação)."""
    personagem = get_object_or_404(Personagem, pk=pk, usuario=request.user)
    nome = personagem.nome
    personagem.delete()
    messages.success(request, f'Personagem "{nome}" foi deletado.')
    return redirect('personagens:listar')


# Views auxiliares para AJAX
@login_required
def buscar_racas_por_sistema(request):
    """Retorna raças disponíveis para um sistema específico."""
    sistema_id = request.GET.get('sistema_id')
    if not sistema_id:
        return JsonResponse({'error': 'sistema_id é obrigatório'}, status=400)
    
    try:
        racas = ConteudoSistema.objects.filter(
            sistema_jogo_id=sistema_id,
            tipo='raca',
            ativo=True
        ).values('id', 'nome', 'descricao').order_by('nome')
        return JsonResponse({'racas': list(racas)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def buscar_classes_por_sistema(request):
    """Retorna classes disponíveis para um sistema específico."""
    sistema_id = request.GET.get('sistema_id')
    if not sistema_id:
        return JsonResponse({'error': 'sistema_id é obrigatório'}, status=400)
    
    try:
        classes = ConteudoSistema.objects.filter(
            sistema_jogo_id=sistema_id,
            tipo='classe',
            ativo=True
        ).values('id', 'nome', 'descricao').order_by('nome')
        return JsonResponse({'classes': list(classes)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)