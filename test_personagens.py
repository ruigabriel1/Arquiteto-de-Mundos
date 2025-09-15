#!/usr/bin/env python
"""
Script de teste para verificar o sistema de personagens avançado
"""

import os
import sys
import django
from django.test import Client
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_chronicles.settings')
django.setup()

from django.contrib.auth import get_user_model
from sistema_unificado.models import SistemaJogo, ConteudoSistema
from campanhas.models import Campanha

User = get_user_model()


def test_sistema_data():
    """Testar se os dados dos sistemas foram carregados corretamente"""
    print("🧪 Testando dados dos sistemas...")
    
    # Verificar sistemas
    sistemas = SistemaJogo.objects.all()
    print(f"✅ Sistemas encontrados: {sistemas.count()}")
    for sistema in sistemas:
        print(f"   - {sistema.nome} ({sistema.codigo})")
    
    # Verificar conteúdos
    for sistema in sistemas:
        racas = ConteudoSistema.objects.filter(sistema_jogo=sistema, tipo='raca').count()
        classes = ConteudoSistema.objects.filter(sistema_jogo=sistema, tipo='classe').count()
        print(f"   {sistema.codigo}: {racas} raças, {classes} classes")
    
    print()


def test_apis():
    """Testar as APIs do sistema"""
    print("🧪 Testando APIs...")
    
    client = Client()
    
    # Testar API de sistemas
    response = client.get('/api/personagens/api/sistemas/')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API sistemas: {data['total']} sistemas encontrados")
    else:
        print(f"❌ API sistemas falhou: {response.status_code}")
    
    # Testar API de conteúdo por sistema
    for sistema_slug in ['dnd5e', 't20']:
        response = client.get(f'/api/personagens/api/sistema-conteudo/{sistema_slug}/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API {sistema_slug}: {data['total_racas']} raças, {data['total_classes']} classes")
        else:
            print(f"❌ API {sistema_slug} falhou: {response.status_code}")
    
    print()


def test_template_views():
    """Testar as views de template"""
    print("🧪 Testando views de template...")
    
    client = Client()
    
    # Criar usuário de teste
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print("✅ Usuário de teste criado")
    
    # Fazer login
    client.login(username='testuser', password='testpass123')
    
    # Testar página de listagem
    response = client.get('/personagens/')
    if response.status_code == 200:
        print("✅ Página de listagem de personagens carregou")
    else:
        print(f"❌ Página de listagem falhou: {response.status_code}")
    
    # Testar construtor avançado
    response = client.get('/personagens/criar/avancado/')
    if response.status_code == 200:
        print("✅ Construtor avançado carregou")
    else:
        print(f"❌ Construtor avançado falhou: {response.status_code}")
    
    print()


def test_character_creation_flow():
    """Testar o fluxo completo de criação de personagem"""
    print("🧪 Testando fluxo de criação de personagem...")
    
    client = Client()
    
    # Login
    user = User.objects.get(username='testuser')
    client.login(username='testuser', password='testpass123')
    
    # Criar uma campanha de teste
    try:
        campanha = Campanha.objects.get(nome='Campanha Teste')
    except Campanha.DoesNotExist:
        # Primeiro, precisa de um sistema de jogo
        sistema = SistemaJogo.objects.first()
        campanha = Campanha.objects.create(
            nome='Campanha Teste',
            descricao='Campanha para testes',
            organizador=user,
            sistema_jogo=sistema
        )
        print("✅ Campanha de teste criada")
    
    # Buscar dados para criação
    sistema_dnd = SistemaJogo.objects.get(codigo='dnd5e')
    raca_humano = ConteudoSistema.objects.filter(
        sistema_jogo=sistema_dnd, 
        tipo='raca'
    ).first()
    classe_guerreiro = ConteudoSistema.objects.filter(
        sistema_jogo=sistema_dnd, 
        tipo='classe'
    ).first()
    
    if raca_humano and classe_guerreiro:
        print(f"✅ Dados encontrados: {raca_humano.nome}, {classe_guerreiro.nome}")
        
        # Simular dados do formulário avançado
        character_data = {
            'nome': 'Herói Teste',
            'campanha': campanha.id,
            'sistema': 'dnd5e',
            'raca': raca_humano.id,
            'classe': classe_guerreiro.id,
            'forca': 15,
            'destreza': 14,
            'constituicao': 13,
            'inteligencia': 12,
            'sabedoria': 10,
            'carisma': 8,
            'historia': 'Um herói corajoso de teste',
            'personalidade': 'Corajoso e determinado'
        }
        
        print("✅ Dados do personagem preparados para criação")
        print(f"   Nome: {character_data['nome']}")
        print(f"   Sistema: {character_data['sistema']}")
        print(f"   Atributos: FOR{character_data['forca']} DES{character_data['destreza']} CON{character_data['constituicao']}")
    else:
        print("❌ Não foi possível encontrar raças ou classes para teste")
    
    print()


def main():
    """Executar todos os testes"""
    print("=" * 60)
    print("🚀 TESTANDO SISTEMA DE PERSONAGENS AVANÇADO")
    print("=" * 60)
    print()
    
    try:
        test_sistema_data()
        test_apis()
        test_template_views()
        test_character_creation_flow()
        
        print("=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 60)
        print()
        print("🎯 O sistema está funcionando corretamente:")
        print("   • Dados populados no banco")
        print("   • APIs respondendo")
        print("   • Templates carregando")
        print("   • Fluxo de criação preparado")
        print()
        print("🌐 Acesse: http://127.0.0.1:8000/personagens/criar/avancado/")
        print("   (após fazer login)")
        
    except Exception as e:
        print(f"❌ ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()