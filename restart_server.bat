@echo off
echo 🔄 Reiniciando servidor Django...

REM Para o servidor atual (se estiver rodando)
taskkill /F /IM python.exe 2>nul

REM Aguarda um momento
timeout /t 3 /nobreak >nul

REM Ativa o ambiente virtual
call .venv\Scripts\activate.bat

REM Inicia o servidor
echo ✅ Iniciando servidor Django...
python manage.py runserver

pause