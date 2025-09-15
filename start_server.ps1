# Unified Chronicles - Iniciar Servidor Django
# PowerShell Script para Windows

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "    🚀 UNIFIED CHRONICLES - SERVIDOR DJANGO" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está na pasta correta
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Erro: manage.py não encontrado!" -ForegroundColor Red
    Write-Host "Certifique-se de executar este script na pasta do projeto." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Iniciando o servidor..." -ForegroundColor Green
Write-Host ""

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Verificar migrações
Write-Host "Verificando migrações..." -ForegroundColor Yellow
try {
    python manage.py makemigrations --check --dry-run | Out-Null
} catch {
    Write-Host "⚠️  Aplicando migrações pendentes..." -ForegroundColor Yellow
    python manage.py makemigrations
    python manage.py migrate
    Write-Host "✅ Migrações aplicadas com sucesso!" -ForegroundColor Green
    Write-Host ""
}

# Coletar arquivos estáticos
Write-Host "Coletando arquivos estáticos..." -ForegroundColor Yellow
try {
    python manage.py collectstatic --noinput | Out-Null
} catch {
    # Ignorar erro se não houver arquivos estáticos
}

# Mostrar informações do servidor
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " 🌐 Servidor disponível em:" -ForegroundColor Green
Write-Host "    • http://localhost:8000/" -ForegroundColor White
Write-Host "    • http://0.0.0.0:8000/" -ForegroundColor White
Write-Host ""
Write-Host " 📝 Credenciais Admin:" -ForegroundColor Green
Write-Host "    • Usuário: admin" -ForegroundColor White
Write-Host "    • Senha: admin123" -ForegroundColor White
Write-Host "    • Admin: http://localhost:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host " ⏹️  Para parar: Ctrl + C" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor
try {
    python manage.py runserver 0.0.0.0:8000
} catch {
    Write-Host ""
    Write-Host "❌ Erro ao iniciar servidor!" -ForegroundColor Red
    Write-Host "Verifique se o Python e Django estão instalados corretamente." -ForegroundColor Red
}

Write-Host ""
Write-Host "Servidor finalizado." -ForegroundColor Yellow
pause