from django.apps import AppConfig


class SessoesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sessoes'
    verbose_name = 'Sessões de Jogo'
    
    def ready(self):
        """Configurações quando a aplicação estiver pronta"""
        pass