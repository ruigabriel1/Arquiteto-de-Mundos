#!/usr/bin/env python
"""
Script para criar superusuário do Unified Chronicles
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_chronicles.settings')
django.setup()

from usuarios.models import Usuario

# Criar superusuário
try:
    admin = Usuario.objects.create_superuser(
        username='admin',
        email='admin@unified.local', 
        password='admin123',
        nome_completo='Administrador do Sistema'
    )
    print(f"✓ Superusuário criado: {admin.username} ({admin.email})")
    print("  Senha: admin123")
    print("  Acesse: http://localhost:8000/admin/")
except Exception as e:
    print(f"✗ Erro ao criar superusuário: {e}")