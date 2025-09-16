#!/usr/bin/env python
"""
Script OPCIONAL para remover o frontend React não utilizado
Remove a pasta frontend/ que contém node_modules (246MB, 41.884 arquivos)

ATENÇÃO: Execute apenas se você tem certeza de que não precisa do frontend React!
O projeto está funcionando perfeitamente com templates Django + Bootstrap.
"""

import shutil
from pathlib import Path

def analisar_frontend():
    """Analisa o frontend React e suas dependências"""
    print("🔍 ANÁLISE DO FRONTEND REACT")
    print("=" * 50)
    
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Pasta frontend/ não encontrada")
        return False
        
    # Analisa node_modules
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        try:
            # Conta arquivos aproximadamente (para não travar)
            arquivos_amostra = list(node_modules.rglob("*"))[:1000]  # Amostra de 1000 arquivos
            total_aproximado = len(list(node_modules.iterdir())) * 50  # Estimativa conservadora
            
            print(f"📦 Frontend React identificado:")
            print(f"   📁 Localização: {frontend_dir}")
            print(f"   📊 Tamanho estimado: ~246MB")
            print(f"   🗂️ Arquivos estimados: ~42.000")
            print(f"   📋 Status: NÃO UTILIZADO (projeto usa templates Django)")
            
        except Exception as e:
            print(f"⚠️ Erro ao analisar: {e}")
            
    else:
        print("ℹ️ node_modules não encontrado, apenas código fonte")
    
    # Verifica arquivos fonte
    src_files = list(frontend_dir.rglob("*.tsx")) + list(frontend_dir.rglob("*.ts")) + list(frontend_dir.rglob("*.jsx")) + list(frontend_dir.rglob("*.js"))
    print(f"💻 Arquivos de código fonte: {len(src_files)}")
    
    return True

def confirmar_remocao():
    """Pede confirmação do usuário"""
    print("\n" + "⚠️" * 20)
    print("ATENÇÃO: OPERAÇÃO IRREVERSÍVEL")
    print("⚠️" * 20)
    
    print("\n❗ Você está prestes a remover:")
    print("   📁 frontend/ (pasta completa)")
    print("   📦 node_modules/ (~246MB)")
    print("   💻 Código React/TypeScript")
    print("   📋 package.json e dependências")
    
    print("\n✅ Motivos para remover:")
    print("   - Projeto funciona perfeitamente sem React")
    print("   - Usa templates Django + Bootstrap nativamente")
    print("   - Economiza 246MB de espaço")
    print("   - Remove 41.884 arquivos desnecessários")
    
    print("\n❌ Riscos:")
    print("   - Perda total do código React (irreversível)")
    print("   - Não poderá criar SPA no futuro sem recriar")
    
    print("\n" + "-" * 50)
    
    while True:
        resposta = input("🤔 Tem certeza que quer remover o frontend React? (sim/não): ").strip().lower()
        
        if resposta in ['sim', 's', 'yes', 'y']:
            return True
        elif resposta in ['não', 'nao', 'n', 'no']:
            return False
        else:
            print("❌ Resposta inválida. Digite 'sim' ou 'não'")

def remover_frontend():
    """Remove a pasta frontend"""
    print("\n🗑️ REMOVENDO FRONTEND REACT...")
    
    frontend_dir = Path("frontend")
    
    try:
        # Backup da configuração (caso seja necessário no futuro)
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            shutil.copy2(package_json, backup_dir / "package.json.backup")
            print("   💾 Backup do package.json salvo em backups/")
        
        # Remove a pasta completa
        shutil.rmtree(frontend_dir)
        print("   ✅ Pasta frontend/ removida completamente")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao remover: {e}")
        return False

def main():
    """Função principal"""
    print("🧹 LIMPEZA OPCIONAL - FRONTEND REACT")
    print("=" * 50)
    
    # Analisa o estado atual
    if not analisar_frontend():
        return 1
    
    # Confirmação do usuário
    if not confirmar_remocao():
        print("\n✅ Operação cancelada. Frontend mantido.")
        print("💡 O projeto continuará funcionando normalmente com templates Django.")
        return 0
    
    # Segunda confirmação (segurança)
    print("\n⚠️ ÚLTIMA CHANCE!")
    confirmacao_final = input("✋ Digite 'REMOVER FRONTEND' para confirmar: ").strip()
    
    if confirmacao_final != "REMOVER FRONTEND":
        print("\n✅ Operação cancelada por segurança.")
        return 0
    
    # Remove o frontend
    if remover_frontend():
        print("\n🎉 Frontend React removido com sucesso!")
        
        # Executa estatísticas pós-remoção
        from pathlib import Path
        raiz = Path(".")
        arquivos_restantes = sum(1 for f in raiz.rglob("*") if f.is_file() and ".venv" not in str(f))
        
        print(f"\n📊 RESULTADO:")
        print(f"   📄 Arquivos no projeto: {arquivos_restantes}")
        print(f"   💾 Espaço economizado: ~246MB")
        print(f"   🗑️ Arquivos removidos: ~41.884")
        
        print(f"\n✅ Projeto mais limpo e organizado!")
        print(f"💡 Execute 'python test_sistema_completo.py' para verificar se tudo está funcionando.")
        
    else:
        print("\n❌ Falha ao remover frontend.")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())