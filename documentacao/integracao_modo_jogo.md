# 🎮 Integração do Modo de Jogo - Documentação Técnica

## 📋 Visão Geral

Esta documentação descreve a integração entre o frontend (HTML/JavaScript) e o backend (Django/API REST) para o funcionamento do modo de jogo com o "Arquiteto de Mundos" (IA Game Master).

## 🔄 Fluxo de Comunicação

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Frontend      │      │    Backend      │      │    IA GM        │
│   (Browser)     │◄────►│   (Django)      │◄────►│  (IA Service)   │
│                 │      │                 │      │                 │
│ - HTML/JS       │      │ - API REST      │      │ - OpenAI/Claude │
│ - WebSocket     │      │ - WebSocket     │      │ - Local IA      │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## 🧩 Componentes Principais

### 1. Frontend (Template `sessao.html`)

O template `sessao.html` contém a interface do usuário para o modo de jogo, incluindo:

- Chat com IA GM
- Controles de sessão (iniciar, pausar, encerrar)
- Painel lateral para personagens e NPCs
- Comandos rápidos e rolagem de dados

### 2. JavaScript (`game-session.js`)

O arquivo `game-session.js` contém as funções para:

- Iniciar/pausar/encerrar sessão
- Processar turnos
- Enviar mensagens para a IA
- Receber e exibir respostas da IA
- Gerenciar o estado da interface

### 3. Backend (API REST)

O backend fornece endpoints para:

- `/api/sessoes/{id}/iniciar-modo-jogo/` - Iniciar uma sessão
- `/api/sessoes/{id}/pausar-jogo/` - Pausar uma sessão em andamento
- `/api/sessoes/{id}/encerrar-jogo/` - Encerrar uma sessão
- `/api/sessoes/{id}/processar-turno/` - Enviar ações e receber respostas da IA

## 🔌 Integração Frontend-Backend

### Atributos HTML Necessários

Os seguintes atributos devem estar presentes no HTML para correta integração:

```html
<div id="chat-container" data-sessao-id="{{ sessao.id }}">
    <!-- Conteúdo do chat -->
</div>

<form id="chat-form">
    {% csrf_token %}
    <input type="text" id="message-input" placeholder="Digite sua mensagem ou comando...">
    <button type="submit">Enviar</button>
</form>

<div id="game-controls">
    <button id="start-game-btn" class="btn btn-success">▶️ Iniciar Modo de Jogo</button>
    <button id="pause-game-btn" class="btn btn-warning" disabled>⏸️ Pausar Jogo</button>
    <button id="end-game-btn" class="btn btn-danger" disabled>⏹️ Encerrar Jogo</button>
</div>

<div id="status-indicators">
    <span id="current-turn-indicator">Turno atual: <strong>Nenhum</strong></span>
    <span id="waiting-indicator" class="d-none">Aguardando jogadores...</span>
</div>
```

### Inicialização do JavaScript

O JavaScript deve ser incluído e inicializado:

```html
<!-- Incluir o script do modo de jogo -->
<script src="{% static 'js/game-session.js' %}"></script>

<!-- Inicializar -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Inicializar manipuladores de eventos
        initGameSession();
    });
</script>
```

## 📡 Comunicação via API REST

### 1. Iniciar Modo de Jogo

```javascript
async function startGameMode() {
    const sessaoId = getSessaoId();
    const csrfToken = getCSRFToken();
    
    try {
        const response = await fetch(`/api/sessoes/${sessaoId}/iniciar-modo-jogo/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            const data = await response.json();
            updateGameStatus(data);
            updateUIForGameStarted();
        } else {
            console.error('Erro ao iniciar modo de jogo:', await response.text());
        }
    } catch (error) {
        console.error('Erro de rede ao iniciar modo de jogo:', error);
    }
}
```

### 2. Processar Turno (Enviar Mensagem para IA)

```javascript
async function processTurn(message) {
    const sessaoId = getSessaoId();
    const csrfToken = getCSRFToken();
    
    try {
        const response = await fetch(`/api/sessoes/${sessaoId}/processar-turno/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayAIResponse(data.response);
            updateGameStatus(data);
        } else {
            console.error('Erro ao processar turno:', await response.text());
        }
    } catch (error) {
        console.error('Erro de rede ao processar turno:', error);
    }
}
```

### 3. Pausar Jogo

```javascript
async function pauseGame() {
    const sessaoId = getSessaoId();
    const csrfToken = getCSRFToken();
    
    try {
        const response = await fetch(`/api/sessoes/${sessaoId}/pausar-jogo/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            const data = await response.json();
            updateGameStatus(data);
            updateUIForGamePaused();
        } else {
            console.error('Erro ao pausar jogo:', await response.text());
        }
    } catch (error) {
        console.error('Erro de rede ao pausar jogo:', error);
    }
}
```

### 4. Encerrar Jogo

```javascript
async function endGame() {
    const sessaoId = getSessaoId();
    const csrfToken = getCSRFToken();
    
    try {
        const response = await fetch(`/api/sessoes/${sessaoId}/encerrar-jogo/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            const data = await response.json();
            updateGameStatus(data);
            updateUIForGameEnded();
        } else {
            console.error('Erro ao encerrar jogo:', await response.text());
        }
    } catch (error) {
        console.error('Erro de rede ao encerrar jogo:', error);
    }
}
```

## 🎭 Estados da Sessão

A sessão pode estar em um dos seguintes estados:

1. **Não iniciada** - Sessão criada, mas modo de jogo não iniciado
2. **Ativa** - Modo de jogo em andamento
3. **Pausada** - Modo de jogo temporariamente suspenso
4. **Encerrada** - Modo de jogo finalizado

### Atualização do UI baseado no Estado

```javascript
function updateUIForGameStarted() {
    document.getElementById('start-game-btn').disabled = true;
    document.getElementById('pause-game-btn').disabled = false;
    document.getElementById('end-game-btn').disabled = false;
    document.getElementById('message-input').disabled = false;
    
    const statusIndicator = document.getElementById('current-turn-indicator');
    statusIndicator.innerHTML = 'Turno atual: <strong>Jogadores</strong>';
    
    addSystemMessage('O modo de jogo foi iniciado! A IA GM está pronta para narrar a aventura.');
}

function updateUIForGamePaused() {
    document.getElementById('start-game-btn').disabled = false;
    document.getElementById('pause-game-btn').disabled = true;
    document.getElementById('end-game-btn').disabled = false;
    document.getElementById('message-input').disabled = true;
    
    const statusIndicator = document.getElementById('current-turn-indicator');
    statusIndicator.innerHTML = 'Turno atual: <strong>Pausado</strong>';
    
    addSystemMessage('O modo de jogo foi pausado temporariamente.');
}

function updateUIForGameEnded() {
    document.getElementById('start-game-btn').disabled = false;
    document.getElementById('pause-game-btn').disabled = true;
    document.getElementById('end-game-btn').disabled = true;
    document.getElementById('message-input').disabled = true;
    
    const statusIndicator = document.getElementById('current-turn-indicator');
    statusIndicator.innerHTML = 'Turno atual: <strong>Encerrado</strong>';
    
    addSystemMessage('O modo de jogo foi encerrado. Você pode iniciar uma nova sessão.');
}
```

## 🎮 Comandos Especiais

O sistema suporta comandos especiais no chat:

- `/rolar XdY` - Rola dados (exemplo: `/rolar 1d20+5`)
- `/status` - Exibe status do personagem atual
- `/inventario` - Exibe inventário do personagem
- `/ajuda` - Exibe lista de comandos disponíveis

### Processamento de Comandos

```javascript
function processCommand(message) {
    const commandMatch = message.match(/^\/([a-zA-Z]+)(?:\s+(.+))?$/);
    
    if (!commandMatch) {
        return false; // Não é um comando
    }
    
    const command = commandMatch[1].toLowerCase();
    const args = commandMatch[2] || '';
    
    switch (command) {
        case 'rolar':
            processRollCommand(args);
            return true;
        case 'status':
            displayCharacterStatus();
            return true;
        case 'inventario':
            displayCharacterInventory();
            return true;
        case 'ajuda':
            displayHelpMessage();
            return true;
        default:
            addSystemMessage(`Comando desconhecido: /${command}`);
            return true;
    }
}
```

## 🔧 Funções Auxiliares

### Obter ID da Sessão

```javascript
function getSessaoId() {
    const chatContainer = document.getElementById('chat-container');
    return chatContainer.dataset.sessaoId;
}
```

### Obter CSRF Token

```javascript
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
```

### Adicionar Mensagem ao Chat

```javascript
function addMessageToChat(sender, message, isSystem = false) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    
    messageElement.classList.add('message');
    if (isSystem) {
        messageElement.classList.add('system-message');
    } else {
        messageElement.classList.add(sender === 'Você' ? 'user-message' : 'gm-message');
    }
    
    messageElement.innerHTML = `
        <div class="message-header">
            <strong>${sender}</strong>
            <span class="message-time">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="message-content">${message}</div>
    `;
    
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
```

### Adicionar Mensagem do Sistema

```javascript
function addSystemMessage(message) {
    addMessageToChat('Sistema', message, true);
}
```

### Exibir Resposta da IA

```javascript
function displayAIResponse(response) {
    // Processa possíveis formatações (markdown, etc)
    const formattedResponse = processMarkdown(response);
    
    // Adiciona ao chat
    addMessageToChat('Mestre (IA)', formattedResponse);
    
    // Atualiza indicadores
    document.getElementById('current-turn-indicator').innerHTML = 
        'Turno atual: <strong>Jogadores</strong>';
    document.getElementById('waiting-indicator').classList.add('d-none');
}
```

## 🧪 Testes

Para testar a integração:

1. Abra uma sessão: `http://localhost:8000/sessoes/{id}/`
2. Clique no botão "▶️ Iniciar Modo de Jogo"
3. Digite uma mensagem e envie
4. Verifique se a IA responde corretamente
5. Teste pausar e retomar a sessão
6. Teste encerrar a sessão

## 🐛 Solução de Problemas

### Problema: IA não responde

**Possíveis causas:**
- API de IA não configurada
- Erro no processamento do turno
- Problema na conexão com serviço de IA

**Solução:**
- Verifique logs do servidor
- Confirme configurações de IA em `settings.py`
- Verifique console do navegador para erros

### Problema: Erro de CSRF

**Possíveis causas:**
- Token CSRF não incluído nas requisições
- Sessão expirada

**Solução:**
- Verifique se `getCSRFToken()` está funcionando
- Atualize a página para obter novo token

### Problema: Estado da Sessão Incorreto

**Possíveis causas:**
- Dessincronia entre frontend e backend
- Erro no processamento de estado

**Solução:**
- Reinicie a sessão
- Verifique logs do servidor
- Atualize a página

## 📝 Melhores Práticas

1. **Manipulação de Erros:**
   - Sempre exiba feedback visual para erros
   - Log detalhado no console
   - Mensagens de erro amigáveis para o usuário

2. **Gestão de Estado:**
   - Mantenha o estado da UI sincronizado com o backend
   - Atualize UI imediatamente após ações do usuário
   - Valide estado atual antes de cada ação

3. **Performance:**
   - Limite o número de mensagens exibidas no chat
   - Considere paginação para histórico longo
   - Otimize chamadas à API

4. **Acessibilidade:**
   - Use contraste adequado para texto
   - Inclua text-to-speech para mensagens importantes
   - Suporte navegação por teclado

## 🔍 Referências

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Fetch API](https://developer.mozilla.org/pt-BR/docs/Web/API/Fetch_API)
- [WebSocket API](https://developer.mozilla.org/pt-BR/docs/Web/API/WebSockets_API)

---

## ✅ Checklist de Implementação

- [x] Estrutura HTML correta
- [x] Atributos data-* necessários
- [x] Inclusão do JavaScript
- [x] Funções para iniciar/pausar/encerrar jogo
- [x] Processamento de turnos
- [x] Exibição de mensagens
- [x] Processamento de comandos
- [x] Manipulação de erros
- [x] Atualização de UI baseada em estado
- [x] Documentação completa

---

Documentação criada em: **14/09/2023**