#!/usr/bin/env python
"""
Script para limpar arquivos desnecessários e organizar o projeto Unified Chronicles
Remove backups, arquivos temporários, duplicados e reorganiza a estrutura
"""

import os
import shutil
from pathlib import Path

def limpar_projeto():
    """Limpa arquivos desnecessários do projeto"""
    print("🧹 LIMPEZA DO PROJETO UNIFIED CHRONICLES")
    print("=" * 50)
    
    # Diretório raiz do projeto
    raiz = Path(".")
    
    # Lista de arquivos para remover
    arquivos_remover = [
        "db.sqlite3.bak",        # Backup antigo do banco
        "db.sqlite3.tmp",        # Arquivo temporário
        "requirements_new.txt",  # Gerado durante testes
        ".env.local",           # Duplicata da configuração
        ".env.local.example",   # Exemplo duplicado
        "restart_server.sh",    # Script Unix não usado no Windows
        "start_server.ps1",     # Script PowerShell não usado
        "test_personagens.py"   # Script de teste isolado
    ]
    
    # Remove arquivos desnecessários
    print("🗑️ Removendo arquivos desnecessários...")
    for arquivo in arquivos_remover:
        caminho = raiz / arquivo
        if caminho.exists():
            try:
                if caminho.is_file():
                    caminho.unlink()
                    print(f"   ✅ Removido: {arquivo}")
                else:
                    print(f"   ⚠️ Não é arquivo: {arquivo}")
            except Exception as e:
                print(f"   ❌ Erro ao remover {arquivo}: {e}")
        else:
            print(f"   ℹ️ Já removido: {arquivo}")
    
    # Verifica pastas vazias que podem ser limpas
    print("\n📁 Verificando pastas...")
    
    pastas_verificar = [
        "logs",
        "media", 
        "scripts",
        "docs/temp" if (raiz / "docs" / "temp").exists() else None,
        "backups/old" if (raiz / "backups" / "old").exists() else None
    ]
    
    for pasta in pastas_verificar:
        if pasta is None:
            continue
            
        caminho_pasta = raiz / pasta
        if caminho_pasta.exists() and caminho_pasta.is_dir():
            # Conta arquivos (excluindo .gitkeep)
            arquivos = [f for f in caminho_pasta.rglob("*") if f.is_file() and f.name != ".gitkeep"]
            if len(arquivos) == 0:
                print(f"   📂 {pasta}: Vazia (mantida para estrutura)")
            else:
                print(f"   📂 {pasta}: {len(arquivos)} arquivo(s)")
    
    # Limpa arquivos temporários ocultos comuns
    print("\n🔍 Procurando arquivos temporários...")
    
    padroes_temp = [
        "**/*.tmp",
        "**/*.bak", 
        "**/*.swp",
        "**/Thumbs.db",
        "**/.DS_Store",
        "**/desktop.ini"
    ]
    
    for padrao in padroes_temp:
        arquivos_temp = list(raiz.glob(padrao))
        # Exclui arquivos dentro de .venv
        arquivos_temp = [f for f in arquivos_temp if ".venv" not in str(f)]
        
        for arquivo_temp in arquivos_temp:
            try:
                arquivo_temp.unlink()
                print(f"   🗑️ Removido temporário: {arquivo_temp}")
            except Exception as e:
                print(f"   ❌ Erro ao remover {arquivo_temp}: {e}")
    
    # Consolida configurações de exemplo
    print("\n⚙️ Consolidando arquivos de configuração...")
    
    # Mantém apenas .env.example como referência principal
    if (raiz / ".env.example").exists():
        print("   ✅ .env.example mantido como referência principal")
    
    # Verifica arquivos de requisitos
    print("\n📦 Verificando arquivos de requisitos...")
    if (raiz / "requirements.txt").exists():
        print("   ✅ requirements.txt principal mantido")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMO DA LIMPEZA:")
    
    # Calcula estatísticas finais
    total_arquivos = sum(1 for f in raiz.rglob("*") if f.is_file() and ".venv" not in str(f))
    total_pastas = sum(1 for f in raiz.rglob("*") if f.is_dir() and ".venv" not in str(f))
    
    print(f"   📄 Arquivos no projeto: {total_arquivos}")
    print(f"   📁 Pastas no projeto: {total_pastas}")
    
    # Verifica arquivos importantes
    arquivos_importantes = [
        "manage.py",
        "requirements.txt", 
        "README.md",
        "WARP.md",
        ".env.example",
        "start_server.bat"
    ]
    
    print("\n✅ Arquivos principais verificados:")
    for arquivo in arquivos_importantes:
        if (raiz / arquivo).exists():
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo} - FALTANDO!")
    
    print("\n🎉 Limpeza concluída!")
    print("\n📋 Próximos passos recomendados:")
    print("   1. Executar: python test_sistema_completo.py")
    print("   2. Verificar se tudo funciona: .\\start_server.bat") 
    print("   3. Fazer commit das alterações se tudo estiver OK")

def main():
    """Função principal"""
    try:
        limpar_projeto()
    except Exception as e:
        print(f"\n💥 Erro durante a limpeza: {e}")
        return 1
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())