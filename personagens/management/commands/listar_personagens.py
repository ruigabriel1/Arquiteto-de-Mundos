"""
Comando Django para listar personagens do sistema
"""

from django.core.management.base import BaseCommand
from personagens.models import Personagem
from campanhas.models import Campanha
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Lista todos os personagens do sistema'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('📋 Listando personagens do sistema...\n')
        )
        
        # Contar totais
        total_personagens = Personagem.objects.count()
        total_usuarios = User.objects.count()
        total_campanhas = Campanha.objects.count()
        
        self.stdout.write(f"🎲 Total de personagens: {total_personagens}")
        self.stdout.write(f"👥 Total de usuários: {total_usuarios}")
        self.stdout.write(f"🏰 Total de campanhas: {total_campanhas}\n")
        
        # Listar personagens
        personagens = Personagem.objects.select_related('usuario', 'campanha').all()
        
        if not personagens:
            self.stdout.write(
                self.style.WARNING('⚠️ Nenhum personagem encontrado!')
            )
            return
        
        for personagem in personagens:
            self.stdout.write(
                f"🧙 {personagem.nome} (Nível {personagem.nivel})"
            )
            self.stdout.write(
                f"   👤 Jogador: {personagem.usuario.username}"
            )
            self.stdout.write(
                f"   🏰 Campanha: {personagem.campanha.nome}"
            )
            
            # Mostrar raça/classe se disponível
            raca_nome = ""
            if personagem.raca and isinstance(personagem.raca, dict):
                raca_nome = personagem.raca.get('nome', '')
            
            classe_nome = ""
            if personagem.classes and isinstance(personagem.classes, list) and len(personagem.classes) > 0:
                classe_nome = personagem.classes[0].get('nome', '')
            
            if raca_nome or classe_nome:
                self.stdout.write(
                    f"   🎭 {raca_nome} {classe_nome}".strip()
                )
            
            # Mostrar atributos
            self.stdout.write(
                f"   ⚔️ FOR:{personagem.forca} DES:{personagem.destreza} CON:{personagem.constituicao} INT:{personagem.inteligencia} SAB:{personagem.sabedoria} CAR:{personagem.carisma}"
            )
            
            self.stdout.write(
                f"   📅 Criado: {personagem.data_criacao.strftime('%d/%m/%Y %H:%M')}\n"
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Listagem concluída! Total: {total_personagens} personagens')
        )