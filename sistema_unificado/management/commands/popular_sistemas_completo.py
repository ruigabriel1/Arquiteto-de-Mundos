"""
Comando COMPLETO para popular o banco com TODOS os dados de Tormenta 20 e D&D 5e
Baseado nos livros oficiais
"""

from django.core.management.base import BaseCommand
from sistema_unificado.models import SistemaJogo, ConteudoSistema


class Command(BaseCommand):
    help = 'Popula o banco com TODOS os dados completos de Tormenta 20 e D&D 5e'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população COMPLETA dos sistemas...')
        
        # Criar sistemas
        self.criar_sistemas()
        
        # Popular D&D 5e COMPLETO
        self.popular_dnd5e_completo()
        
        # Popular Tormenta 20 COMPLETO
        self.popular_tormenta20_completo()
        
        self.stdout.write(
            self.style.SUCCESS('Sistemas populados COMPLETAMENTE com sucesso!')
        )

    def criar_sistemas(self):
        """Criar os sistemas de jogo"""
        sistemas = [
            {
                'nome': 'D&D 5th Edition',
                'codigo': 'dnd5e',
                'versao': '5.1',
                'descricao': 'Dungeons & Dragons 5ª Edição - Player\'s Handbook'
            },
            {
                'nome': 'Tormenta20',
                'codigo': 't20',
                'versao': '1.0',
                'descricao': 'Sistema Tormenta20 - Livro Básico'
            },
            {
                'nome': 'Sistema Unificado',
                'codigo': 'unified',
                'versao': '1.0',
                'descricao': 'Sistema unificado T20 + D&D 5e com conversão automática'
            }
        ]
        
        for sistema_data in sistemas:
            sistema, created = SistemaJogo.objects.get_or_create(
                codigo=sistema_data['codigo'],
                defaults=sistema_data
            )
            if created:
                self.stdout.write(f'Criado sistema: {sistema.nome}')

    def popular_dnd5e_completo(self):
        """Popular TODAS as raças e classes D&D 5e"""
        sistema = SistemaJogo.objects.get(codigo='dnd5e')
        
        # TODAS as Raças D&D 5e do Player's Handbook
        racas_dnd5e = [
            {
                'nome': 'Humano',
                'descricao': 'A raça mais versátil e adaptável dos mundos de D&D',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 30,
                    'bonus_atributos': {'todos': 1},
                    'idiomas': ['Comum', 'Um idioma adicional à sua escolha'],
                    'tracos': ['Perícia adicional', 'Talento adicional (Humano Variante)'],
                    'expectativa_vida': '80-100 anos',
                    'altura': '1,50-1,90m',
                    'peso': '50-100kg'
                }
            },
            {
                'nome': 'Elfo',
                'descricao': 'Seres mágicos longevos com conexão com a natureza e magia',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 30,
                    'bonus_atributos': {'destreza': 2},
                    'idiomas': ['Comum', 'Élfico'],
                    'tracos': ['Visão no Escuro (18m)', 'Percepção aguçada', 'Ancestral Feérico', 'Transe (4h em vez de 8h de sono)'],
                    'expectativa_vida': '700+ anos',
                    'altura': '1,50-1,80m',
                    'peso': '40-70kg',
                    'subtypes': {
                        'Alto Elfo': {'inteligencia': 1, 'extras': ['Truque de mago', 'Proficiência com armas élficas']},
                        'Elfo da Floresta': {'sabedoria': 1, 'extras': ['Proficiência com armas élficas', 'Pés Ligeiros', 'Máscara da Natureza']},
                        'Elfo Negro (Drow)': {'carisma': 1, 'extras': ['Visão no Escuro Superior (36m)', 'Sensibilidade à Luz Solar', 'Magia Drow']}
                    }
                }
            },
            {
                'nome': 'Anão',
                'descricao': 'Povo robusto das montanhas, mestres da forja e artesanato',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 25,
                    'bonus_atributos': {'constituicao': 2},
                    'idiomas': ['Comum', 'Anão'],
                    'tracos': ['Visão no Escuro (18m)', 'Resistência Anã', 'Proficiências Anãs', 'Conhecimento de Pedra'],
                    'expectativa_vida': '300-400 anos',
                    'altura': '1,20-1,50m',
                    'peso': '60-100kg',
                    'subtypes': {
                        'Anão da Montanha': {'forca': 2, 'extras': ['Proficiência com armaduras']},
                        'Anão da Colina': {'sabedoria': 1, 'extras': ['Tenacidade Anã (+1 PV por nível)']}
                    }
                }
            },
            {
                'nome': 'Halfling',
                'descricao': 'Pequenos seres ágeis e sortudos, amantes do conforto',
                'dados_originais': {
                    'tamanho': 'Pequeno',
                    'deslocamento': 25,
                    'bonus_atributos': {'destreza': 2},
                    'idiomas': ['Comum', 'Halfling'],
                    'tracos': ['Sortudo', 'Corajoso', 'Agilidade Halfling'],
                    'expectativa_vida': '150 anos',
                    'altura': '0,90-1,20m',
                    'peso': '20-30kg',
                    'subtypes': {
                        'Pés Ligeiros': {'carisma': 1, 'extras': ['Furtividade Natural']},
                        'Robusto': {'constituicao': 1, 'extras': ['Resistência a venenos']}
                    }
                }
            },
            {
                'nome': 'Draconato',
                'descricao': 'Descendentes de dragões com sopro ancestral',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 30,
                    'bonus_atributos': {'forca': 2, 'carisma': 1},
                    'idiomas': ['Comum', 'Dracônico'],
                    'tracos': ['Ancestralidade Dracônica', 'Arma de Sopro', 'Resistência a Dano'],
                    'expectativa_vida': '80 anos',
                    'altura': '1,80-2,10m',
                    'peso': '100-140kg'
                }
            },
            {
                'nome': 'Gnomo',
                'descricao': 'Pequenos inventores e estudiosos da magia',
                'dados_originais': {
                    'tamanho': 'Pequeno',
                    'deslocamento': 25,
                    'bonus_atributos': {'inteligencia': 2},
                    'idiomas': ['Comum', 'Gnômico'],
                    'tracos': ['Visão no Escuro (18m)', 'Astúcia Gnômica'],
                    'expectativa_vida': '350-500 anos',
                    'altura': '0,90-1,20m',
                    'peso': '18-25kg',
                    'subtypes': {
                        'Gnomo da Floresta': {'destreza': 1, 'extras': ['Ilusionista Natural', 'Falar com Bestas']},
                        'Gnomo das Rochas': {'constituicao': 1, 'extras': ['Conhecimento de Artífice', 'Engenhoqueiro']}
                    }
                }
            },
            {
                'nome': 'Meio-elfo',
                'descricao': 'Híbridos entre humanos e elfos, versáteis socialmente',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 30,
                    'bonus_atributos': {'carisma': 2, 'livre1': 1, 'livre2': 1},
                    'idiomas': ['Comum', 'Élfico', 'Um adicional'],
                    'tracos': ['Visão no Escuro (18m)', 'Ancestral Feérico', 'Versatilidade em Perícias'],
                    'expectativa_vida': '180 anos',
                    'altura': '1,50-1,80m',
                    'peso': '45-80kg'
                }
            },
            {
                'nome': 'Meio-orc',
                'descricao': 'Híbridos fortes com herança orc',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 30,
                    'bonus_atributos': {'forca': 2, 'constituicao': 1},
                    'idiomas': ['Comum', 'Orc'],
                    'tracos': ['Visão no Escuro (18m)', 'Resistência Implacável', 'Ataques Selvagens'],
                    'expectativa_vida': '75 anos',
                    'altura': '1,80-2,10m',
                    'peso': '80-120kg'
                }
            },
            {
                'nome': 'Tiefling',
                'descricao': 'Humanos com herança infernal',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 30,
                    'bonus_atributos': {'inteligencia': 1, 'carisma': 2},
                    'idiomas': ['Comum', 'Infernal'],
                    'tracos': ['Visão no Escuro (18m)', 'Resistência Infernal', 'Legado Infernal'],
                    'expectativa_vida': '90-100 anos',
                    'altura': '1,50-1,90m',
                    'peso': '50-100kg'
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
        
        # TODAS as Classes D&D 5e
        classes_dnd5e = [
            {
                'nome': 'Bárbaro',
                'descricao': 'Guerreiro primitivo movido pela fúria',
                'dados_originais': {
                    'dado_vida': 12,
                    'pv_nivel1': 12,
                    'proficiencias_saving': ['Força', 'Constituição'],
                    'proficiencias_armadura': ['Leve', 'Média', 'Escudos'],
                    'proficiencias_arma': ['Simples', 'Marciais'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['Adestrar Animais', 'Atletismo', 'Intimidação', 'Natureza', 'Percepção', 'Sobrevivência'],
                    'atributo_principal': 'Força',
                    'habilidades_especiais': ['Fúria', 'Defesa sem Armadura']
                }
            },
            {
                'nome': 'Bardo',
                'descricao': 'Mestre das palavras, música e magia',
                'dados_originais': {
                    'dado_vida': 8,
                    'pv_nivel1': 8,
                    'proficiencias_saving': ['Destreza', 'Carisma'],
                    'proficiencias_armadura': ['Leve'],
                    'proficiencias_arma': ['Simples', 'Espada longa', 'Rapieira', 'Espada curta', 'Besta de mão'],
                    'pericias_escolhas': 3,
                    'pericias_disponiveis': 'Qualquer',
                    'atributo_principal': 'Carisma',
                    'conjuracao': {
                        'atributo': 'Carisma',
                        'conhece_magias': True,
                        'ritual': True
                    },
                    'habilidades_especiais': ['Inspiração Bárdica', 'Versatilidade']
                }
            },
            {
                'nome': 'Clérigo',
                'descricao': 'Campeão divino com poderes sagrados',
                'dados_originais': {
                    'dado_vida': 8,
                    'pv_nivel1': 8,
                    'proficiencias_saving': ['Sabedoria', 'Carisma'],
                    'proficiencias_armadura': ['Leve', 'Média', 'Escudos'],
                    'proficiencias_arma': ['Simples'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['História', 'Intuição', 'Medicina', 'Persuasão', 'Religião'],
                    'atributo_principal': 'Sabedoria',
                    'conjuracao': {
                        'atributo': 'Sabedoria',
                        'prepara_magias': True,
                        'ritual': True
                    },
                    'habilidades_especiais': ['Canalizar Divindade', 'Domínio Divino']
                }
            },
            {
                'nome': 'Druida',
                'descricao': 'Guardião da natureza com poderes primordiais',
                'dados_originais': {
                    'dado_vida': 8,
                    'pv_nivel1': 8,
                    'proficiencias_saving': ['Inteligência', 'Sabedoria'],
                    'proficiencias_armadura': ['Leve', 'Média (não-metal)', 'Escudos (não-metal)'],
                    'proficiencias_arma': ['Cimitarra', 'Clava', 'Adaga', 'Dardo', 'Azagaia', 'Maça', 'Bordão', 'Lança', 'Funda'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['Arcanismo', 'Adestrar Animais', 'Intuição', 'Medicina', 'Natureza', 'Percepção', 'Religião', 'Sobrevivência'],
                    'atributo_principal': 'Sabedoria',
                    'conjuracao': {
                        'atributo': 'Sabedoria',
                        'prepara_magias': True,
                        'ritual': True
                    },
                    'habilidades_especiais': ['Druídico', 'Forma Selvagem']
                }
            },
            {
                'nome': 'Guerreiro',
                'descricao': 'Mestre das armas e táticas de combate',
                'dados_originais': {
                    'dado_vida': 10,
                    'pv_nivel1': 10,
                    'proficiencias_saving': ['Força', 'Constituição'],
                    'proficiencias_armadura': ['Leve', 'Média', 'Pesada', 'Escudos'],
                    'proficiencias_arma': ['Simples', 'Marciais'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['Acrobacia', 'Adestrar Animais', 'Atletismo', 'História', 'Intimidação', 'Intuição', 'Percepção', 'Sobrevivência'],
                    'atributo_principal': 'Força ou Destreza',
                    'habilidades_especiais': ['Estilo de Luta', 'Surto de Ação', 'Ataques Múltiplos']
                }
            },
            {
                'nome': 'Ladino',
                'descricao': 'Especialista em furtividade e ataques precisos',
                'dados_originais': {
                    'dado_vida': 8,
                    'pv_nivel1': 8,
                    'proficiencias_saving': ['Destreza', 'Inteligência'],
                    'proficiencias_armadura': ['Leve'],
                    'proficiencias_arma': ['Simples', 'Espada longa', 'Rapieira', 'Espada curta', 'Besta de mão'],
                    'pericias_escolhas': 4,
                    'pericias_disponiveis': ['Acrobacia', 'Atletismo', 'Enganação', 'Furtividade', 'Intimidação', 'Intuição', 'Investigação', 'Percepção', 'Performance', 'Persuasão', 'Prestidigitação', 'Sobrevivência'],
                    'atributo_principal': 'Destreza',
                    'habilidades_especiais': ['Ataque Furtivo', 'Gíria de Ladrão', 'Esquiva Sobrenatural']
                }
            },
            {
                'nome': 'Mago',
                'descricao': 'Estudioso das artes arcanas e magia',
                'dados_originais': {
                    'dado_vida': 6,
                    'pv_nivel1': 6,
                    'proficiencias_saving': ['Inteligência', 'Sabedoria'],
                    'proficiencias_armadura': [],
                    'proficiencias_arma': ['Adaga', 'Dardo', 'Funda', 'Bordão', 'Besta leve'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['Arcanismo', 'História', 'Intuição', 'Investigação', 'Medicina', 'Religião'],
                    'atributo_principal': 'Inteligência',
                    'conjuracao': {
                        'atributo': 'Inteligência',
                        'conhece_magias': True,
                        'ritual': True,
                        'grimorio': True
                    },
                    'habilidades_especiais': ['Recuperação Arcana', 'Tradição Arcana']
                }
            },
            {
                'nome': 'Monge',
                'descricao': 'Guerreiro místico que canaliza energia interna',
                'dados_originais': {
                    'dado_vida': 8,
                    'pv_nivel1': 8,
                    'proficiencias_saving': ['Força', 'Destreza'],
                    'proficiencias_armadura': [],
                    'proficiencias_arma': ['Simples', 'Espada curta'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['Acrobacia', 'Atletismo', 'História', 'Intuição', 'Religião', 'Furtividade'],
                    'atributo_principal': 'Destreza e Sabedoria',
                    'habilidades_especiais': ['Defesa sem Armadura', 'Artes Marciais', 'Ki']
                }
            },
            {
                'nome': 'Paladino',
                'descricao': 'Guerreiro sagrado com votos divinos',
                'dados_originais': {
                    'dado_vida': 10,
                    'pv_nivel1': 10,
                    'proficiencias_saving': ['Sabedoria', 'Carisma'],
                    'proficiencias_armadura': ['Leve', 'Média', 'Pesada', 'Escudos'],
                    'proficiencias_arma': ['Simples', 'Marciais'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['Atletismo', 'Intimidação', 'Intuição', 'Medicina', 'Persuasão', 'Religião'],
                    'atributo_principal': 'Força e Carisma',
                    'conjuracao': {
                        'atributo': 'Carisma',
                        'prepara_magias': True,
                        'nivel_minimo': 2
                    },
                    'habilidades_especiais': ['Sentido Divino', 'Cura Divina', 'Juramento Sagrado']
                }
            },
            {
                'nome': 'Patrulheiro',
                'descricao': 'Guerreiro da natureza e caçador especializado',
                'dados_originais': {
                    'dado_vida': 10,
                    'pv_nivel1': 10,
                    'proficiencias_saving': ['Força', 'Destreza'],
                    'proficiencias_armadura': ['Leve', 'Média', 'Escudos'],
                    'proficiencias_arma': ['Simples', 'Marciais'],
                    'pericias_escolhas': 3,
                    'pericias_disponiveis': ['Adestrar Animais', 'Atletismo', 'Intuição', 'Investigação', 'Natureza', 'Percepção', 'Furtividade', 'Sobrevivência'],
                    'atributo_principal': 'Destreza e Sabedoria',
                    'conjuracao': {
                        'atributo': 'Sabedoria',
                        'conhece_magias': True,
                        'nivel_minimo': 2
                    },
                    'habilidades_especiais': ['Inimigo Favorito', 'Terreno Favorito', 'Companheiro Animal']
                }
            },
            {
                'nome': 'Feiticeiro',
                'descricao': 'Conjurador inato com magia no sangue',
                'dados_originais': {
                    'dado_vida': 6,
                    'pv_nivel1': 6,
                    'proficiencias_saving': ['Constituição', 'Carisma'],
                    'proficiencias_armadura': [],
                    'proficiencias_arma': ['Adaga', 'Dardo', 'Funda', 'Bordão', 'Besta leve'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['Arcanismo', 'Enganação', 'Intuição', 'Intimidação', 'Persuasão', 'Religião'],
                    'atributo_principal': 'Carisma',
                    'conjuracao': {
                        'atributo': 'Carisma',
                        'conhece_magias': True
                    },
                    'habilidades_especiais': ['Origem da Feitiçaria', 'Pontos de Feitiçaria', 'Metamagia']
                }
            },
            {
                'nome': 'Bruxo',
                'descricao': 'Conjurador que fez pacto com entidade extraplanar',
                'dados_originais': {
                    'dado_vida': 8,
                    'pv_nivel1': 8,
                    'proficiencias_saving': ['Sabedoria', 'Carisma'],
                    'proficiencias_armadura': ['Leve'],
                    'proficiencias_arma': ['Simples'],
                    'pericias_escolhas': 2,
                    'pericias_disponiveis': ['Arcanismo', 'Enganação', 'História', 'Intimidação', 'Investigação', 'Natureza', 'Religião'],
                    'atributo_principal': 'Carisma',
                    'conjuracao': {
                        'atributo': 'Carisma',
                        'conhece_magias': True,
                        'slots_especiais': True
                    },
                    'habilidades_especiais': ['Patrono Transcendental', 'Invocações Místicas']
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
        
        self.stdout.write(f'Populado D&D 5e: {len(racas_dnd5e)} raças, {len(classes_dnd5e)} classes')

    def popular_tormenta20_completo(self):
        """Popular TODAS as raças e classes Tormenta20"""
        sistema = SistemaJogo.objects.get(codigo='t20')
        
        # TODAS as Raças Tormenta20
        racas_t20 = [
            {
                'nome': 'Humano',
                'descricao': 'A raça mais comum e versátil de Arton',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 9,
                    'bonus_atributos': {'livre1': 2, 'livre2': 1},
                    'idiomas': ['Valkar', 'Um idioma regional'],
                    'tracos': ['Versátil', 'Perícia adicional', 'Talento adicional']
                }
            },
            {
                'nome': 'Elfo',
                'descricao': 'Descendentes dos primeiros elfos, ligados à magia',
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
                'descricao': 'Povo das montanhas, mestres da forja e artesanato',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 6,
                    'bonus_atributos': {'constituicao': 2, 'sabedoria': 1},
                    'idiomas': ['Valkar', 'Anão'],
                    'tracos': ['Visão na Penumbra', 'Tradição de Ofício', 'Resistência Anã']
                }
            },
            {
                'nome': 'Halfling',
                'descricao': 'Pequenos e corajosos, amantes da boa vida',
                'dados_originais': {
                    'tamanho': 'Pequeno',
                    'deslocamento': 6,
                    'bonus_atributos': {'destreza': 2, 'carisma': 1},
                    'idiomas': ['Valkar', 'Halfling'],
                    'tracos': ['Sortudo', 'Corajoso', 'Tamanho Pequeno']
                }
            },
            {
                'nome': 'Golem',
                'descricao': 'Construtos criados pelos anões, seres artificiais',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 6,
                    'bonus_atributos': {'forca': 2, 'constituicao': 1},
                    'idiomas': ['Valkar', 'Anão'],
                    'tracos': ['Construto', 'Resistência Elemental', 'Slam Natural']
                }
            },
            {
                'nome': 'Qareen',
                'descricao': 'Gênios do deserto com poderes elementais',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 9,
                    'bonus_atributos': {'inteligencia': 2, 'carisma': 1},
                    'idiomas': ['Valkar', 'Qareen'],
                    'tracos': ['Herança Elemental', 'Resistência Elemental', 'Magia Inata']
                }
            },
            {
                'nome': 'Kliren',
                'descricao': 'Meio-elementais nascidos da união com espíritos',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 9,
                    'bonus_atributos': {'constituicao': 1, 'livre': 2},
                    'idiomas': ['Valkar', 'Primordial'],
                    'tracos': ['Corpo Elemental', 'Resistência', 'Conexão Elemental']
                }
            },
            {
                'nome': 'Minotauro',
                'descricao': 'Touros humanoides, guerreiros orgulhosos',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 9,
                    'bonus_atributos': {'forca': 2, 'constituicao': 1},
                    'idiomas': ['Valkar', 'Minotauro'],
                    'tracos': ['Chifradas', 'Sentidos Aguçados', 'Fúria']
                }
            },
            {
                'nome': 'Lefou',
                'descricao': 'Marcados pela Tormenta, mas mantêm sua humanidade',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 9,
                    'bonus_atributos': {'livre1': 2, 'livre2': 2},
                    'idiomas': ['Valkar', 'Um regional'],
                    'tracos': ['Marca da Tormenta', 'Poder da Tormenta', 'Resistência']
                }
            },
            {
                'nome': 'Osteon',
                'descricao': 'Mortos-vivos conscientes, esqueletos animados',
                'dados_originais': {
                    'tamanho': 'Médio',
                    'deslocamento': 9,
                    'bonus_atributos': {'inteligencia': 2, 'sabedoria': 1},
                    'idiomas': ['Valkar', 'Um adicional'],
                    'tracos': ['Morto-vivo', 'Resistência a necromancia', 'Não precisa dormir']
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
        
        # TODAS as Classes Tormenta20
        classes_t20 = [
            {
                'nome': 'Arcanista',
                'descricao': 'Estudioso das artes mágicas arcanas',
                'dados_originais': {
                    'pv_nivel': 12,
                    'pm_nivel': 6,
                    'proficiencias': ['Armas simples'],
                    'pericias_treinadas': 6,
                    'atributo_principal': 'Inteligência',
                    'conjuracao': {
                        'atributo': 'Inteligência',
                        'escola': 'Arcana',
                        'magias_conhecidas': True
                    }
                }
            },
            {
                'nome': 'Bárbaro',
                'descricao': 'Guerreiro selvagem movido pela fúria',
                'dados_originais': {
                    'pv_nivel': 24,
                    'pm_nivel': 2,
                    'proficiencias': ['Armas simples', 'Armas marciais', 'Armaduras leves'],
                    'pericias_treinadas': 4,
                    'atributo_principal': 'Força',
                    'habilidades': ['Fúria', 'Resistência a dano']
                }
            },
            {
                'nome': 'Bardo',
                'descricao': 'Artista versátil com poderes mágicos',
                'dados_originais': {
                    'pv_nivel': 16,
                    'pm_nivel': 4,
                    'proficiencias': ['Armas simples', 'Armaduras leves'],
                    'pericias_treinadas': 8,
                    'atributo_principal': 'Carisma',
                    'conjuracao': {
                        'atributo': 'Carisma',
                        'escola': 'Universal',
                        'magias_conhecidas': True
                    }
                }
            },
            {
                'nome': 'Bucaneiro',
                'descricao': 'Aventureiro dos mares e explorador',
                'dados_originais': {
                    'pv_nivel': 16,
                    'pm_nivel': 4,
                    'proficiencias': ['Armas simples', 'Armas de fogo', 'Armaduras leves'],
                    'pericias_treinadas': 8,
                    'atributo_principal': 'Destreza',
                    'habilidades': ['Audácia', 'Esquiva Aprimorada']
                }
            },
            {
                'nome': 'Caçador',
                'descricao': 'Especialista em rastreamento e sobrevivência',
                'dados_originais': {
                    'pv_nivel': 20,
                    'pm_nivel': 3,
                    'proficiencias': ['Armas simples', 'Armas marciais', 'Armaduras leves', 'Armaduras médias'],
                    'pericias_treinadas': 6,
                    'atributo_principal': 'Destreza ou Sabedoria'
                }
            },
            {
                'nome': 'Cavaleiro',
                'descricao': 'Guerreiro nobre montado em sua montaria',
                'dados_originais': {
                    'pv_nivel': 20,
                    'pm_nivel': 3,
                    'proficiencias': ['Armas simples', 'Armas marciais', 'Armaduras leves', 'Armaduras pesadas', 'Escudos'],
                    'pericias_treinadas': 4,
                    'atributo_principal': 'Força',
                    'habilidades': ['Montaria', 'Investida']
                }
            },
            {
                'nome': 'Clérigo',
                'descricao': 'Servo divino com poderes sagrados',
                'dados_originais': {
                    'pv_nivel': 16,
                    'pm_nivel': 5,
                    'proficiencias': ['Armas simples', 'Armaduras leves', 'Armaduras médias', 'Escudos'],
                    'pericias_treinadas': 4,
                    'atributo_principal': 'Sabedoria',
                    'conjuracao': {
                        'atributo': 'Sabedoria',
                        'escola': 'Divina',
                        'prepara_magias': True
                    }
                }
            },
            {
                'nome': 'Druida',
                'descricao': 'Guardião da natureza com poderes primais',
                'dados_originais': {
                    'pv_nivel': 16,
                    'pm_nivel': 5,
                    'proficiencias': ['Armas simples', 'Armaduras leves (não-metal)'],
                    'pericias_treinadas': 6,
                    'atributo_principal': 'Sabedoria',
                    'conjuracao': {
                        'atributo': 'Sabedoria',
                        'escola': 'Divina',
                        'prepara_magias': True
                    },
                    'habilidades': ['Forma Selvagem', 'Empatia Selvagem']
                }
            },
            {
                'nome': 'Guerreiro',
                'descricao': 'Especialista em combate e armas',
                'dados_originais': {
                    'pv_nivel': 20,
                    'pm_nivel': 2,
                    'proficiencias': ['Armas simples', 'Armas marciais', 'Armaduras leves', 'Armaduras pesadas', 'Escudos'],
                    'pericias_treinadas': 4,
                    'atributo_principal': 'Força ou Destreza',
                    'habilidades': ['Ataques Múltiplos', 'Especialização']
                }
            },
            {
                'nome': 'Inventor',
                'descricao': 'Criador de dispositivos tecnológicos',
                'dados_originais': {
                    'pv_nivel': 12,
                    'pm_nivel': 6,
                    'proficiencias': ['Armas simples', 'Armas de fogo'],
                    'pericias_treinadas': 8,
                    'atributo_principal': 'Inteligência',
                    'habilidades': ['Inventos', 'Engenhoqueiro']
                }
            },
            {
                'nome': 'Ladino',
                'descricao': 'Especialista em furtividade e ataques precisos',
                'dados_originais': {
                    'pv_nivel': 16,
                    'pm_nivel': 4,
                    'proficiencias': ['Armas simples', 'Armaduras leves'],
                    'pericias_treinadas': 12,
                    'atributo_principal': 'Destreza',
                    'habilidades': ['Ataque Furtivo', 'Esquiva Sobrenatural']
                }
            },
            {
                'nome': 'Lutador',
                'descricao': 'Guerreiro desarmado especialista em combate corpo a corpo',
                'dados_originais': {
                    'pv_nivel': 20,
                    'pm_nivel': 4,
                    'proficiencias': ['Armas simples'],
                    'pericias_treinadas': 4,
                    'atributo_principal': 'Força ou Destreza',
                    'habilidades': ['Artes Marciais', 'Golpes Especiais']
                }
            },
            {
                'nome': 'Nobre',
                'descricao': 'Aristocrata com influência social e recursos',
                'dados_originais': {
                    'pv_nivel': 16,
                    'pm_nivel': 4,
                    'proficiencias': ['Armas simples', 'Armaduras leves'],
                    'pericias_treinadas': 8,
                    'atributo_principal': 'Carisma',
                    'habilidades': ['Recursos', 'Influência Social']
                }
            },
            {
                'nome': 'Paladino',
                'descricao': 'Guerreiro sagrado com votos divinos',
                'dados_originais': {
                    'pv_nivel': 20,
                    'pm_nivel': 3,
                    'proficiencias': ['Armas simples', 'Armas marciais', 'Armaduras leves', 'Armaduras pesadas', 'Escudos'],
                    'pericias_treinadas': 4,
                    'atributo_principal': 'Força ou Destreza',
                    'conjuracao': {
                        'atributo': 'Carisma',
                        'escola': 'Divina',
                        'prepara_magias': True,
                        'nivel_minimo': 2
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
        
        self.stdout.write(f'Populado Tormenta20: {len(racas_t20)} raças, {len(classes_t20)} classes')