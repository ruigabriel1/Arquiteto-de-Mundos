"""
Settings de Produção para Railway Deploy
"""
from .settings import *
import os

# Configurações de Produção
DEBUG = False
ALLOWED_HOSTS = [
    '.railway.app',
    '.up.railway.app', 
    'localhost', 
    '127.0.0.1'
]

# Database PostgreSQL (Railway fornece automaticamente)
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Configuração manual PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('PGDATABASE', 'unified_chronicles'),
            'USER': os.environ.get('PGUSER', 'postgres'),
            'PASSWORD': os.environ.get('PGPASSWORD', ''),
            'HOST': os.environ.get('PGHOST', 'localhost'),
            'PORT': os.environ.get('PGPORT', '5432'),
        }
    }

# Static files (Whitenoise para servir arquivos estáticos)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware Whitenoise (deve ser logo após SecurityMiddleware)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Media files (Railway pode servir ou usar AWS S3)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security Settings para produção
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CORS (se necessário)
CORS_ALLOWED_ORIGINS = [
    f"https://{os.environ.get('RAILWAY_STATIC_URL', '')}",
] if os.environ.get('RAILWAY_STATIC_URL') else []

CORS_ALLOW_ALL_ORIGINS = True  # Para desenvolvimento, em produção especifique domínios

# Logging para Railway
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache (usar Redis se disponível)
if 'REDIS_URL' in os.environ:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Session engine (usar cache se disponível)
if 'REDIS_URL' in os.environ:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'