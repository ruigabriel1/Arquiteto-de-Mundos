1. Análise do Problema (Contexto)
A IA GM está exibindo um comportamento falho. Abaixo está um log de uma interação recente que ilustra os problemas:

Plaintext

[COLE AQUI O LOG DA INTERAÇÃO QUE VOCÊ ME MOSTROU]

🤖 IA GM
16:31:28
Desco, vocês estão juntos quando percebem algo: Vocês ouvem o som distante de um rio a correr, prometendo água fresca.
De repente, Uma estranha névoa dourada dissipa-se à vossa frente, revelando um beco que não estava lá antes.
O que vocês fazem?
...
Turno 3
Vocês notam um objeto brilhando sutilmente debaixo de uma pilha de escombros.
O que vocês fazem?
Os problemas identificados são:

Falha na Conexão Causa-Efeito: A consequência de uma ação não tem relação lógica com a ação em si (ex: procurar pessoas causa um tremor de terra).

Ignorando a Ação do Jogador: A IA não responde às perguntas ou pedidos dos jogadores (ex: ignora o pedido de /sugestao).

Uso de Meta-Linguagem Proibida: A IA continua usando frases genéricas como "o ambiente ao redor reage", violando as regras de narração.

Repetição e Loops: A IA está presa em um loop, repetindo a mesma descrição de cena ("Vocês notam um objeto brilhando...").

2. Hipótese da Causa Raiz
A hipótese é que a função Python que processa o turno do jogador está apenas usando a ação como um gatilho para gerar um evento genérico, em vez de usar a ação específica do jogador como o contexto principal para a próxima geração de texto da IA. A lógica atual parece desconectada e não mantém um estado de conversa coerente.

3. Requisitos para a Solução
O código novo ou refatorado deve seguir estritamente os seguintes requisitos:

Processamento de Ação Direta: A lógica principal deve pegar a string da ação do jogador (ex: "procuro se tem alguem por perto") e gerar uma consequência narrativa que seja uma resposta direta e lógica a essa ação.

Aderência Estrita às Regras de Persona: O prompt enviado para o modelo de linguagem deve ser construído de forma a forçar a aderência às regras de narração já definidas (sem meta-linguagem, narração concreta, foco nos 5 sentidos, etc.).

Manutenção de Contexto (Anti-Loop): A função deve receber o histórico da conversa recente para garantir que a IA não se repita e que a narrativa progrida de forma coerente.

4. Tarefa Concreta de Código
Com base em tudo isso, sua tarefa é escrever ou refatorar a função Python responsável por processar o turno do jogador. Assuma que esta função recebe o histórico da conversa e a ação do jogador atual, e deve retornar a próxima parte da narrativa gerada pela IA.

Por favor, gere o código Python para a seguinte função:

Python

# Importe as bibliotecas necessárias para interagir com a API do Gemini
import google.generativeai as genai

# Assuma que a API Key está configurada
# genai.configure(api_key="SUA_API_KEY")

def processar_acao_do_jogador(historico_da_conversa: list, acao_do_jogador: str) -> str:
    """
    Processa a ação de um jogador, gera a continuação da história com a IA Gemini
    e retorna a resposta narrativa.

    Args:
        historico_da_conversa: Uma lista de dicionários representando os turnos anteriores,
                                no formato {"role": "user"|"model", "parts": ["texto"]}.
        acao_do_jogador: A string de texto com a ação do jogador atual.

    Returns:
        A string com a resposta narrativa do Mestre de IA.
    """
    # 1. Obtenha as regras de persona e narração (de um arquivo ou de uma constante).
    # Estas são as regras que definimos anteriormente para proibir meta-linguagem e forçar narração concreta.
    regras_do_mestre = """
    REGRAS DO MESTRE DE IA:
    - Você é um Mestre de RPG. Sua resposta DEVE ser puramente narrativa e imersiva.
    - NUNCA use meta-linguagem (ex: 'a aventura se desenrola', 'o ambiente reage').
    - RESPONDA DIRETAMENTE à ação do jogador com uma consequência lógica e concreta. Descreva o que o personagem vê, ouve e sente.
    - Se o jogador pergunta "Acho uma taverna?", sua resposta deve ser "Sim, você encontra..." ou "Não, mas você vê...".
    - NUNCA se repita. Continue a história com base no que acabou de acontecer.
    - Sempre termine sua resposta com uma pergunta aberta como "O que você faz?".
    """

    # 2. Construa o prompt para a IA, combinando as regras, o histórico e a nova ação.
    prompt_completo = f"""
    {regras_do_mestre}

    --- HISTÓRICO DA CONVERSA ---
    {historico_da_conversa}

    --- AÇÃO ATUAL DO JOGADOR ---
    {acao_do_jogador}

    --- RESPOSTA DO MESTRE (Continue a história) ---
    """

    # 3. Configure e chame o modelo Gemini.
    # A função deve ser robusta para lidar com a formatação do histórico.
    # O prompt final enviado para a IA deve ser uma combinação das regras, do histórico e da ação atual.
    
    # Exemplo de como a lógica de chamada pode ser (pode precisar de ajustes):
    # model = genai.GenerativeModel('gemini-pro')
    # full_prompt_for_api = historico_da_conversa + [{"role": "user", "parts": [f"{regras_do_mestre}\n\nAção atual: {acao_do_jogador}"]}]
    # response = model.generate_content(full_prompt_for_api)
    # resposta_narrativa = response.text
    
    # 4. Retorne a resposta da IA.
    # return resposta_narrativa
    
    # Por favor, complete a lógica desta função.
    print("Lógica da função a ser gerada aqui...")
    return "Resposta narrativa gerada pela IA..."
