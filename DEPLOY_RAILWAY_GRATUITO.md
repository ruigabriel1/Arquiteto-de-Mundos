# 🚂 DEPLOY GRATUITO COM RAILWAY

## 🎯 **POR QUE RAILWAY?**

- 🆓 **$5 crédito mensal GRATUITO**
- 🚀 **Deploy automático** do GitHub
- 🐘 **PostgreSQL gratuito** incluído
- 🔧 **Zero configuração** necessária
- 📊 **Escalável** conforme cresce

---

## 📋 **PASSO A PASSO COMPLETO**

### **1. Preparar o Projeto**

#### A. Criar arquivos necessários para deploy:

```bash
# 1. Criar Procfile (Railway precisa)
echo "web: gunicorn unified_chronicles.wsgi --log-file -" > Procfile

# 2. Criar runtime.txt (especificar Python)
echo "python-3.11.6" > runtime.txt

# 3. Instalar gunicorn
pip install gunicorn
pip freeze > requirements.txt
```

#### B. Configurar settings para produção:

Criar arquivo `unified_chronicles/settings_prod.py`:

```python
from .settings import *
import os

# Configurações de Produção
DEBUG = False
ALLOWED_HOSTS = ['*']  # Railway configura automaticamente

# Database PostgreSQL (Railway fornece automaticamente)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE'),
        'USER': os.environ.get('PGUSER'),
        'PASSWORD': os.environ.get('PGPASSWORD'),
        'HOST': os.environ.get('PGHOST'),
        'PORT': os.environ.get('PGPORT', 5432),
    }
}

# Static files (Railway serve automaticamente)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware Whitenoise (para servir static files)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
```

### **2. Configurar Railway**

#### A. Ir para [railway.app](https://railway.app) e fazer login com GitHub

#### B. Conectar seu repositório:
1. Clique em "New Project"
2. Escolha "Deploy from GitHub repo" 
3. Selecione seu repositório `unified_chronicles`

#### C. Railway detecta automaticamente que é Django!

### **3. Configurar Variáveis de Ambiente**

No dashboard da Railway, adicionar:

```env
DJANGO_SETTINGS_MODULE=unified_chronicles.settings_prod
DJANGO_SECRET_KEY=sua-chave-secreta-aqui
OPENAI_API_KEY=sua-chave-openai
ANTHROPIC_API_KEY=sua-chave-anthropic
```

### **4. Deploy Automático** 

Railway faz deploy automaticamente quando você fizer push para GitHub:

```bash
git add .
git commit -m "Configuração para Railway"
git push origin main
```

---

## 💰 **CUSTOS REAIS**

### **Completamente Gratuito até:**
- 📊 **500 horas/mês** de uso
- 🗄️ **1GB PostgreSQL**
- 🌐 **100GB transferência**
- 👥 **~200-500 usuários** simultâneos

### **Quando começará a cobrar:**
- 💰 **$5/mês** por projeto (após limites)
- 📈 **Apenas com muito tráfego** (milhares de usuários)

---

## 🚀 **VANTAGENS DO RAILWAY**

1. **Deploy em 2 minutos** ⚡
2. **PostgreSQL automático** 🐘
3. **SSL grátis** 🔒
4. **Domínio .railway.app** 🌐
5. **Logs em tempo real** 📊
6. **Backup automático** 💾

---

## 🔧 **COMANDOS COMPLETOS PARA DEPLOY**

Execute isso na ordem:

```bash
# 1. Instalar dependências de produção
pip install gunicorn whitenoise psycopg2-binary
pip freeze > requirements.txt

# 2. Criar Procfile
echo "web: python manage.py migrate && gunicorn unified_chronicles.wsgi" > Procfile

# 3. Criar runtime.txt  
echo "python-3.11.6" > runtime.txt

# 4. Commit e push
git add .
git commit -m "Configuração Railway deploy"
git push origin main
```

Depois é só conectar no Railway! ✨

---

## 🎉 **RESULTADO**

Em **menos de 5 minutos** você terá:
- ✅ Site online em `https://seu-projeto.up.railway.app`
- ✅ PostgreSQL funcionando
- ✅ IA integrada
- ✅ Sistema completo de RPG

**CUSTO: $0/mês** para começar! 🎯