# 🏛️ Arquiteto de Mundos

**Plataforma Completa de RPG Online com IA Game Master**

![Status](https://img.shields.io/badge/Status-Pronto-brightgreen)
![Django](https://img.shields.io/badge/Django-4.2.7-blue)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![IA](https://img.shields.io/badge/IA-GPT%2BClaude-orange)

---

## 🚀 **Início Rápido**

### ⚡ **Método Mais Rápido (Windows)**
1. **Duplo clique** em `start_server.bat`
2. Aguarde inicialização automática (30-60 segundos)
3. **Acesse:** http://localhost:8000/

### 🖥️ **Método Manual**
```bash
# Ativar ambiente virtual
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac

# Iniciar servidor
python manage.py runserver
```

### 👤 **Credenciais de Teste**
- **Admin:** `admin` / `admin123`
- **Demo:** `demo` / `demo123`

### 📍 **URLs Importantes**
- **Sistema Principal:** http://localhost:8000/
- **Painel Admin:** http://localhost:8000/admin/
- **IA Game Master:** http://localhost:8000/ia-gm/

---

## 🎯 **O que é o Arquiteto de Mundos?**

Uma **plataforma web revolucionária** que combina:

### 🎮 **Sistema Completo de RPG**
- ✅ **Campanhas Online** - Criação e gerenciamento completo
- ✅ **Fichas Digitais** - Personagens D&D 5e + Tormenta20
- ✅ **Chat em Tempo Real** - Interface estilo Discord
- ✅ **Sistema de Usuários** - Autenticação e perfis

### 🤖 **"Arquiteto de Mundos" - IA Game Master**
- ✅ **Mestre IA Inteligente** - Segue regras comportamentais rígidas
- ✅ **Filosofia "Sim, e..."** - Nunca bloqueia, sempre cria oportunidades
- ✅ **NPCs com Alma** - Personalidades únicas e consistentes
- ✅ **Mundo Vivo** - Reage às ações dos jogadores

---

## 🏗️ **Arquitetura do Sistema**

```
Frontend (Bootstrap + JS) ←→ Django Backend ←→ SQLite/PostgreSQL
         ↓                          ↓                  ↓
   WebSocket Chat        ←→    Django Channels   ←→   Redis
         ↓                          ↓                  
   Interface IA          ←→    Arquiteto de Mundos ←→ APIs IA
```

### 📁 **Estrutura de Apps**
```
├── 👤 usuarios/           # Autenticação e perfis
├── 🎯 campanhas/          # Gerenciamento de campanhas  
├── 👥 personagens/        # Fichas de personagem
├── 💬 chat/               # Chat em tempo real
├── 🤖 ia_gm/             # IA Game Master
├── ⚙️ sistema_unificado/  # Sistema de jogos
└── 📜 sessoes/            # Sessões de jogo
```

---

## 🤖 **Arquiteto de Mundos - IA Game Master**

### 🎭 **Características Únicas**

#### **Persona Inteligente**
- 🎯 **Nunca se subordina** - Mantém autoridade como Mestre
- 📢 **Dirige-se aos personagens** - Nunca chama jogador de "Mestre"
- 🔄 **Dois modos distintos** - Configuração vs Jogo ativo

#### **Ciclo de Jogo Rigoroso**
1. **DESCREVER** - Situção vivida + "O que vocês fazem?"
2. **AGUARDAR** - Espera TODOS os jogadores declararem ações
3. **RESOLVER** - Processa tudo junto, narra consequências

#### **Roleplay Avançado**
- 💬 **Diálogos Estruturados** - `[NPC] [ação] "fala" (tom)`
- 👥 **NPCs Únicos** - Motivação, falha e segredo para cada um
- 🎨 **"Descreva primeiro"** - Imagens só quando solicitado

### 🚀 **Como Usar**

1. **Acesse:** http://localhost:8000/ia-gm/
2. **Selecione** uma campanha sua
3. **Crie** uma sessão de IA
4. **Configure** estilo, criatividade, dificuldade
5. **Use as ferramentas:**
   - 👥 Gerar NPCs únicos
   - 🗺️ Criar locais com história
   - 📜 Desenvolver missões envolventes
   - ⚡ Processar ações "impossíveis"

---

## 🎯 **Sistema de Campanhas**

### **Funcionalidades Completas**
- ✅ **Interface Web** - Criação através da interface
- ✅ **Gerenciamento de Participantes** - Aprovação/rejeição automática
- ✅ **Um Personagem por Usuário** - Regra de negócio implementada
- ✅ **Notificações** - Sistema de logs integrado
- ✅ **Responsivo** - Funciona em mobile e desktop

### **Fluxo de Participação**
1. **Jogador** encontra campanha pública ou recebe convite
2. **Solicita participação** através da interface
3. **Organizador aprova/rejeita** pelo painel de gerenciamento
4. **Jogador define personagem** após aprovação
5. **Participa ativamente** da campanha

---

## 💬 **Chat em Tempo Real**

### **Recursos**
- ✅ **WebSocket** - Mensagens instantâneas
- ✅ **Salas por Campanha** - Contexto isolado
- ✅ **Interface Moderna** - Design estilo Discord
- ✅ **Histórico Persistente** - Mensagens salvas
- ✅ **Status Online** - Veja quem está conectado

### **Integração com IA**
- 🤖 **Chat de Sessão** - Interface dedicada para IA GM
- 📏 **Altura Otimizada** - 75vh para melhor visualização
- ⚙️ **Comandos Contextuais** - Baseado no modo atual da IA

---

## 👤 **Sistema de Usuários**

### **Recursos Completos**
- ✅ **Registro/Login** - Autenticação segura
- ✅ **Dashboard Pessoal** - Painel do usuário
- ✅ **Perfil Editável** - Dados pessoais
- ✅ **Menu Lateral** - Navegação consistente
- ✅ **Design Responsivo** - Mobile-friendly

### **Tema Visual**
- 🎨 **Dark/Purple** - Design moderno
- 📱 **Mobile First** - Otimizado para dispositivos móveis
- ♿ **Acessível** - Interface clara e intuitiva

---

## 🛠️ **Configuração Avançada**

### **Variáveis de Ambiente (.env)**
```env
# Core Django
DEBUG=True
SECRET_KEY=sua_chave_super_secreta
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de Dados (Produção)
DATABASE_URL=postgres://user:pass@host:5432/dbname

# Cache Redis
REDIS_URL=redis://localhost:6379/0

# APIs de IA (Opcional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### **Deploy em Produção**
```bash
# 1. Clone o projeto
git clone https://github.com/ruigabriel1/Arquiteto-de-Mundos.git
cd unified_chronicles

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure variáveis
cp .env.example .env
# Edite o .env com suas configurações

# 4. Migre banco
python manage.py migrate

# 5. Colete arquivos estáticos
python manage.py collectstatic

# 6. Execute com Gunicorn
gunicorn unified_chronicles.wsgi:application --bind 0.0.0.0:8000
```

---

## 🧪 **Testes e Qualidade**

### **Sistema Testado**
```bash
# Verificar integridade
python manage.py check

# Testes da IA GM
python ia_gm/test_master_rules.py

# Resultado esperado: ✅ TODOS OS TESTES PASSARAM
```

### **Status dos Componentes**
- 🟢 **Backend Django** - Totalmente funcional
- 🟢 **Frontend Bootstrap** - Interface completa
- 🟢 **IA GM** - Regras implementadas e testadas
- 🟢 **WebSocket Chat** - Funcionando perfeitamente
- 🟢 **Sistema de Campanhas** - Completo
- 🟢 **Autenticação** - Segura e robusta

---

## 📚 **Documentação Adicional**

- 📋 **[PROJETO_FINAL.md](PROJETO_FINAL.md)** - Documentação completa do projeto
- 🤖 **[REGRAS_MESTRE_IA_IMPLEMENTADAS.md](REGRAS_MESTRE_IA_IMPLEMENTADAS.md)** - Detalhes da IA GM
- ⚡ **[QUICKSTART.md](QUICKSTART.md)** - Guia rápido de início
- 🔧 **[TECHNICAL_SPECS.md](TECHNICAL_SPECS.md)** - Especificações técnicas

---

## 🎯 **Próximos Passos**

### **Para Usar Imediatamente**
1. ✅ Execute `start_server.bat` 
2. ✅ Acesse http://localhost:8000/
3. ✅ Crie sua conta ou use `demo/demo123`
4. ✅ Explore o sistema completo

### **Para Expandir (Futuro)**
- 🎲 **Sistema de Dados Virtuais**
- 🗺️ **Mapas Interativos**
- 📱 **App Mobile**
- 🌐 **VTT Completo**

---

## ❤️ **Sobre o Projeto**

O **Arquiteto de Mundos** foi desenvolvido especialmente para a **comunidade RPG brasileira**, oferecendo uma experiência completa de RPG online com tecnologia de ponta e inteligência artificial verdadeiramente útil.

**Características Únicas:**
- 🇧🇷 **Totalmente em Português** - Interface e conteúdo
- 🤖 **IA GM Real** - Não apenas chatbot, mas Mestre de verdade
- 🎭 **Experiência Imersiva** - Filosofia "Sim, e..." implementada
- 🚀 **Tecnologia Moderna** - Django, WebSocket, Bootstrap 5

---

## 🏁 **Conclusão**

O **Arquiteto de Mundos está 100% funcional** e pronto para uso. É uma plataforma completa que revoluciona a forma como jogamos RPG online.

**Comece sua aventura agora mesmo!** 🎲⚔️

---

**Desenvolvido com ❤️ para RPGistas brasileiros**  
*"Onde as histórias ganham vida"*