#!/usr/bin/env python
"""
Script para criar dados iniciais de teste do Unified Chronicles
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_chronicles.settings')
django.setup()

from usuarios.models import Usuario
from sistema_unificado.models import SistemaJogo, ConteudoSistema
from campanhas.models import Campanha

def criar_sistemas_jogo():
    """Cria os sistemas de jogo suportados"""
    print("📚 Criando sistemas de jogo...")
    
    # D&D 5e
    dnd5e, created = SistemaJogo.objects.get_or_create(
        codigo='dnd5e',
        defaults={
            'nome': 'D&D 5th Edition',
            'versao': '5.1',
            'descricao': 'Dungeons & Dragons 5ª Edição - Sistema clássico de RPG de fantasia',
            'configuracoes': {
                'dados_vida': {'guerreiro': 10, 'mago': 6, 'clerigo': 8},
                'progressao_nivel': 'xp_table',
                'max_nivel': 20
            }
        }
    )
    if created:
        print(f"  ✓ {dnd5e.nome} criado")
    
    # Tormenta20
    t20, created = SistemaJogo.objects.get_or_create(
        codigo='t20',
        defaults={
            'nome': 'Tormenta20',
            'versao': '1.0',
            'descricao': 'Sistema brasileiro de RPG baseado em Arton',
            'configuracoes': {
                'dados_vida': {'guerreiro': 10, 'arcanista': 6, 'clerigo': 8},
                'progressao_nivel': 'xp_table',
                'max_nivel': 20
            }
        }
    )
    if created:
        print(f"  ✓ {t20.nome} criado")
    
    # Sistema Unificado
    unified, created = SistemaJogo.objects.get_or_create(
        codigo='unified',
        defaults={
            'nome': 'Sistema Unificado',
            'versao': '1.0',
            'descricao': 'Sistema que combina elementos de D&D 5e e Tormenta20',
            'configuracoes': {
                'conversao_automatica': True,
                'balance_factor': 1.0,
                'equivalencias_ativas': True
            }
        }
    )
    if created:
        print(f"  ✓ {unified.nome} criado")
    
    return dnd5e, t20, unified

def criar_conteudo_exemplo(dnd5e, t20):
    """Cria conteúdo de exemplo para os sistemas"""
    print("⚔️  Criando conteúdo de exemplo...")
    
    # Raças D&D 5e
    racas_dnd = [
        {
            'nome': 'Humano',
            'dados_originais': {
                'bonus_atributos': {'todos': 1},
                'tracos': ['Versatilidade'],
                'idiomas': 1,
                'pericias': 1
            }
        },
        {
            'nome': 'Elfo',
            'dados_originais': {
                'bonus_atributos': {'destreza': 2},
                'tracos': ['Sentidos Aguçados', 'Transe Élfico'],
                'proficiencias': ['Percepção', 'Arco Longo'],
                'resistencias': ['encantamento']
            }
        },
        {
            'nome': 'Anão',
            'dados_originais': {
                'bonus_atributos': {'constituicao': 2},
                'tracos': ['Visão no Escuro', 'Resistência Anã'],
                'proficiencias': ['Machados', 'Martelos'],
                'resistencias': ['veneno']
            }
        }
    ]
    
    for raca_data in racas_dnd:
        raca, created = ConteudoSistema.objects.get_or_create(
            sistema_jogo=dnd5e,
            tipo='raca',
            nome=raca_data['nome'],
            defaults={
                'descricao': f'Raça {raca_data["nome"]} do D&D 5e',
                'dados_originais': raca_data['dados_originais'],
                'nivel_minimo': 1,
                'tags': ['core', 'phb']
            }
        )
        if created:
            print(f"    ✓ Raça {raca.nome} (D&D 5e)")
    
    # Classes D&D 5e
    classes_dnd = [
        {
            'nome': 'Guerreiro',
            'dados_originais': {
                'dados_vida': 10,
                'proficiencias_armadura': ['leve', 'media', 'pesada', 'escudos'],
                'proficiencias_armas': ['simples', 'marciais'],
                'resistencias_base': ['forca', 'constituicao'],
                'pericias_escolha': 2,
                'pericias_opcoes': ['Acrobacia', 'Adestrar Animais', 'Atletismo', 'História', 'Intuição', 'Intimidação', 'Percepção', 'Sobrevivência']
            }
        },
        {
            'nome': 'Mago',
            'dados_originais': {
                'dados_vida': 6,
                'proficiencias_armadura': [],
                'proficiencias_armas': ['adaga', 'dardo', 'funda', 'bastao', 'besta_leve'],
                'resistencias_base': ['inteligencia', 'sabedoria'],
                'magias': True,
                'atributo_magia': 'inteligencia'
            }
        }
    ]
    
    for classe_data in classes_dnd:
        classe, created = ConteudoSistema.objects.get_or_create(
            sistema_jogo=dnd5e,
            tipo='classe',
            nome=classe_data['nome'],
            defaults={
                'descricao': f'Classe {classe_data["nome"]} do D&D 5e',
                'dados_originais': classe_data['dados_originais'],
                'nivel_minimo': 1,
                'tags': ['core', 'phb']
            }
        )
        if created:
            print(f"    ✓ Classe {classe.nome} (D&D 5e)")
    
    # Conteúdo básico Tormenta20
    racas_t20 = [
        {
            'nome': 'Humano',
            'dados_originais': {
                'bonus_atributos': {'dois_a_escolha': 1},
                'pericias_extras': 2,
                'talento_extra': 1
            }
        },
        {
            'nome': 'Elfo',
            'dados_originais': {
                'bonus_atributos': {'destreza': 2, 'inteligencia': 1},
                'tracos': ['Sentidos Élficos', 'Herança Élfica'],
                'proficiencias': ['Arco', 'Espada Longa']
            }
        }
    ]
    
    for raca_data in racas_t20:
        raca, created = ConteudoSistema.objects.get_or_create(
            sistema_jogo=t20,
            tipo='raca',
            nome=raca_data['nome'],
            defaults={
                'descricao': f'Raça {raca_data["nome"]} do Tormenta20',
                'dados_originais': raca_data['dados_originais'],
                'nivel_minimo': 1,
                'tags': ['core', 'livro_basico']
            }
        )
        if created:
            print(f"    ✓ Raça {raca.nome} (Tormenta20)")
    
    print(f"  ✓ Criado conteúdo para {dnd5e.nome} e {t20.nome}")

def criar_usuarios_teste():
    """Cria usuários de teste"""
    print("👥 Criando usuários de teste...")
    
    usuarios_data = [
        {
            'username': 'mestre_joao',
            'email': 'mestre@test.com',
            'nome_completo': 'João Silva',
            'campanhas_como_mestre': 2,
            'horas_jogadas': 150
        },
        {
            'username': 'player_ana',
            'email': 'ana@test.com', 
            'nome_completo': 'Ana Santos',
            'campanhas_como_jogador': 3,
            'horas_jogadas': 80
        },
        {
            'username': 'player_carlos',
            'email': 'carlos@test.com',
            'nome_completo': 'Carlos Pereira',
            'campanhas_como_jogador': 2,
            'horas_jogadas': 60
        }
    ]
    
    for user_data in usuarios_data:
        user, created = Usuario.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'nome_completo': user_data['nome_completo'],
                'campanhas_como_mestre': user_data.get('campanhas_como_mestre', 0),
                'campanhas_como_jogador': user_data.get('campanhas_como_jogador', 0),
                'horas_jogadas': user_data.get('horas_jogadas', 0),
                'configuracoes_jogo': {
                    'tema': 'escuro',
                    'notificacoes': True,
                    'sistema_preferido': 'dnd5e'
                }
            }
        )
        user.set_password('test123')
        user.save()
        
        if created:
            print(f"  ✓ Usuário {user.username} ({user.nome_completo})")

def criar_campanhas_teste(sistemas):
    """Cria campanhas de teste"""
    print("🎲 Criando campanhas de teste...")
    
    dnd5e, t20, unified = sistemas
    mestre = Usuario.objects.get(username='mestre_joao')
    
    campanhas_data = [
        {
            'nome': 'A Maldição do Castelo Sombrio',
            'sistema': dnd5e,
            'descricao': 'Uma aventura clássica de D&D 5e em um castelo assombrado. Os heróis devem desvendar os mistérios e quebrar a antiga maldição.',
            'nivel_inicial': 1,
            'nivel_maximo': 10,
            'configuracoes_ia': {
                'personalidade': 'misterioso',
                'nivel_dificuldade': 'medio',
                'foco_narrativo': 'horror_gotico'
            }
        },
        {
            'nome': 'Crônicas de Arton',
            'sistema': t20,
            'descricao': 'Uma campanha épica no mundo de Arton usando o sistema Tormenta20. Os personagens são heróis destinados a salvar o reino.',
            'nivel_inicial': 3,
            'nivel_maximo': 15,
            'configuracoes_ia': {
                'personalidade': 'epico',
                'nivel_dificuldade': 'alto', 
                'foco_narrativo': 'aventura_heroica'
            }
        },
        {
            'nome': 'Experimento Unificado',
            'sistema': unified,
            'descricao': 'Uma campanha experimental usando o sistema unificado, combinando elementos de D&D e Tormenta.',
            'nivel_inicial': 2,
            'nivel_maximo': 12,
            'configuracoes_ia': {
                'personalidade': 'adaptativo',
                'conversao_automatica': True,
                'sistemas_permitidos': ['dnd5e', 't20']
            }
        }
    ]
    
    for camp_data in campanhas_data:
        campanha, created = Campanha.objects.get_or_create(
            nome=camp_data['nome'],
            defaults={
                'organizador': mestre,
                'sistema_jogo': camp_data['sistema'],
                'descricao': camp_data['descricao'],
                'nivel_inicial': camp_data['nivel_inicial'],
                'nivel_maximo': camp_data['nivel_maximo'],
                'estado': 'planejamento',
                'ia_ativa': True,
                'configuracoes_ia': camp_data['configuracoes_ia'],
                'personalidade_gm': {
                    'humor': camp_data['configuracoes_ia'].get('personalidade', 'neutro'),
                    'verbosidade': 'media',
                    'criatividade': 'alta'
                }
            }
        )
        if created:
            print(f"  ✓ Campanha {campanha.nome} ({campanha.sistema_jogo.nome})")

def main():
    """Função principal"""
    print("🚀 Iniciando criação de dados de teste...")
    
    try:
        # Criar sistemas de jogo
        sistemas = criar_sistemas_jogo()
        
        # Criar conteúdo de exemplo
        criar_conteudo_exemplo(sistemas[0], sistemas[1])
        
        # Criar usuários de teste
        criar_usuarios_teste()
        
        # Criar campanhas de teste
        criar_campanhas_teste(sistemas)
        
        print("\n✅ Dados de teste criados com sucesso!")
        print("\n📋 Resumo:")
        print(f"  - Sistemas de jogo: {SistemaJogo.objects.count()}")
        print(f"  - Conteúdos: {ConteudoSistema.objects.count()}")
        print(f"  - Usuários: {Usuario.objects.count()}")
        print(f"  - Campanhas: {Campanha.objects.count()}")
        
        print("\n🎮 Contas de teste criadas:")
        print("  - Admin: admin / admin123")
        print("  - Mestre: mestre_joao / test123")
        print("  - Jogador 1: player_ana / test123")
        print("  - Jogador 2: player_carlos / test123")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()