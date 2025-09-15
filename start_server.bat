@echo off
echo ================================================
echo     🚀 UNIFIED CHRONICLES - SERVIDOR DJANGO
echo ================================================
echo.
echo Iniciando o servidor...
echo.

REM Ativar ambiente virtual
call venv\Scripts\activate

REM Verificar se há migrações pendentes
echo Verificando migrações...
python manage.py makemigrations --check --dry-run > nul 2>&1
if errorlevel 1 (
    echo ⚠️  Aplicando migrações pendentes...
    python manage.py makemigrations
    python manage.py migrate
    echo ✅ Migrações aplicadas com sucesso!
    echo.
)

REM Coletar arquivos estáticos (se necessário)
echo Coletando arquivos estáticos...
python manage.py collectstatic --noinput > nul 2>&1

REM Iniciar servidor
echo ================================================
echo  🌐 Servidor disponível em:
echo     • Frontend: http://localhost:8000/
echo     • Admin: http://localhost:8000/admin/
echo     • API REST: http://localhost:8000/api/
echo     • 🧿 Arquiteto de Mundos: http://localhost:8000/arquiteto/
echo.
echo  📝 Credenciais Admin:
echo     • Usuário: admin
echo     • Senha: admin123
echo.
echo  ✨ NOVO: Sistema "Arquiteto de Mundos" - IA Game Master
echo     Filosofia "Sim, e..." para narrativas colaborativas
echo.
echo  ⏹️  Para parar: Ctrl + C
echo ================================================
echo.

python manage.py runserver 0.0.0.0:8000

echo.
echo Servidor finalizado.
pause