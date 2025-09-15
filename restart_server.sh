#!/bin/bash

echo "🔄 Reiniciando servidor Django..."

# Para o servidor atual (se estiver rodando)
pkill -f "python manage.py runserver" 2>/dev/null

# Aguarda um momento
sleep 3

# Ativa o ambiente virtual
source .venv/bin/activate

# Inicia o servidor
echo "✅ Iniciando servidor Django..."
python manage.py runserver