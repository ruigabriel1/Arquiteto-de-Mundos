# Compêndio de Dados Estruturados para Aplicações de RPG: D&D 5e e Tormenta 20

## Parte I: Compêndio de Dados de Dungeons & Dragons 5th Edition

Esta parte fornece um conjunto de dados completo e estruturado para o sistema Dungeons & Dragons 5th Edition, projetado para integração direta em uma aplicação web. Inicia-se com uma explicação detalhada da arquitetura de dados em formato JSON, seguida pelos dados populados para raças, classes e equipamentos.

### Seção 1.1: Arquitetura de Dados para D&D 5e

Esta seção define a estrutura JSON utilizada ao longo da Parte I. A arquitetura foi concebida para ser relacional, hierárquica e de fácil análise programática, permitindo que a aplicação do utilizador gere dinamicamente opções de personagem e calcule estatísticas.

**Estrutura de Nível Superior**

A raiz do arquivo JSON será um objeto denominado `dnd5e`, contendo quatro chaves primárias: `races`, `classes`, `weapons` e `equipment`. Esta separação garante modularidade e facilidade de acesso a categorias de dados distintas.

**Esquema de `races`**

A chave `races` conterá um array de objetos, onde cada objeto representa uma raça jogável.

* **Nota de Design (Sub-raças Aninhadas):** A inclusão de sub-raças (`subraces`) como um array aninhado é deliberada. O sistema D&D 5e baseia-se num modelo de herança, onde uma sub-raça herda as características da raça parental. Ao aninhar os dados, a lógica da aplicação pode simplesmente agregar as características da raça base com as da sub-raça selecionada, espelhando a mecânica do jogo e simplificando o desenvolvimento.

```json
{
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
      "from": ["String"]
    }
  },
  "size": "String",
  "speed": "Integer",
  "languages": ["String"],
  "traits": ["Object"],
  "subraces": ["Object"]
}
```

**Esquema de `classes`**

A chave `classes` conterá um array de objetos de classe.

* **Nota de Design (Progressão e Escolhas):** Características de classe evoluem com o nível. A estrutura `class_features` inclui campos opcionais como `progression` (para mapear níveis a valores, ex: `{"1": "1d6", "3": "2d6"}`) e `choices` (um array de opções). Esta abordagem torna os dados "inteligentes", codificando a lógica de progressão diretamente na estrutura.

```json
{
  "name": "String",
  "description": "String",
  "hit_die": "String",
  "primary_abilities": ["String"],
  "saving_throw_proficiencies": ["String"],
  "proficiencies": {
    "armor": ["String"],
    "weapons": ["String"],
    "tools": ["String"],
    "skills": {
      "choose": "Integer",
      "from": ["String"]
    }
  },
  "starting_equipment": "String",
  "class_features": ["Object"],
  "subclass_archetype_name": "String",
  "subclass_level": "Integer",
  "subclasses": ["Object"]
}
```

**Esquema de `weapons` e `equipment`**

Estruturas simples para catalogar itens.

* **Nota de Design (Propriedade "Especial"):** Armas com a propriedade "Especial" (ex: Rede) indicam regras únicas. A aplicação deve ser programada para detetar esta propriedade e exibir uma descrição detalhada da sua mecânica única.

**Esquema de `weapons`:**
```json
{
  "name": "String",
  "cost": "String",
  "damage_dice": "String",
  "damage_type": "String",
  "weight": "String",
  "category": "String",
  "properties": ["String"]
}
```

**Esquema de `equipment`:**
```json
{
  "name": "String",
  "category": "String",
  "cost": "String",
  "weight": "String"
}
```

### Seção 1.2: Raças e Sub-raças Jogáveis

Dados completos para as raças e sub-raças de D&D 5e.

**Raças do Player's Handbook**
```json
[
  {
    "name": "Anão",
    "description": "Corajosos e resistentes, os anões são conhecidos como hábeis guerreiros, mineiros e trabalhadores de pedra e metal. Embora tenham menos de 1,50 metro de altura, os anões são tão largos e compactos que podem pesar tanto quanto um humano com quase 60 centímetros a mais.",
    "ability_score_increase": { "Constitution": 2 },
    "size": "Médio",
    "speed": 25,
    "languages": ["Comum", "Anão"],
    "traits": [],
    "subraces": [
      {
        "name": "Anão da Colina",
        "ability_score_increase": { "Wisdom": 1 },
        "traits": [
          { "name": "Resiliência Anã", "description": "Você tem vantagem em testes de resistência contra veneno e resistência a dano de veneno." }
        ]
      },
      {
        "name": "Anão da Montanha",
        "ability_score_increase": { "Strength": 2 },
        "traits": [
          { "name": "Treinamento de Armadura Anã", "description": "Você tem proficiência com armaduras leves e médias." }
        ]
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
    "traits": [
        { "name": "Visão no Escuro", "description": "Você enxerga na penumbra a até 18 metros como se fosse luz plena, e na escuridão como se fosse penumbra." },
        { "name": "Ancestral Feérico", "description": "Você tem vantagem em testes de resistência contra ser enfeitiçado e a magia não pode colocá-lo para dormir."}
    ],
    "subraces": [
      {
        "name": "Alto Elfo",
        "ability_score_increase": { "Intelligence": 1 },
        "traits": [
            { "name": "Treinamento em Armas Élficas", "description": "Você tem proficiência com espadas longas, espadas curtas, arcos curtos e arcos longos." },
            { "name": "Truque", "description": "Você conhece um truque da lista de magias do Mago. Inteligência é seu atributo de conjuração para ele."}
        ]
      },
      {
        "name": "Elfo da Floresta",
        "ability_score_increase": { "Wisdom": 1 },
        "traits": [
            { "name": "Pés Ligeiros", "description": "Seu deslocamento base aumenta para 10,5 metros." },
            { "name": "Máscara da Natureza", "description": "Você pode tentar se esconder mesmo quando estiver apenas levemente obscurecido por folhagem, chuva forte, neve caindo, névoa e outros fenômenos naturais." }
        ]
      },
      {
        "name": "Elfo Negro (Drow)",
        "ability_score_increase": { "Charisma": 1 },
        "traits": [
            { "name": "Visão no Escuro Superior", "description": "Sua visão no escuro tem um raio de 36 metros." },
            { "name": "Sensibilidade à Luz Solar", "description": "Você tem desvantagem em jogadas de ataque e testes de Sabedoria (Percepção) que dependem da visão quando você, o alvo do seu ataque ou o que você está tentando perceber está sob luz solar direta."}
        ]
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
    "traits": [],
    "subraces": []
  }
]
```

**Raças Expandidas**

Opções de suplementos oficiais como *Volo's Guide to Monsters* e *Mordenkainen's Tome of Foes*.

* **Aasimar:** Com as sub-raças Caído, Protetor e Flagelo.
* **Firbolg:** Gigantes gentis com magia druídica inata.
* **Goliath:** Humanoides montanheses fortes e competitivos.
* **Kenku:** Povo-pássaro amaldiçoado sem voz própria, que se comunica através da mímica.
* **Lizardfolk:** Répteis pragmáticos e sobreviventes dos pântanos.
* **Tabaxi:** Humanoides felinos curiosos e ágeis.
* **Tritão:** Guardiões dos oceanos profundos.
* **Yuan-ti Pureblood:** Humanoides com sangue de serpente, imunes a veneno e com resistência mágica.
* **Bugbear, Goblin, Hobgoblin, Kobold, Orc:** Raças tradicionalmente monstruosas, apresentadas como opções jogáveis.
* **Gith:** Com as sub-raças Githyanki e Githzerai, guerreiros psiónicos do Plano Astral.

**Tabela de Referência Rápida: Modificadores de Atributos**

| Raça | Sub-raça | FOR | DES | CON | INT | SAB | CAR | Flexível/Escolha |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Anão** | - | 0 | 0 | +2 | 0 | 0 | 0 | - |
| Anão | Anão da Colina | 0 | 0 | +2 | 0 | +1 | 0 | - |
| Anão | Anão da Montanha | +2 | 0 | +2 | 0 | 0 | 0 | - |
| **Elfo** | - | 0 | +2 | 0 | 0 | 0 | 0 | - |
| Elfo | Alto Elfo | 0 | +2 | 0 | +1 | 0 | 0 | - |
| Elfo | Elfo da Floresta | 0 | +2 | 0 | 0 | +1 | 0 | - |
| Elfo | Elfo Negro (Drow) | 0 | +2 | 0 | 0 | 0 | +1 | - |
| **Humano** | Padrão | +1 | +1 | +1 | +1 | +1 | +1 | - |
| Humano | Variante | - | - | - | - | - | - | +1 em dois atributos |
| **Meio-Elfo**| - | 0 | 0 | 0 | 0 | 0 | +2 | +1 em dois outros |
| **Meio-Orc** | - | +2 | 0 | +1 | 0 | 0 | 0 | - |
| **Tiefling** | - | 0 | 0 | 0 | +1 | 0 | +2 | - |


### Seção 1.3: Classes de Personagem e Subclasses

Dados para as 13 classes oficiais de D&D 5e.

**Tabela de Referência Rápida: Mecânicas de Classe**

| Classe | Dado de Vida | Atributo Primário | Proficiências em Testes de Resistência |
| :--- | :--- | :--- | :--- |
| Artífice | d8 | Inteligência | Constituição, Inteligência |
| Bárbaro | d12 | Força | Força, Constituição |
| Bardo | d8 | Carisma | Destreza, Carisma |
| Bruxo | d8 | Carisma | Sabedoria, Carisma |
| Clérigo | d8 | Sabedoria | Sabedoria, Carisma |
| Druida | d8 | Sabedoria | Inteligência, Sabedoria |
| Feiticeiro | d6 | Carisma | Constituição, Carisma |
| Guerreiro | d10 | Força ou Destreza | Força, Constituição |
| Ladino | d8 | Destreza | Destreza, Inteligência |
| Mago | d6 | Inteligência | Inteligência, Sabedoria |
| Monge | d8 | Destreza, Sabedoria | Força, Destreza |
| Paladino | d10 | Força, Carisma | Sabedoria, Carisma |
| Patrulheiro | d10 | Destreza, Sabedoria | Força, Destreza |

**Dados Estruturados de Classe (Exemplo)**
```json
{
  "name": "Bárbaro",
  "description": "Um guerreiro feroz de fúria primal. Para cada Bárbaro, a fúria é um poder que alimenta não apenas a sua proeza em batalha, mas também reflexos, resiliência e feitos de força sobre-humanos.",
  "hit_die": "d12",
  "primary_abilities": ["Força"],
  "saving_throw_proficiencies": ["Força", "Constituição"],
  "proficiencies": {
    "armor": ["Armaduras leves", "Armaduras médias", "Escudos"],
    "weapons": ["Armas simples", "Armas marciais"],
    "tools": [],
    "skills": {
      "choose": 2,
      "from": ["Adestrar Animais", "Atletismo", "Intimidação", "Natureza", "Percepção", "Sobrevivência"]
    }
  },
  "starting_equipment": "Você começa com o seguinte equipamento: (a) um machado grande ou (b) qualquer arma marcial corpo a corpo; (a) duas machadinhas ou (b) qualquer arma simples; Um pacote de explorador e quatro azagaias.",
  "class_features": [],
  "subclass_archetype_name": "Caminho Primal",
  "subclass_level": 3,
  "subclasses": [
    {
      "name": "Caminho do Berserker",
      "description": "Para alguns bárbaros, a fúria é um meio para um fim – esse fim sendo a violência. O Caminho do Berserker é um caminho de fúria descontrolada, encharcado de sangue.",
      "subclass_features": []
    },
    {
      "name": "Caminho do Guerreiro Totêmico",
      "description": "O Caminho do Guerreiro Totêmico é uma jornada espiritual, à medida que o bárbaro aceita um espírito animal como guia, protetor e inspiração.",
      "subclass_features": []
    }
  ]
}
```

### Seção 1.4: Armas, Armaduras e Equipamentos

Dados para equipamentos padrão.

**Armas**
```json
[
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
    "properties": ["Munição (alcance 45/180 m)", "Pesada", "Duas Mãos"]
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
```

**Equipamentos de Aventura**
```json
[
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
    "name": "Mochila",
    "category": "Equipamento de Aventura",
    "cost": "2 po",
    "weight": "2.5 kg"
  }
]
```

---

## Parte II: Compêndio de Dados de Tormenta 20

Esta parte aborda os requisitos de dados para o sistema Tormenta 20. Onde as informações são incompletas, será indicado a necessidade de consulta aos manuais oficiais.

### Seção 2.1: Arquitetura de Dados para Tormenta 20

Esquema JSON adaptado às mecânicas únicas de Tormenta 20.

**Esquema de `races`**
```json
{
  "name": "String",
  "description": "String",
  "attribute_modifiers": {
    "Força": "Integer",
    "Destreza": "Integer",
    "Constituição": "Integer",
    "Inteligência": "Integer",
    "Sabedoria": "Integer",
    "Carisma": "Integer"
  },
  "abilities": ["Object"]
}
```

**Esquema de `classes`**

* **Nota de Design (Modelo de "Biblioteca"):** Tormenta 20 emprega um modelo de "biblioteca", onde o jogador escolhe um "Poder" de uma vasta lista a cada nível. O esquema JSON deve conter um array de todos os `class_powers` possíveis, com pré-requisitos, para que a aplicação possa filtrar e apresentar as opções válidas ao jogador.

```json
{
  "name": "String",
  "description": "String",
  "pv_initial": "Integer",
  "pv_per_level": "Integer",
  "pm_per_level": "Integer",
  "pericias": {
    "initial": ["String"],
    "choose": "Integer",
    "from": ["String"]
  },
  "proficiencies": ["String"],
  "class_abilities": ["Object"],
  "class_powers": ["Object"]
}
```

### Seção 2.2: Raças Jogáveis (Tormenta 20)
Dados compilados para as raças de Tormenta 20.

```json
[
  {
    "name": "Humano",
    "description": "Versáteis e adaptáveis, os humanos são a raça mais numerosa em Arton.",
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
  },
  {
    "name": "Anão",
    "description": "Mestres da forja e da cerveja, os anões são um povo robusto e honrado das montanhas.",
    "attribute_modifiers": {
      "Força": 0,
      "Destreza": -2,
      "Constituição": 4,
      "Inteligência": 0,
      "Sabedoria": 2,
      "Carisma": 0
    },
    "abilities": [
      {
        "name": "Conhecimento das Rochas",
        "description": "Você recebe proficiência em Percepção e Sobrevivência para atividades subterrâneas."
      }
    ]
  }
]
```

### Seção 2.3: Classes de Personagem (Tormenta 20)

Lista de classes de Tormenta 20. A população de dados para cada classe focará em PV, PM, Perícias e uma lista de "Poderes" conhecidos.

* Arcanista
* Bárbaro
* Bardo
* Bucaneiro
* Caçador
* Cavaleiro
* Clérigo
* Druida
* Guerreiro
* Inventor
* Ladino
* Lutador
* Nobre
* Paladino

### Seção 2.4: Armas e Equipamentos (Tormenta 20)

Dados limitados sobre equipamentos de Tormenta 20, extraídos de fontes como *Ameaças de Arton*.
**Aviso:** A lista não é exaustiva. Recomenda-se a aquisição dos manuais de regras oficiais para uma lista completa.

---

## Parte III: Análise de Implementação e Recomendações

### Seção 3.1: Orientação para Integração da Aplicação

* **Análise de Dados Hierárquicos:** Lide com os dados aninhados de `subraces` e `subclasses` em D&D 5e combinando as características do objeto pai (raça/classe) com as do objeto filho selecionado (sub-raça/subclasse).
* **Gestão da Escolha do Jogador:** Construa componentes de UI que filtrem opções válidas com base em pré-requisitos, especialmente para o sistema de "Poderes" de Tormenta 20.
* **Lidar com Discrepâncias de Dados:** Para os dados incompletos de Tormenta 20, exiba mensagens de "manual oficial necessário" ou implemente uma funcionalidade para os utilizadores inserirem dados manualmente.

### Seção 3.2: Perspectivas Sistémicas e Caminhos de Expansão

* **Filosofia de Design:** O design de D&D 5e é centrado em "subclasses" com caminhos de progressão fixos. Tormenta 20 foca em "Poderes", permitindo uma personalização mais granular. A UI deve refletir isso: um "assistente" guiado para D&D 5e e uma "biblioteca" de opções para Tormenta 20.
* **Roteiro para Expansão Futura:** Os próximos passos lógicos incluem a adição de compêndios para **Magias**, **Itens Mágicos** e um **Bestiário** de monstros.

## Parte IV: Sistema Unificado (Híbrido)

Esta parte detalha a lógica e a arquitetura de dados para um sistema unificado (ou "híbrido"), que aproveita os melhores elementos de Dungeons & Dragons 5th Edition e Tormenta 20. O objetivo é criar uma base de regras coesa que permita aos jogadores misturar e combinar raças e classes de ambos os universos de forma equilibrada.

### Seção 4.1: Filosofia de Design e Regras Fundamentais

O sistema unificado opera sobre um conjunto de regras fundamentais que servem como uma "camada de compatibilidade" entre as mecânicas distintas de D&D 5e e T20.

1.  **Estrutura de Atributos Unificada:** O sistema adota o modelo de seis atributos (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma). Todos os bônus e penalidades, seja de D&D 5e (`ability_score_increase`) ou T20 (`attribute_modifiers`), são convertidos para um modificador numérico único (ex: +2, -1). Isso simplifica os cálculos e garante paridade entre as raças.

2.  **Sistema de Progressão Híbrido:** Para unificar o modelo de "roteiro" (D&D 5e) com o de "biblioteca" (T20), a progressão de classe será híbrida:
    * **Habilidades de Classe Fixas:** Personagens recebem habilidades chave em níveis específicos, definidas pela sua classe, de forma similar aos arquétipos de D&D 5e.
    * **Sistema de Poderes:** Em níveis intermediários ou como parte de escolhas, os jogadores ganham acesso a uma lista de "Poderes". Esses poderes podem ser genéricos (disponíveis para todos) ou específicos da classe, permitindo a personalização granular característica de Tormenta 20.

3.  **Recursos (PV e PM):** O sistema adota o modelo de Pontos de Vida (PV) e Pontos de Mana (PM) de Tormenta 20 como padrão para todos os personagens.
    * **Pontos de Vida (PV):** Classes de D&D 5e terão seu "Dado de Vida" convertido para um valor fixo de "PV por Nível" (ex: um d12 se torna `+7 PV por nível`, um d8 se torna `+5 PV por nível`).
    * **Pontos de Mana (PM):** Classes conjuradoras de D&D 5e (Mago, Clérigo) receberão um valor de "PM por Nível" para alimentar suas magias, em vez do sistema de "espaços de magia". Classes não-mágicas terão 0 PM por nível, a menos que selecionem poderes que concedam PM.

### Seção 4.2: Arquitetura de Dados para o Sistema Unificado

Para suportar esta lógica, são necessários esquemas JSON adaptados para o sistema híbrido.

**Esquema de `unified_race`**

Este esquema combina os elementos de ambos os sistemas, adicionando um campo `source_system` para rastreabilidade.

```json
{
  "name": "String",
  "description": "String",
  "source_system": "String (dnd5e | tormenta20 | unified)",
  "attribute_modifiers": {
    "Força": "Integer",
    "Destreza": "Integer",
    "Constituição": "Integer",
    "Inteligência": "Integer",
    "Sabedoria": "Integer",
    "Carisma": "Integer"
  },
  "abilities": [
    {
      "name": "String",
      "description": "String"
    }
  ]
}