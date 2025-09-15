# 🚀 Guia de Início Rápido - Unified Chronicles

## ⚡ Método Mais Rápido (1 minuto)

### Windows:
1. **Duplo clique** em `start_server.bat`
2. Aguarde aparecer: "Servidor disponível em:"
3. **Acesse:** http://localhost:8000/

### Linux/Mac:
```bash
source venv/bin/activate
python manage.py runserver
```

## 🌐 URLs Principais

| Área | URL | Descrição |
|------|-----|-----------|
| **Frontend** | http://localhost:8000/ | Interface principal |
| **Admin** | http://localhost:8000/admin/ | Painel administrativo |
| **API** | http://localhost:8000/api/ | Endpoints REST |
| **🧿 Arquiteto** | http://localhost:8000/arquiteto/ | **IA Game Master** |

## 🔑 Credenciais Padrão

### Administrador:
- **Usuário:** `admin`
- **Senha:** `admin123`

### Usuários de Teste:
- **mestre_demo** / `demo123`
- **jogador1** / `demo123`
- **jogador2** / `demo123`

## 🧿 Como Usar o "Arquiteto de Mundos"

### Passo 1: Acesse o Sistema
1. Vá para: http://localhost:8000/arquiteto/
2. Faça login como `admin`

### Passo 2: Crie uma Sessão de IA
1. Selecione uma campanha
2. Clique em "Nova Sessão IA"
3. Configure:
   - **Estilo Narrativo:** Épico, Misterioso, Sombrio, etc.
   - **Criatividade:** 1-10 (recomendado: 7)
   - **Dificuldade:** 1-10 (recomendado: 5)

### Passo 3: Use as Ferramentas
- 👥 **Gerar NPC** → Cria personagens únicos
- 🗺️ **Criar Local** → Desenvolve ambientes ricos
- 📜 **Nova Missão** → Gera aventuras personalizadas
- 🎲 **Processar Ação** → Responde ações dos jogadores
- ✨ **Ação "Impossível"** → Filosofia "Sim, e..."

## 💬 Chat em Tempo Real

### Acessar Chat:
1. Entre em uma campanha
2. Vá para a sala de chat
3. Use comandos:
   - `/roll 1d20+5` → Rola dados
   - `/whisper [usuário] [mensagem]` → Mensagem privada

## 🔧 Configuração de IA (Opcional)

Para usar APIs externas, edite `settings.py`:

```python
# OpenAI
OPENAI_API_KEY = 'sk-...'

# Anthropic Claude  
ANTHROPIC_API_KEY = 'sk-ant-...'

# Modelo Local (Ollama)
LOCAL_AI_URL = 'http://localhost:11434'
```

**Nota:** Funciona sem APIs externas!

## 🌐 Acessar de Outros Dispositivos

### Mesma Rede (LAN):
```bash
python manage.py runserver 0.0.0.0:8000
# Outros acessam via: http://SEU_IP:8000/
```

### Descobrir seu IP:
```bash
# Windows
ipconfig | findstr "IPv4"

# Linux/Mac  
ifconfig | grep inet
```

## ❗ Problemas Comuns

### "Port 8000 already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID [NÚMERO] /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Erro de Migração
```bash
python manage.py migrate
```

### Problemas de Permissão
```bash
# Windows (como Admin)
netsh advfirewall firewall add rule name="Django" dir=in action=allow protocol=TCP localport=8000
```

## 📱 Dispositivos Suportados

- ✅ **Desktop** (Windows, Linux, Mac)
- ✅ **Tablets** (interface responsiva)
- ✅ **Mobile** (funcional, otimizado para tablet)

## 🎯 Primeiros Passos Recomendados

1. **Explore o Admin** → Veja dados pré-carregados
2. **Teste o Chat** → Experimente comandos de dados
3. **Crie um Personagem** → Use o sistema de fichas
4. **Use o Arquiteto** → Experimente a IA GM
5. **Convide Amigos** → Teste em grupo

## 🆘 Precisa de Ajuda?

- **README Completo:** [README.md](README.md)
- **Documentação da API:** http://localhost:8000/api/
- **Issues:** Crie uma issue no GitHub
- **Discord:** [Link da comunidade]

---

**Unified Chronicles** - Onde as histórias ganham vida! 🎲✨