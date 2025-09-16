# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Regras do Projeto (pt-BR)

- Toda a comunicação (entre agentes, desenvolvedores e usuários) deve ser feita em Português do Brasil (pt-BR).
- Codificação: comentários, docstrings, mensagens de log, mensagens de erro, textos de interface e mensagens de commit devem ser escritos em pt-BR.
- Identificadores (nomes de variáveis, funções, classes e módulos): preferencialmente em pt_br, sem acentos e sem espaços; siga o padrão já adotado no arquivo (snake_case para Python, PascalCase para classes). Use termos em inglês apenas quando forem nomes próprios de bibliotecas/stack.
- Arquivos e documentação (README, WARP.md, etc.): manter em pt-BR. Traduções são opcionais e, se existirem, devem ser indicadas explicitamente.
- Em explicações de comandos/saídas no terminal, use pt-BR nas descrições; os comandos continuam no idioma da ferramenta.

## Project Overview

Unified Chronicles is a Brazilian Portuguese RPG platform with an AI Game Master called "Arquiteto de Mundos" (World Architect). It combines traditional RPG management with intelligent AI narrative assistance.

### Core Architecture

**Backend**: Django 5.2.6 with Django Channels for WebSocket support  
**Database**: SQLite (development) / PostgreSQL (production)  
**Real-time**: Redis for channels and caching  
**AI Integration**: Multi-provider support (OpenAI, Anthropic Claude, local models)  
**Frontend**: Bootstrap 5 + vanilla JavaScript

### Django Apps Structure

```
├── usuarios/           # User authentication and profiles
├── campanhas/          # Campaign management (D&D 5e, Tormenta20)
├── personagens/        # Character sheets and management
├── sessoes/            # Game sessions and participant management
├── chat/               # Real-time WebSocket chat
├── ia_gm/              # AI Game Master "Arquiteto de Mundos"
├── sistema_unificado/  # Game system abstraction layer
├── rolagem/            # Dice rolling system
└── mensagens/          # Messaging system
```

## Development Commands

### Quick Start
```powershell
# Windows quick start
.\start_server.bat

# Manual start
.venv\Scripts\activate
python manage.py runserver
```

### Database Management
```powershell
# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Or use the automated script: python create_superuser.py

# Load test data
python create_fixtures.py
```

### Testing
```powershell
# Run Django tests
python manage.py test

# Test AI Game Master rules (comprehensive behavioral tests)
python ia_gm/test_master_rules.py

# Run specific app tests
python manage.py test campanhas
python manage.py test ia_gm
python manage.py test personagens
```

### Development Tools
```powershell
# Check project integrity
python manage.py check

# Collect static files
python manage.py collectstatic

# Run with different settings
python manage.py runserver --settings=unified_chronicles.settings_dev
```

## Core Features & Key URLs

### Main System
- **Root**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/ (admin/admin123)
- **API Root**: http://localhost:8000/api/

### AI Game Master
- **Arquiteto de Mundos Interface**: http://localhost:8000/arquiteto/
- **Campaign-based AI sessions with behavioral rules engine**
- **Multi-provider AI support with fallback mechanisms**

## Architecture Highlights

### AI Game Master System (`ia_gm/`)

The "Arquiteto de Mundos" is the most sophisticated component, featuring:

**Behavioral Rules Engine** (`master_rules.py`):
- **Two Operation Modes**: Configuration mode (accepts slash commands) vs. Active Game mode (narrative only)
- **Mandatory Game Cycle**: 1) Describe situation + ask question, 2) Wait for ALL player actions, 3) Process and narrate consequences
- **Persona Rules**: Never subordinates to players, addresses characters by name, maintains "Yes, and..." philosophy

**Multi-Provider AI Client** (`ai_client.py`):
- Supports OpenAI, Anthropic Claude, and local models (Ollama)
- Automatic failover and cost estimation
- Async operations with connection pooling

**Game Session Manager** (`game_session_manager.py`):
- Manages AI session states and player action coordination
- Integrates with Django Channels for real-time updates
- Memory persistence for campaign continuity

### Real-time Chat System (`chat/`)
- WebSocket-based using Django Channels
- Campaign-isolated chat rooms
- Discord-style interface design
- Integration with AI Game Master for session chats

### Character & Campaign Management
- **D&D 5e and Tormenta20 support** with extensible system architecture
- **Web-based character creation** with validation rules
- **Campaign participation workflow** with approval/rejection system
- **One character per user per campaign** rule enforcement

## Environment Configuration

### Required Environment Variables (.env)
```env
# Core Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
DATABASE_URL=postgres://user:pass@host:5432/dbname

# Redis (for channels and caching)
REDIS_URL=redis://localhost:6379/0

# AI Providers (optional - at least one recommended)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LOCAL_AI_URL=http://localhost:11434  # For Ollama
```

### Production Deployment
```bash
# Standard Django deployment
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn unified_chronicles.wsgi:application --bind 0.0.0.0:8000

# With Docker
docker build -t unified-chronicles .
docker run -p 8000:8000 unified-chronicles
```

## Development Guidelines

### AI Game Master Rules
The AI system has strict behavioral rules enforced through `MasterRulesEngine`:
- **Never break persona**: AI maintains authority as game master
- **Mandatory cycle compliance**: Always follow describe→wait→resolve pattern
- **Command validation**: Slash commands only in configuration mode
- **Memory consistency**: NPCs maintain personality across sessions

### Database Design
- **Multi-tenancy**: Campaigns isolate user data
- **Polymorphic models**: Character system supports multiple RPG systems
- **Audit trails**: Session participation and AI interaction tracking
- **Soft deletes**: Campaign and character preservation

### Real-time Features
- Django Channels for WebSocket connections
- Redis backend for message persistence
- Chat rooms scoped to campaigns
- AI integration for session management

### Testing Strategy
- Behavioral tests for AI rules compliance (`test_master_rules.py`)
- Django unit tests for models and business logic
- Integration tests for real-time features
- Manual testing scripts for character creation

### Key Configuration Files
- `unified_chronicles/settings.py`: Main Django configuration
- `unified_chronicles/urls.py`: URL routing with namespace separation
- `requirements.txt`: Python dependencies (Django 5.2.6, Channels, DRF)
- `start_server.bat`: Windows development server with auto-migration

The system is production-ready with comprehensive testing, multi-provider AI integration, and sophisticated behavioral rules for the AI Game Master component.