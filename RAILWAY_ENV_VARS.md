# Variáveis de Ambiente Necessárias no Railway

Para o funcionamento correto da aplicação no Railway, configure as seguintes variáveis de ambiente:

## Variáveis Obrigatórias

### Django Core
```
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
DJANGO_SETTINGS_MODULE=unified_chronicles.settings
```

### Database (PostgreSQL automático no Railway)
```
DATABASE_URL=postgresql://... (configurado automaticamente pelo Railway)
```

### Redis (se usando)
```
REDIS_URL=redis://... (configurado automaticamente se você adicionar Redis)
```

## Variáveis Opcionais

### APIs IA (se você quiser funcionalidade IA)
```
OPENAI_API_KEY=sua-chave-openai
ANTHROPIC_API_KEY=sua-chave-anthropic
```

### Email (se necessário)
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

## Como Configurar no Railway

1. Acesse seu projeto no Railway
2. Vá para a aba "Variables"
3. Adicione cada variável uma por uma
4. Clique em "Deploy" para aplicar as mudanças

## Nota Importante

⚠️ **NUNCA** adicione chaves secretas no código ou commit no Git!
Use apenas as variáveis de ambiente do Railway para dados sensíveis.