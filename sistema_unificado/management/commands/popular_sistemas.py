"""
Comando para popular o banco de dados com conteúdo de Tormenta 20 e D&D 5e
"""

from django.core.management.base import BaseCommand
from sistema_unificado.models import SistemaJogo, ConteudoSistema


class Command(BaseCommand):
    help = 'Popula o banco com dados de Tormenta 20 e D&D 5e'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população dos sistemas...')
        
        # Criar sistemas
        self.criar_sistemas()
        
        # Popular D&D 5e
        self.popular_dnd5e()
        
        # Popular Tormenta 20
        self.popular_tormenta20()
        
        self.stdout.write(
            self.style.SUCCESS('Sistemas populados com sucesso!')
        )

    def criar_sistemas(self):
        """Criar os sistemas de jogo"""
        sistemas = [
            {
                'nome': 'D&D 5th Edition',
                'codigo': 'dnd5e',
                'versao': '5.1',
                'descricao': 'Dungeons & Dragons 5ª Edição'
            },
            {
                'nome': 'Tormenta20',
                'codigo': 't20',
                'versao': '1.0',
                'descricao': 'Sistema Tormenta20'
            },
            {
                'nome': 'Sistema Unificado',
                'codigo': 'unified',
                'versao': '1.0',
                'descricao': 'Sistema unificado T20 + D&D 5e'
            }
        ]
        
        for sistema_data in sistemas:
            sistema, created = SistemaJogo.objects.get_or_create(
                codigo=sistema_data['codigo'],
                defaults=sistema_data
            )
            if created:
                self.stdout.write(f'Criado sistema: {sistema.nome}')

    def popular_dnd5e(self):
        """Popular conteúdo D&D 5e"""
        sistema = SistemaJogo.objects.get(codigo='dnd5e')
        
        # Raças D&D 5e
        racas_dnd5e = [
            {
                'nome': 'Humano',
                'descricao': 'A raça mais versátil e adaptável',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 30,
                    'bonus_atributos': {'todos': 1},
                    'idiomas': ['Comum', 'Um adicional'],
                    'tracos': ['Perícia adicional', 'Talento adicional']
                }
            },
            {
                'nome': 'Elfo',
                'descricao': 'Seres mágicos longevos com conexão com a natureza',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 30,
                    'bonus_atributos': {'destreza': 2},
                    'idiomas': ['Comum', 'Élfico'],
                    'tracos': ['Visão no Escuro', 'Percepção aguçada', 'Ancestral Feérico', 'Transe']
                }
            },
            {
                'nome': 'Anão',
                'descricao': 'Povo robusto das montanhas, mestres artesãos',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 25,
                    'bonus_atributos': {'constituicao': 2},
                    'idiomas': ['Comum', 'Anão'],
                    'tracos': ['Visão no Escuro', 'Resistência Anã', 'Proficiências Anãs']
                }
            },
            {
                'nome': 'Halfling',
                'descricao': 'Pequenos e ágeis, mestres da sorte',
                'dados_originais': {
                    'tamanho': 'Pequeno',
                    'deslocamento': 25,
                    'bonus_atributos': {'destreza': 2},
                    'idiomas': ['Comum', 'Halfling'],
                    'tracos': ['Sortudo', 'Corajoso', 'Agilidade Halfling']
                }
            }
        ]
        
        for raca_data in racas_dnd5e:
            ConteudoSistema.objects.get_or_create(
                sistema_jogo=sistema,
                tipo='raca',
                nome=raca_data['nome'],
                defaults={
                    'descricao': raca_data['descricao'],
                    'dados_originais': raca_data['dados_originais']
                }
            )
        
        # Classes D&D 5e
        classes_dnd5e = [
            {
                'nome': 'Guerreiro',
                'descricao': 'Mestre das armas e combate',
                'dados_originais': {
                    'dado_vida': 10,
                    'proficiencias_saving': ['Força', 'Constituição'],
                    'proficiencias_armadura': ['Leve', 'Média', 'Pesada', 'Escudos'],
                    'proficiencias_arma': ['Simples', 'Marciais'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['Acrobacia', 'Adestrar Animais', 'Atletismo', 'História', 'Intimidação', 'Intuição', 'Percepção', 'Sobrevivência']
                }
            },
            {
                'nome': 'Mago',
                'descricao': 'Estudioso das artes arcanas',
                'dados_originais': {
                    'dado_vida': 6,
                    'proficiencias_saving': ['Inteligência', 'Sabedoria'],
                    'proficiencias_armadura': [],
                    'proficiencias_arma': ['Adaga', 'Dardo', 'Funda', 'Bordão', 'Besta leve'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['Arcanismo', 'História', 'Intuição', 'Investigação', 'Medicina', 'Religião'],
                    'conjuracao': {
                        'atributo': 'Inteligência',
                        'conhece_magias': True,
                        'ritual': True
                    }
                }
            }
        ]
        
        for classe_data in classes_dnd5e:
            ConteudoSistema.objects.get_or_create(
                sistema_jogo=sistema,
                tipo='classe',
                nome=classe_data['nome'],
                defaults={
                    'descricao': classe_data['descricao'],
                    'dados_originais': classe_data['dados_originais']
                }
            )

    def popular_tormenta20(self):
        """Popular conteúdo Tormenta20"""
        sistema = SistemaJogo.objects.get(codigo='t20')
        
        # Raças Tormenta20
        racas_t20 = [
            {
                'nome': 'Humano',
                'descricao': 'A raça mais comum e versátil de Arton',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 9,
                    'bonus_atributos': {'livre': 2, 'livre2': 1},
                    'idiomas': ['Valkar', 'Um regional'],
                    'tracos': ['Versátil', 'Perícia adicional', 'Talento adicional']
                }
            },
            {
                'nome': 'Elfo',
                'descricao': 'Descendentes dos primeiros elfos de Lenórienn',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 9,
                    'bonus_atributos': {'destreza': 2, 'inteligencia': 1},
                    'idiomas': ['Valkar', 'Élfico'],
                    'tracos': ['Visão na Penumbra', 'Herança Feérica', 'Proficiência Élfica']
                }
            },
            {
                'nome': 'Anão',
                'descricao': 'Povo das montanhas, mestres da forja',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 6,
                    'bonus_atributos': {'constituicao': 2, 'sabedoria': 1},
                    'idiomas': ['Valkar', 'Anão'],
                    'tracos': ['Visão na Penumbra', 'Tradição de Ofício', 'Resistência Anã']
                }
            }
        ]
        
        for raca_data in racas_t20:
            ConteudoSistema.objects.get_or_create(
                sistema_jogo=sistema,
                tipo='raca',
                nome=raca_data['nome'],
                defaults={
                    'descricao': raca_data['descricao'],
                    'dados_originais': raca_data['dados_originais']
                }
            )
        
        # Classes Tormenta20
        classes_t20 = [
            {
                'nome': 'Guerreiro',
                'descricao': 'Especialista em combate e armas',
                'dados_originais': {
                    'pv_nivel': 20,
                    'pm_nivel': 2,
                    'proficiencias': ['Armas simples', 'Armas marciais', 'Armaduras leves', 'Armaduras pesadas', 'Escudos'],
                    'pericias_treinadas': 4,
                    'atributo_principal': 'Força'
                }
            },
            {
                'nome': 'Arcanista',
                'descricao': 'Estudioso das artes mágicas',
                'dados_originais': {
                    'pv_nivel': 12,
                    'pm_nivel': 6,
                    'proficiencias': ['Armas simples'],
                    'pericias_treinadas': 6,
                    'atributo_principal': 'Inteligência',
                    'conjuracao': {
                        'atributo': 'Inteligência',
                        'escola': 'Arcana'
                    }
                }
            }
        ]
        
        for classe_data in classes_t20:
            ConteudoSistema.objects.get_or_create(
                sistema_jogo=sistema,
                tipo='classe',
                nome=classe_data['nome'],
                defaults={
                    'descricao': classe_data['descricao'],
                    'dados_originais': classe_data['dados_originais']
                }
            )