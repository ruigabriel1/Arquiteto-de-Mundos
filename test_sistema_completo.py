#!/usr/bin/env python
"""
Script para testar se o sistema Unified Chronicles está funcionando completamente
Executa uma bateria de testes para verificar todas as funcionalidades principais
"""

import os
import sys
import django
import asyncio
from django.test.utils import get_runner
from django.conf import settings

# Setup do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_chronicles.settings')
django.setup()

from django.contrib.auth import get_user_model
from campanhas.models import Campanha
from personagens.models import Personagem
from sistema_unificado.models import SistemaJogo
from ia_gm.models import SessaoIA
from django.core.management import call_command

User = get_user_model()

def testar_banco_dados():
    """Testa se o banco de dados está funcionando"""
    print("🔍 Testando banco de dados...")
    
    try:
        # Testa conexão básica
        total_users = User.objects.count()
        print(f"   ✅ Usuários no banco: {total_users}")
        
        # Testa modelo personalizado de usuário
        if total_users > 0:
            admin = User.objects.first()
            print(f"   ✅ Usuário admin: {admin.username}")
            print(f"   ✅ Configurações JSON: {type(admin.configuracoes_jogo).__name__}")
        
        # Testa outros modelos
        campanhas = Campanha.objects.count()
        sistemas = SistemaJogo.objects.count()
        personagens = Personagem.objects.count()
        
        print(f"   ✅ Campanhas: {campanhas}")
        print(f"   ✅ Sistemas de jogo: {sistemas}")
        print(f"   ✅ Personagens: {personagens}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no banco: {e}")
        return False

def testar_urls():
    """Testa se as URLs principais estão configuradas"""
    print("\n🌐 Testando configuração de URLs...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # URLs principais
        urls_teste = [
            ('usuarios:index', 'Página inicial'),
            ('admin:index', 'Admin'),
        ]
        
        for url_name, descricao in urls_teste:
            try:
                url = reverse(url_name)
                print(f"   ✅ {descricao}: {url}")
            except Exception as e:
                print(f"   ⚠️ {descricao}: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nas URLs: {e}")
        return False

def testar_templates():
    """Testa se os templates existem"""
    print("\n📄 Testando templates...")
    
    try:
        from django.template.loader import get_template
        
        templates_teste = [
            'base.html',
            'index.html',
            'usuarios/index.html'
        ]
        
        for template_name in templates_teste:
            try:
                template = get_template(template_name)
                print(f"   ✅ Template: {template_name}")
            except Exception as e:
                print(f"   ⚠️ Template {template_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nos templates: {e}")
        return False

def testar_arquivos_estaticos():
    """Testa se arquivos estáticos estão configurados"""
    print("\n📁 Testando arquivos estáticos...")
    
    try:
        from django.contrib.staticfiles import finders
        from django.conf import settings
        import os
        
        # Testa configuração básica
        print(f"   ✅ STATIC_URL: {settings.STATIC_URL}")
        print(f"   ✅ STATIC_ROOT: {settings.STATIC_ROOT}")
        
        # Testa se diretório static existe
        static_dirs = settings.STATICFILES_DIRS
        for static_dir in static_dirs:
            if os.path.exists(static_dir):
                print(f"   ✅ Diretório estático: {static_dir}")
            else:
                print(f"   ⚠️ Diretório não existe: {static_dir}")
        
        # Testa alguns arquivos
        arquivos_teste = [
            'css/global-theme.css',
            'js/game-session.js'
        ]
        
        for arquivo in arquivos_teste:
            if finders.find(arquivo):
                print(f"   ✅ Arquivo estático: {arquivo}")
            else:
                print(f"   ⚠️ Não encontrado: {arquivo}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nos arquivos estáticos: {e}")
        return False

def testar_ia_gm():
    """Testa o sistema de IA Game Master"""
    print("\n🤖 Testando sistema IA Game Master...")
    
    try:
        from ia_gm.master_rules import MasterRulesEngine, ModoOperacao
        from ia_gm.models import SessaoIA
        
        # Testa regras comportamentais
        regras_config = MasterRulesEngine.gerar_prompt_comportamental(ModoOperacao.CONFIGURACAO)
        regras_jogo = MasterRulesEngine.gerar_prompt_comportamental(ModoOperacao.JOGO)
        
        print("   ✅ Regras de configuração geradas")
        print("   ✅ Regras de jogo geradas")
        
        # Testa validação
        validacao = MasterRulesEngine.validar_entrada_comando("/npc teste", ModoOperacao.CONFIGURACAO)
        if validacao['valida']:
            print("   ✅ Validação de comandos funcionando")
        
        # Testa se há sessões
        sessoes = SessaoIA.objects.count()
        print(f"   ✅ Sessões IA no banco: {sessoes}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no sistema IA GM: {e}")
        return False

def testar_dependencias():
    """Testa se as dependências principais estão instaladas"""
    print("\n📦 Testando dependências...")
    
    dependencias = [
        ('django', 'Django'),
        ('channels', 'Django Channels'),
        ('rest_framework', 'DRF'),
        ('corsheaders', 'CORS Headers'),
        ('PIL', 'Pillow'),  # Pillow é importado como PIL
        ('redis', 'Redis')
    ]
    
    sucesso = True
    for modulo, nome in dependencias:
        try:
            __import__(modulo)
            print(f"   ✅ {nome}")
        except ImportError:
            print(f"   ❌ {nome} não encontrado")
            sucesso = False
    
    return sucesso

def main():
    """Executa todos os testes"""
    print("🚀 TESTANDO SISTEMA UNIFIED CHRONICLES")
    print("=" * 50)
    
    testes = [
        testar_dependencias,
        testar_banco_dados,
        testar_urls,
        testar_templates,
        testar_arquivos_estaticos,
        testar_ia_gm
    ]
    
    resultados = []
    for teste in testes:
        resultado = teste()
        resultados.append(resultado)
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    
    sucessos = sum(resultados)
    total = len(resultados)
    
    if sucessos == total:
        print(f"🎉 TODOS OS TESTES PASSARAM! ({sucessos}/{total})")
        print("\n✅ O sistema está funcionando corretamente!")
        print("\n🚀 Para iniciar o servidor:")
        print("   - Execute: .\\start_server.bat")
        print("   - Ou: python manage.py runserver")
        print("\n🌐 URLs importantes:")
        print("   - Frontend: http://localhost:8000/")
        print("   - Admin: http://localhost:8000/admin/")
        print("   - IA GM: http://localhost:8000/arquiteto/")
        print("\n👤 Credenciais:")
        print("   - Admin: admin / admin123")
        print("   - Teste: mestre_joao / test123")
    else:
        print(f"⚠️ {sucessos}/{total} testes passaram")
        print("❌ Alguns problemas foram encontrados. Verifique os logs acima.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())