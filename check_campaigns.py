from campanhas.models import Campanha

campaign_names = ["test2", "Jogando com mestre"]

for name in campaign_names:
    try:
        campanha = Campanha.objects.get(nome=name)
        print(f"Campanha '{name}': publica={campanha.publica}")
    except Campanha.DoesNotExist:
        print(f"Campanha '{name}' não encontrada.")
    except Exception as e:
        print(f"Erro ao buscar campanha '{name}': {e}")
