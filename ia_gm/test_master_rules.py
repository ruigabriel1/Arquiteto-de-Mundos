"""
Script de testes para validar o comportamento do Mestre IA
Testa as regras fundamentais implementadas
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model

# Setup do Django para testes standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_chronicles.settings')
django.setup()

from campanhas.models import Campanha
from personagens.models import Personagem
from ia_gm.models import SessaoIA, EstiloNarrativo
from ia_gm.master_rules import (
    MasterRulesEngine, ModoOperacao, FaseCicloJogo,
    CicloJogoValidator, obter_modo_operacao_sessao,
    aplicar_regras_ao_prompt
)
from ia_gm.game_session_manager import GameSessionManager


User = get_user_model()


def criar_dados_teste():
    """Cria dados básicos para testes"""
    print("🔧 Criando dados de teste...")
    
    # Usuário organizador
    try:
        organizador = User.objects.get(username='test_master')
    except User.DoesNotExist:
        organizador = User.objects.create_user(
            username='test_master',
            email='master@test.com',
            password='testpass123'
        )
    
    # Usuários jogadores
    jogadores = []
    for i in range(3):
        try:
            jogador = User.objects.get(username=f'jogador{i+1}')
        except User.DoesNotExist:
            jogador = User.objects.create_user(
                username=f'jogador{i+1}',
                email=f'jogador{i+1}@test.com',
                password='testpass123'
            )
        jogadores.append(jogador)
    
    # Importa e obtém sistema de jogo padrão
    from sistema_unificado.models import SistemaJogo
    
    # Tenta criar/obter sistema D&D 5E para testes
    sistema_jogo, _ = SistemaJogo.objects.get_or_create(
        nome='D&D 5E',
        defaults={
            'descricao': 'Sistema de teste para validar regras do Mestre IA',
            'ativo': True
        }
    )
    
    # Campanha de teste
    campanha, created = Campanha.objects.get_or_create(
        nome='Campanha de Teste - Mestre IA',
        defaults={
            'descricao': 'Campanha para testar as regras do Mestre IA',
            'sistema_jogo': sistema_jogo,
            'organizador': organizador
        }
    )
    
    if created:
        campanha.jogadores.set(jogadores)
    
    # Personagens de teste
    personagens = []
    nomes_personagens = ['Thorin', 'Elara', 'Marcus']
    classes_dados = [
        {'nome': 'Guerreiro', 'nivel': 1, 'origem': 'dnd5e'},
        {'nome': 'Mago', 'nivel': 1, 'origem': 'dnd5e'},
        {'nome': 'Ladino', 'nivel': 1, 'origem': 'dnd5e'}
    ]
    racas_dados = [
        {'nome': 'Anão', 'origem': 'dnd5e'},
        {'nome': 'Elfo', 'origem': 'dnd5e'},
        {'nome': 'Humano', 'origem': 'dnd5e'}
    ]
    
    for i, (nome, classe_data, raca_data, jogador) in enumerate(zip(nomes_personagens, classes_dados, racas_dados, jogadores)):
        personagem, created = Personagem.objects.get_or_create(
            nome=nome,
            campanha=campanha,
            defaults={
                'sistema_jogo': sistema_jogo,
                'classes': [classe_data],
                'raca': raca_data,
                'nivel': 1,
                'historia': f'História de {nome}, um {raca_data["nome"]} {classe_data["nome"]}',
                'usuario': jogador
            }
        )
        personagens.append(personagem)
    
    # Sessão de teste
    sessao, created = SessaoIA.objects.get_or_create(
        campanha=campanha,
        nome='Teste das Regras do Mestre',
        defaults={
            'descricao': 'Sessão para validar regras comportamentais',
            'estilo_narrativo': EstiloNarrativo.EPICO,
            'criatividade_nivel': 7,
            'dificuldade_nivel': 5,
            'ativa': False
        }
    )
    
    print(f"✅ Dados criados - Campanha: {campanha.nome}, Sessão: {sessao.nome}")
    return organizador, jogadores, campanha, personagens, sessao


def testar_modo_operacao():
    """Testa identificação e comportamento dos modos de operação"""
    print("\n🧪 TESTE: Modos de Operação")
    
    _, _, _, _, sessao = criar_dados_teste()
    
    # Teste 1: Sessão inativa deve estar em CONFIGURACAO
    modo = obter_modo_operacao_sessao(sessao)
    assert modo == ModoOperacao.CONFIGURACAO, f"Esperado CONFIGURACAO, obtido {modo}"
    print("✅ Sessão inativa corretamente identificada como CONFIGURACAO")
    
    # Teste 2: Validação de comandos em modo configuração
    validacao = MasterRulesEngine.validar_entrada_comando("/npc Aldeão Misterioso", ModoOperacao.CONFIGURACAO)
    assert validacao['valida'] == True, "Comando /npc deve ser válido em configuração"
    assert validacao['tipo'] == 'comando_configuracao', "Deve ser identificado como comando de configuração"
    print("✅ Comandos de barra validados corretamente em CONFIGURACAO")
    
    # Teste 3: Rejeição de comandos de barra em modo jogo
    validacao = MasterRulesEngine.validar_entrada_comando("/npc teste", ModoOperacao.JOGO)
    assert validacao['valida'] == False, "Comandos de barra devem ser rejeitados em modo JOGO"
    print("✅ Comandos de barra corretamente rejeitados em JOGO")
    
    # Teste 4: Geração de prompts comportamentais
    prompt_config = MasterRulesEngine.gerar_prompt_comportamental(ModoOperacao.CONFIGURACAO)
    assert "MODO DE CONFIGURAÇÃO ATIVO" in prompt_config, "Prompt deve indicar modo configuração"
    assert "/ambiente" in prompt_config, "Deve listar comandos disponíveis"
    print("✅ Prompt de CONFIGURACAO gerado corretamente")
    
    prompt_jogo = MasterRulesEngine.gerar_prompt_comportamental(ModoOperacao.JOGO)
    assert "MODO DE JOGO ATIVO" in prompt_jogo, "Prompt deve indicar modo jogo"
    assert "CICLO OBRIGATÓRIO" in prompt_jogo, "Deve mencionar ciclo de jogo"
    assert "JAMAIS" in prompt_jogo, "Deve conter regras invioláveis"
    print("✅ Prompt de JOGO gerado corretamente")


def testar_ciclo_jogo():
    """Testa validação do ciclo de jogo"""
    print("\n🧪 TESTE: Ciclo de Jogo")
    
    # Teste 1: Validação de fase DESCREVENDO_SITUACAO
    resposta_com_pergunta = "Os heróis estão na taverna. O que vocês fazem?"
    validacao = CicloJogoValidator.validar_fase_atual(
        FaseCicloJogo.DESCREVENDO_SITUACAO,
        resposta_com_pergunta,
        []
    )
    assert validacao['valida'] == True, "Descrição terminada com pergunta deve ser válida"
    print("✅ Fase DESCREVENDO_SITUACAO validada corretamente")
    
    resposta_sem_pergunta = "Os heróis estão na taverna."
    validacao = CicloJogoValidator.validar_fase_atual(
        FaseCicloJogo.DESCREVENDO_SITUACAO,
        resposta_sem_pergunta,
        []
    )
    assert validacao['valida'] == False, "Descrição sem pergunta deve ser inválida"
    print("✅ Descrição sem pergunta corretamente rejeitada")
    
    # Teste 2: Validação de fase AGUARDANDO_TODAS_ACOES
    acoes_pendentes = ["Thorin", "Elara"]
    validacao = CicloJogoValidator.validar_fase_atual(
        FaseCicloJogo.AGUARDANDO_TODAS_ACOES,
        "",
        acoes_pendentes
    )
    assert validacao['valida'] == True, "Deve aguardar enquanto há ações pendentes"
    assert "Thorin, Elara" in validacao['feedback'], "Deve listar personagens pendentes"
    print("✅ Aguardo de ações validado corretamente")
    
    # Teste 3: Validação de fase PROCESSANDO_CONSEQUENCIAS
    validacao = CicloJogoValidator.validar_fase_atual(
        FaseCicloJogo.PROCESSANDO_CONSEQUENCIAS,
        "",
        []
    )
    assert validacao['valida'] == True, "Sem ações pendentes deve permitir processamento"
    print("✅ Fase de processamento validada corretamente")


def testar_game_session_manager():
    """Testa integração com GameSessionManager"""
    print("\n🧪 TESTE: GameSessionManager Integrado")
    
    _, jogadores, _, personagens, sessao = criar_dados_teste()
    
    # Teste 1: Criação do manager
    manager = GameSessionManager(sessao)
    assert manager.sessao == sessao, "Manager deve estar vinculado à sessão correta"
    print("✅ GameSessionManager criado corretamente")
    
    # Teste 2: Estado inicial
    estado = manager.estado_sessao
    # Como a sessão está inativa, deve estar em ENCERRADA ou CONFIGURACAO
    print(f"✅ Estado inicial: {estado}")
    
    # Teste 3: Apenas validar estrutura sem chamar IA real
    # manager.ativar_modo_jogo() chamaria IA, então testamos só a estrutura
    
    # Simula ativação para testar estrutura
    from django.core.cache import cache
    cache.set(f"game_session_{sessao.id}_estado", "ativa", 3600)
    
    # Testa obtenção de personagens
    personagens_ativos = manager._obter_personagens_ativos()
    assert len(personagens_ativos) == 3, "Deve obter 3 personagens de teste"
    print(f"✅ {len(personagens_ativos)} personagens ativos identificados")
    
    # Teste 4: Status da sessão
    status = manager.obter_status_sessao()
    print(f"✅ Status obtido: {status}")
    
    # Limpa cache
    cache.delete(f"game_session_{sessao.id}_estado")


def testar_aplicacao_regras():
    """Testa aplicação das regras aos prompts"""
    print("\n🧪 TESTE: Aplicação de Regras aos Prompts")
    
    _, _, _, _, sessao = criar_dados_teste()
    
    prompt_base = "Você é uma IA que ajuda jogadores de RPG."
    contexto = "Teste de integração das regras"
    
    # Teste com sessão inativa (configuração)
    prompt_integrado = aplicar_regras_ao_prompt(prompt_base, sessao, contexto)
    assert "CONFIGURAÇÃO ATIVO" in prompt_integrado, "Deve aplicar regras de configuração"
    assert "/ambiente" in prompt_integrado, "Deve listar comandos de configuração"
    print("✅ Regras de CONFIGURACAO aplicadas ao prompt")
    
    # Ativa sessão para testar modo JOGO
    sessao.ativa = True
    sessao.save()
    
    # Simula estado de jogo ativo
    from django.core.cache import cache
    cache.set(f"game_session_{sessao.id}_estado", "ativa", 3600)
    
    prompt_jogo = aplicar_regras_ao_prompt(prompt_base, sessao, contexto)
    assert "MODO DE JOGO ATIVO" in prompt_jogo, "Deve aplicar regras de jogo"
    assert "CICLO OBRIGATÓRIO" in prompt_jogo, "Deve mencionar ciclo de jogo"
    assert "JAMAIS" in prompt_jogo, "Deve conter regras inviolááveis"
    assert "personagens" in prompt_jogo.lower(), "Deve mencionar como se dirigir aos personagens"
    print("✅ Regras de JOGO aplicadas ao prompt")
    
    # Limpa cache
    cache.delete(f"game_session_{sessao.id}_estado")
    sessao.ativa = False
    sessao.save()


def testar_estrutura_dialogo():
    """Testa se as regras de diálogo estão nos prompts"""
    print("\n🧪 TESTE: Estrutura de Diálogo")
    
    from ia_gm.prompts import PromptGenerator
    
    contexto = {
        'npc': {
            'nome': 'Grommash',
            'motivacao': 'Proteger sua aldeia',
            'falha': 'Desconfiança excessiva',
            'segredo': 'Tem medo do escuro',
            'maneirismos': 'Coça a barba quando nervoso',
            'padrao_fala': 'Fala devagar e pausadamente'
        },
        'situacao_dialogo': 'Primeira conversa com os heróis',
        'acao_jogadores': 'Se aproximaram pedindo informações'
    }
    
    prompt_dialogo = PromptGenerator.gerar_dialogo(contexto)
    
    # Verifica se contém a estrutura obrigatória
    assert "[Nome do NPC] [Ação Física ou Expressão Facial]" in prompt_dialogo, "Deve conter formato obrigatório"
    assert "Grommash coça a barba" in prompt_dialogo, "Deve ter exemplo específico"
    assert "ESTRUTURA OBRIGATÓRIA" in prompt_dialogo, "Deve destacar obrigatoriedade"
    print("✅ Estrutura de diálogo presente nos prompts")


def executar_todos_testes():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DAS REGRAS DO MESTRE IA")
    print("=" * 50)
    
    try:
        testar_modo_operacao()
        testar_ciclo_jogo()
        testar_game_session_manager()
        testar_aplicacao_regras()
        testar_estrutura_dialogo()
        
        print("\n" + "=" * 50)
        print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("✅ Regras do Mestre IA implementadas corretamente")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        return False
    except Exception as e:
        print(f"\n💥 ERRO INESPERADO: {e}")
        return False


if __name__ == "__main__":
    sucesso = executar_todos_testes()
    sys.exit(0 if sucesso else 1)