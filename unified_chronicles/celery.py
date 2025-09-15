"""
Configuração do Celery para Unified Chronicles
Usado para processamento assíncrono de IA e outras tarefas pesadas
"""

import os
from celery import Celery

# Define o módulo de configurações Django para o programa 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_chronicles.settings')

app = Celery('unified_chronicles')

# Usando a string aqui significa que o worker não precisa serializar
# o objeto de configuração para processos filhos.
# - namespace='CELERY' significa que todas as configurações relacionadas ao celery
#   devem ter um prefixo CELERY_.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carrega módulos de tarefas de todas as apps registradas no Django.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """Tarefa de debug para testar o Celery"""
    print(f'Request: {self.request!r}')

# Configurações específicas para IA
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_routes={
        'ia_gm.tasks.processar_mensagem_ia': {'queue': 'ia_gm'},
        'ia_gm.tasks.gerar_imagem': {'queue': 'imagens'},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
)