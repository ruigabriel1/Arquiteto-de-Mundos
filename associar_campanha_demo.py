import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_chronicles.settings')
django.setup()

from django.contrib.auth import get_user_model
from campanhas.models import Campanha

User = get_user_model()

try:
    # Pega ou cria o usuário 'demo'
    demo_user, created = User.objects.get_or_create(
        username='demo',
        defaults={'first_name': 'Usuário', 'last_name': 'Demo', 'email': 'demo@example.com'}
    )
    
    if created:
        demo_user.set_password('demo123')
        demo_user.save()
        print(f"INFO: Usuário '{demo_user.username}' criado com a senha 'demo123'.")

    # Pega a primeira campanha do banco de dados
    primeira_campanha = Campanha.objects.first()
    
    if primeira_campanha:
        # Define o usuário 'demo' como organizador
        if primeira_campanha.organizador != demo_user:
            primeira_campanha.organizador = demo_user
            primeira_campanha.save()
            print(f"SUCESSO: O usuário '{demo_user.username}' agora é o organizador da campanha '{primeira_campanha.nome}'.")
        else:
            print(f"INFO: O usuário '{demo_user.username}' já é o organizador da campanha '{primeira_campanha.nome}'.")
    else:
        print("AVISO: Nenhuma campanha encontrada no banco de dados.")

except Exception as e:
    print(f"ERRO: Ocorreu um erro inesperado: {e}")