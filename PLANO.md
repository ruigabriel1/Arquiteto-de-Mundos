Compêndio de Dados Estruturados para Aplicações de RPG: D&D 5e e Tormenta 20Parte I: Compêndio de Dados de Dungeons & Dragons 5th EditionEsta parte fornece um conjunto de dados completo e estruturado para o sistema Dungeons & Dragons 5th Edition, projetado para integração direta em uma aplicação web. Inicia-se com uma explicação detalhada da arquitetura de dados em formato JSON, seguida pelos dados populados para raças, classes e equipamentos.Seção 1.1: Arquitetura de Dados para D&D 5eEsta seção define a estrutura JSON utilizada ao longo da Parte I. A arquitetura foi concebida para ser relacional, hierárquica e de fácil análise programática, permitindo que a aplicação do utilizador gere dinamicamente opções de personagem e calcule estatísticas.Estrutura de Nível SuperiorA raiz do arquivo JSON será um objeto denominado dnd5e, contendo quatro chaves primárias: races, classes, weapons e equipment. Esta separação garante modularidade e facilidade de acesso a categorias de dados distintas.Esquema de racesA chave races conterá um array de objetos, onde cada objeto representa uma raça jogável. A estrutura de cada objeto racial é a seguinte:JSON{
  "name": "String",
  "description": "String",
  "ability_score_increase": {
    "Strength": "Integer",
    "Dexterity": "Integer",
    "Constitution": "Integer",
    "Intelligence": "Integer",
    "Wisdom": "Integer",
    "Charisma": "Integer",
    "choice": {
      "choose": "Integer",
      "from":
    }
  },
  "size": "String",
  "speed": "Integer",
  "languages":,
  "traits":,
  "subraces":
    }
  ]
}
A inclusão de sub-raças (subraces) como um array aninhado dentro do objeto da raça principal é uma decisão de design deliberada. O sistema de regras de D&D 5e baseia-se num modelo de herança, onde uma sub-raça herda todas as características da sua raça parental, adicionando as suas próprias características únicas.1 Uma estrutura de dados plana exigiria que o desenvolvedor reconstruísse manualmente essa relação, resultando em código mais complexo e propenso a erros. Ao aninhar os dados, a lógica da aplicação pode simplesmente agregar as características da raça base com as da sub-raça selecionada, espelhando diretamente a mecânica do jogo e simplificando o desenvolvimento.Esquema de classesA chave classes conterá um array de objetos de classe, cada um com a seguinte estrutura:JSON{
  "name": "String",
  "description": "String",
  "hit_die": "String",
  "primary_abilities":,
  "saving_throw_proficiencies":,
  "proficiencies": {
    "armor":,
    "weapons":,
    "tools":,
    "skills": {
      "choose": "Integer",
      "from":
    }
  },
  "starting_equipment": "String",
  "class_features":
    }
  ],
  "subclass_archetype_name": "String",
  "subclass_level": "Integer",
  "subclasses":
    }
  ]
}
Muitas características de classe evoluem com o nível do personagem (por exemplo, o dano do Ataque Furtivo do Ladino) ou oferecem escolhas (por exemplo, o Estilo de Luta do Guerreiro). Para acomodar isso, a estrutura class_features inclui campos opcionais como progression e choices. O campo progression pode mapear níveis para valores específicos (por exemplo, {"1": "1d6", "3": "2d6",...}), permitindo que a aplicação calcule dinamicamente os bónus. O campo choices conteria um array de opções, cada uma com nome e descrição, permitindo que a interface do utilizador apresente as escolhas relevantes ao jogador. Esta abordagem torna os dados "inteligentes", codificando a lógica de progressão e escolha diretamente na estrutura, o que reduz a quantidade de lógica de jogo que precisa ser codificada na aplicação.Esquema de weapons e equipmentAs chaves weapons e equipment conterão arrays de objetos com estruturas simples para catalogar itens.Esquema de weapons:JSON{
  "name": "String",
  "cost": "String",
  "damage_dice": "String",
  "damage_type": "String",
  "weight": "String",
  "category": "String",
  "properties":
}
Esquema de equipment:JSON{
  "name": "String",
  "category": "String",
  "cost": "String",
  "weight": "String"
}
Seção 1.2: Raças e Sub-raças JogáveisEsta seção contém os dados completos para as raças e sub-raças de D&D 5e, formatados de acordo com o esquema definido na Seção 1.1. Os dados foram compilados e sintetizados a partir de múltiplas fontes para garantir a sua completude.1Raças do Player's HandbookJSON[
  {
    "name": "Anão",
    "description": "Corajosos e resistentes, os anões são conhecidos como hábeis guerreiros, mineiros e trabalhadores de pedra e metal. Embora tenham menos de 1,50 metro de altura, os anões são tão largos e compactos que podem pesar tanto quanto um humano com quase 60 centímetros a mais.",
    "ability_score_increase": { "Constitution": 2 },
    "size": "Médio",
    "speed": 25,
    "languages": ["Comum", "Anão"],
    "traits":,
    "subraces":
      },
      {
        "name": "Anão da Montanha",
        "ability_score_increase": { "Strength": 2 },
        "traits":
      }
    ]
  },
  {
    "name": "Elfo",
    "description": "Elfos são um povo mágico de graça sobrenatural, vivendo no mundo mas não inteiramente parte dele. Eles vivem em lugares de beleza etérea, no meio de florestas antigas ou em torres prateadas que brilham com luz feérica.",
    "ability_score_increase": { "Dexterity": 2 },
    "size": "Médio",
    "speed": 30,
    "languages": ["Comum", "Élfico"],
    "traits":,
    "subraces":
      },
      {
        "name": "Elfo da Floresta",
        "ability_score_increase": { "Wisdom": 1 },
        "traits":
      },
      {
        "name": "Elfo Negro (Drow)",
        "ability_score_increase": { "Charisma": 1 },
        "traits":
      }
    ]
  },
  {
    "name": "Humano",
    "description": "Os humanos são a mais jovem das raças comuns, de vida curta e mais adaptáveis e ambiciosos do que as outras raças. Suas motivações são variadas, tornando-os versáteis e capazes de se destacar em muitas áreas.",
    "ability_score_increase": { "Strength": 1, "Dexterity": 1, "Constitution": 1, "Intelligence": 1, "Wisdom": 1, "Charisma": 1 },
    "size": "Médio",
    "speed": 30,
    "languages": ["Comum", "Um idioma adicional de sua escolha"],
    "traits":,
    "subraces": } },
        "traits":
      }
    ]
  }
]
Raças ExpandidasAlém das raças do livro base, o universo de D&D 5e inclui uma vasta gama de outras opções provenientes de suplementos oficiais. A lista a seguir, compilada a partir de fontes como o Volo's Guide to Monsters e o Mordenkainen's Tome of Foes, será estruturada da mesma forma.4Aasimar: Com as sub-raças Caído, Protetor e Flagelo.Firbolg: Gigantes gentis com magia druídica inata.Goliath: Humanoides montanheses fortes e competitivos.Kenku: Povo-pássaro amaldiçoado sem voz própria, que se comunica através da mímica.Lizardfolk: Répteis pragmáticos e sobreviventes dos pântanos.Tabaxi: Humanoides felinos curiosos e ágeis.Tritão: Guardiões dos oceanos profundos.Yuan-ti Pureblood: Humanoides com sangue de serpente, imunes a veneno e com resistência mágica.Bugbear, Goblin, Hobgoblin, Kobold, Orc: Raças tradicionalmente monstruosas, apresentadas como opções jogáveis.Gith: Com as sub-raças Githyanki e Githzerai, guerreiros psiónicos do Plano Astral.A tabela a seguir fornece uma referência rápida aos modificadores de atributos de cada raça, uma ferramenta essencial para a funcionalidade de filtragem na aplicação do utilizador.RaçaSub-raçaFORDESCONINTSABCARFlexível/EscolhaAnão-00+2000-Anão da Colina00+20+10-Anão da Montanha+20+2000-Elfo-0+20000-Alto Elfo0+20+100-Elfo da Floresta0+200+10-Elfo Negro (Drow)0+2000+1-Halfling-0+20000-Pés Leves0+2000+1-Robusto0+2+1000-HumanoPadrão+1+1+1+1+1+1-Variante------+1 em dois atributosDraconato-+20000+1-Gnomo-000+200-Gnomo da Floresta0+10+200-Gnomo da Pedra00+1+200-Meio-Elfo-00000+2+1 em dois outrosMeio-Orc-+20+1000-Tiefling-000+10+2-Seção 1.3: Classes de Personagem e SubclassesEsta seção apresenta os dados completos para as 13 classes oficiais de D&D 5e. Cada entrada de classe é um módulo autocontido, detalhando a progressão de nível 1 a 20 e aninhando todas as subclasses disponíveis. A compilação baseia-se numa síntese de múltiplas fontes para garantir precisão e profundidade.4A tabela seguinte resume as mecânicas centrais de cada classe, servindo como um guia de referência rápida.ClasseDado de VidaAtributo PrimárioProficiências em Testes de ResistênciaArtíficed8InteligênciaConstituição, InteligênciaBárbarod12ForçaForça, ConstituiçãoBardod8CarismaDestreza, CarismaBruxod8CarismaSabedoria, CarismaClérigod8SabedoriaSabedoria, CarismaDruidad8SabedoriaInteligência, SabedoriaFeiticeirod6CarismaConstituição, CarismaGuerreirod10Força ou DestrezaForça, ConstituiçãoLadinod8DestrezaDestreza, InteligênciaMagod6InteligênciaInteligência, SabedoriaMonged8Destreza, SabedoriaForça, DestrezaPaladinod10Força, CarismaSabedoria, CarismaPatrulheirod10Destreza, SabedoriaForça, DestrezaA seguir, apresentam-se os dados estruturados para cada classe.BárbaroJSON{
  "name": "Bárbaro",
  "description": "Um guerreiro feroz de fúria primal. Para cada Bárbaro, a fúria é um poder que alimenta não apenas a sua proeza em batalha, mas também reflexos, resiliência e feitos de força sobre-humanos.",
  "hit_die": "d12",
  "primary_abilities": ["Força"],
  "saving_throw_proficiencies": ["Força", "Constituição"],
  "proficiencies": {
    "armor": ["Armaduras leves", "Armaduras médias", "Escudos"],
    "weapons": ["Armas simples", "Armas marciais"],
    "tools":,
    "skills": {
      "choose": 2,
      "from":
    }
  },
  "starting_equipment": "Você começa com o seguinte equipamento: (a) um machado grande ou (b) qualquer arma marcial corpo a corpo; (a) duas machadinhas ou (b) qualquer arma simples; Um pacote de explorador e quatro azagaias.",
  "class_features":,
  "subclass_archetype_name": "Caminho Primal",
  "subclass_level": 3,
  "subclasses":
    },
    {
      "name": "Caminho do Guerreiro Totêmico",
      "description": "O Caminho do Guerreiro Totêmico é uma jornada espiritual, à medida que o bárbaro aceita um espírito animal como guia, protetor e inspiração.",
      "subclass_features":
        }
      ]
    }
  ]
}
Seção 1.4: Armas, Armaduras e EquipamentosEsta seção fornece os dados estruturados para todos os equipamentos padrão do jogador, compilados a partir de fontes de regras de referência.9ArmasJSON
  },
  {
    "name": "Adaga",
    "cost": "2 po",
    "damage_dice": "1d4",
    "damage_type": "perfurante",
    "weight": "0.5 kg",
    "category": "Arma Simples Corpo a Corpo",
    "properties": ["Acuidade", "Leve", "Arremesso (alcance 6/18 m)"]
  },
  {
    "name": "Espada Longa",
    "cost": "15 po",
    "damage_dice": "1d8",
    "damage_type": "cortante",
    "weight": "1.5 kg",
    "category": "Arma Marcial Corpo a Corpo",
    "properties": ["Versátil (1d10)"]
  },
  {
    "name": "Arco Longo",
    "cost": "50 po",
    "damage_dice": "1d8",
    "damage_type": "perfurante",
    "weight": "1 kg",
    "category": "Arma Marcial à Distância",
    "properties":
  },
  {
    "name": "Rede",
    "cost": "1 po",
    "damage_dice": "-",
    "damage_type": "-",
    "weight": "1.5 kg",
    "category": "Arma Marcial à Distância",
    "properties": ["Especial", "Arremesso (alcance 1.5/4.5 m)"]
  }
]
A propriedade "Especial" em certas armas, como a Rede ou a Lança de Justa, indica regras únicas que não se enquadram nas categorias padrão.9 Para uma implementação eficaz, o objeto JSON para tal arma deve incluir uma descrição detalhada dessas regras especiais. A aplicação deve ser programada para detetar a propriedade "Especial" e exibir a descrição correspondente ao utilizador, informando-o sobre a mecânica única da arma.Equipamentos de AventuraJSON[
  {
    "name": "Ábaco",
    "category": "Equipamento de Aventura",
    "cost": "2 po",
    "weight": "1 kg"
  },
  {
    "name": "Ácido (frasco)",
    "category": "Equipamento de Aventura",
    "cost": "25 po",
    "weight": "0.5 kg"
  },
  {
    "name": "Fogo de Alquimista (frasco)",
    "category": "Equipamento de Aventura",
    "cost": "50 po",
    "weight": "0.5 kg"
  },
  {
    "name": "Antídoto (frasco)",
    "category": "Equipamento de Aventura",
    "cost": "50 po",
    "weight": "-"
  },
  {
    "name": "Mochila",
    "category": "Equipamento de Aventura",
    "cost": "2 po",
    "weight": "2.5 kg"
  }
]
Parte II: Compêndio de Dados de Tormenta 20Esta parte aborda os requisitos de dados para o sistema Tormenta 20. Devido à natureza fragmentada das fontes de pesquisa disponíveis, esta seção compilará todos os dados acessíveis, ao mesmo tempo que indicará explicitamente onde as informações estão incompletas e requerem consulta aos manuais de regras oficiais.Seção 2.1: Arquitetura de Dados para Tormenta 20Esta seção define um esquema JSON adaptado às mecânicas únicas de Tormenta 20, como o seu sistema de atributos e o sistema flexível de "Poderes".Esquema de racesSemelhante a D&D 5e, mas com uma estrutura de atributos diferente para acomodar bónus e penalidades.12JSON{
  "name": "String",
  "attribute_modifiers": {
    "Força": "Integer",
    "Destreza": "Integer",
    "Constituição": "Integer",
    "Inteligência": "Integer",
    "Sabedoria": "Integer",
    "Carisma": "Integer"
  },
  "abilities":
}
Esquema de classesEsta estrutura difere significativamente de D&D 5e para refletir a progressão e personalização de Tormenta 20.JSON{
  "name": "String",
  "pv_initial": "Integer",
  "pv_per_level": "Integer",
  "pm_per_level": "Integer",
  "pericias": {
    "initial":,
    "choose": "Integer",
    "from":
  },
  "proficiencies":,
  "class_abilities":,
  "class_powers":
}
A distinção fundamental entre os sistemas de progressão de D&D 5e e Tormenta 20 exige arquiteturas de dados diferentes. D&D 5e utiliza um modelo de "roteiro", onde uma classe ganha características predefinidas em níveis específicos. Em contraste, Tormenta 20 emprega um modelo de "biblioteca", onde, a cada nível, o jogador escolhe um "Poder" de uma vasta lista de opções disponíveis para a sua classe.14 Consequentemente, o esquema JSON para uma classe de Tormenta 20 deve conter um array abrangente de todos os class_powers possíveis, incluindo os seus pré-requisitos. A lógica da aplicação será responsável por filtrar esta lista mestra para apresentar ao utilizador apenas as opções válidas no momento da subida de nível, com base no nível atual, atributos e poderes já selecionados do personagem.Seção 2.2: Raças JogáveisEsta seção apresenta os dados compilados para as raças de Tormenta 20 com base nas fontes disponíveis.12JSON
  },
  {
    "name": "Humano",
    "attribute_modifiers": {
      "Força": 2,
      "Destreza": 2,
      "Constituição": 2,
      "Inteligência": 2,
      "Sabedoria": 2,
      "Carisma": 2
    },
    "abilities": [
      {
        "name": "Versátil",
        "description": "Você se torna treinado em duas perícias a sua escolha. Você pode trocar uma dessas perícias por um poder geral a sua escolha."
      }
    ]
  }
]
Seção 2.3: Classes de PersonagemEsta seção fornece dados estruturados para as classes de Tormenta 20 mencionadas nas fontes.15 A informação disponível é menos sistemática do que a de D&D 5e, focando-se mais em papéis e habilidades chave do que numa progressão detalhada.Lista de Classes: Arcanista, Bárbaro, Bardo, Bucaneiro, Caçador, Cavaleiro, Clérigo, Druida, Guerreiro, Inventor, Ladino, Lutador, Nobre, Paladino.15População de Dados: Cada entrada de classe será populada com os seus PV, PM, Perícias e uma lista de "Poderes" conhecidos. Esta lista será inerentemente incompleta e deve ser tratada como um modelo estrutural.Seção 2.4: Armas e EquipamentosEsta seção compila os dados limitados disponíveis sobre equipamentos de Tormenta 20.Fontes de Dados: As informações são extraídas de menções a itens específicos ou a manuais como Ameaças de Arton.18Conteúdo: Será fornecida uma lista parcial de armas (por exemplo, Açoite Finntroll, Arcabuz, Arpão 18) e equipamento de aventura geral (Mochila, Saco de Dormir 20).Aviso: Esta seção enfatizará que a lista fornecida não é exaustiva e serve como um exemplo estrutural. O desenvolvedor é fortemente aconselhado a adquirir os manuais de regras oficiais de Tormenta 20 para uma lista completa de equipamentos.Parte III: Análise de Implementação e Recomendações EstratégicasEsta parte final transita da provisão de dados para a consultoria especializada, oferecendo orientação sobre a utilização do conjunto de dados e a compreensão das filosofias de design dos dois sistemas.Seção 3.1: Orientação para Integração da AplicaçãoEsta seção fornece conselhos técnicos para o desenvolvedor web sobre como utilizar da melhor forma os dados JSON fornecidos.Análise de Dados Hierárquicos: Um guia sobre como lidar com os dados aninhados de subraces e subclasses em D&D 5e, incluindo exemplos de pseudocódigo para combinar características de pais e filhos.Gestão da Escolha do Jogador: Recomendações para construir componentes de UI que lidem com características baseadas em escolhas, como os Estilos de Luta do Guerreiro ou o sistema de "Poderes" de Tormenta 20. Isto incluirá a lógica para filtrar opções válidas com base em pré-requisitos.Cálculo de Estatísticas Derivadas: Orientação sobre o uso dos dados base para calcular estatísticas de personagem em tempo de execução, como a Classe de Armadura (por exemplo, Defesa sem Armadura do Monge: 10+modificador de DES+modificador de SAB), modificadores de perícia (incluindo Especialização) e bónus de ataque/dano.Lidar com Discrepâncias de Dados: Uma estratégia para gerir os dados incompletos de Tormenta 20, como exibir mensagens de "manual oficial necessário" para descrições em falta ou implementar uma funcionalidade para os utilizadores inserirem manualmente dados dos seus próprios livros.Seção 3.2: Perspetivas Sistémicas e Caminhos de ExpansãoEsta seção oferece uma análise de alto nível dos dois sistemas de jogo, fornecendo contexto que pode informar o desenvolvimento futuro da aplicação.O design de D&D 5e está fortemente centrado no "subclasse" ou "arquétipo" escolhido no início da carreira de um personagem. Esta escolha define um caminho com um conjunto de características predeterminadas em níveis específicos. Tormenta 20, em contraste, oferece um vasto leque de "Poderes" em quase todos os níveis, permitindo uma construção de personagem mais granular e personalizável.14 Um Guerreiro Mestre de Batalha de D&D 5e é fundamentalmente diferente de um Campeão, e os seus caminhos de progressão são fixos. Um Guerreiro de Tormenta 20 pode ser construído de inúmeras maneiras, selecionando diferentes "Poderes" a cada nível. Esta diferença de design fundamental deve refletir-se na aplicação: o construtor de personagens de D&D 5e pode ser um "assistente" mais guiado e linear, enquanto o construtor de Tormenta 20 precisa de ser uma interface de "biblioteca" mais aberta, que capacita os utilizadores a navegar e selecionar a partir de uma grande lista de opções a cada nível.Roteiro para Expansão FuturaMagias: O próximo passo lógico é a inclusão de dados de magias. Propõe-se um esquema para spells (incluindo nível, escola, tempo de conjuração, alcance, componentes, duração, descrição) e discute-se a lógica para ligar listas de magias a classes.Itens Mágicos: Esboça-se um esquema para itens mágicos, incluindo raridade, requisitos de sintonização e descrição das propriedades mágicas.Bestiário: Sugere-se um módulo futuro para estatísticas de monstros, essencial para qualquer funcionalidade integrada de construção de encontros ou ecrã digital do Mestre de Jogo.