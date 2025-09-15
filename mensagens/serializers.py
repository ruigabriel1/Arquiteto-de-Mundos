"""
Serializers para API REST de Chat/Mensagens
"""

from rest_framework import serializers
from .models import SalaChat, ParticipacaoChat, Mensagem, TipoMensagem
from campanhas.models import Campanha
from personagens.models import Personagem


class SalaChatListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de salas de chat"""
    
    campanha_nome = serializers.CharField(source='campanha.nome', read_only=True)
    participantes_online = serializers.IntegerField(read_only=True)
    ultima_mensagem_conteudo = serializers.SerializerMethodField()
    ultima_mensagem_timestamp = serializers.SerializerMethodField()
    mensagens_nao_lidas = serializers.SerializerMethodField()
    
    class Meta:
        model = SalaChat
        fields = [
            'id', 'nome', 'campanha_nome', 'participantes_online',
            'ultima_mensagem_conteudo', 'ultima_mensagem_timestamp',
            'mensagens_nao_lidas', 'data_atualizacao'
        ]
    
    def get_ultima_mensagem_conteudo(self, obj):
        """Conteúdo da última mensagem (truncado)"""
        if obj.ultima_mensagem:
            conteudo = obj.ultima_mensagem.conteudo
            return conteudo[:100] + '...' if len(conteudo) > 100 else conteudo
        return None
    
    def get_ultima_mensagem_timestamp(self, obj):
        """Timestamp da última mensagem"""
        if obj.ultima_mensagem:
            return obj.ultima_mensagem.timestamp.isoformat()
        return None
    
    def get_mensagens_nao_lidas(self, obj):
        """Número de mensagens não lidas para o usuário atual"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        
        try:
            participacao = obj.participacoes.get(usuario=request.user)
            return participacao.mensagens_nao_lidas
        except ParticipacaoChat.DoesNotExist:
            return 0


class SalaChatDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para sala de chat"""
    
    campanha = serializers.StringRelatedField(read_only=True)
    participantes_online = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = SalaChat
        fields = [
            'id', 'nome', 'descricao', 'campanha',
            'comandos_habilitados', 'rolagens_publicas', 'historico_visivel',
            'max_mensagens_historico', 'participantes_online',
            'data_criacao', 'data_atualizacao'
        ]


class ParticipacaoChatSerializer(serializers.ModelSerializer):
    """Serializer para participação em chat"""
    
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    username = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = ParticipacaoChat
        fields = [
            'id', 'usuario_nome', 'username', 'online', 'mutado', 
            'is_moderador', 'mensagens_nao_lidas', 'notificacoes_habilitadas',
            'primeira_conexao', 'ultima_conexao', 'ultima_mensagem_vista'
        ]


class MensagemListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de mensagens"""
    
    usuario_nome = serializers.SerializerMethodField()
    personagem_nome = serializers.CharField(source='personagem.nome', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Mensagem
        fields = [
            'id', 'tipo', 'tipo_display', 'conteudo', 'usuario_nome',
            'personagem_nome', 'editada', 'timestamp'
        ]
    
    def get_usuario_nome(self, obj):
        """Nome do usuário ou 'Sistema'"""
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return 'Sistema'


class MensagemDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para mensagem"""
    
    usuario = serializers.SerializerMethodField()
    destinatario = serializers.SerializerMethodField()
    personagem = serializers.SerializerMethodField()
    rolagem = serializers.SerializerMethodField()
    
    class Meta:
        model = Mensagem
        fields = [
            'id', 'tipo', 'conteudo', 'usuario', 'destinatario',
            'personagem', 'rolagem', 'metadados', 'editada',
            'timestamp', 'timestamp_edicao'
        ]
    
    def get_usuario(self, obj):
        """Dados do usuário"""
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'username': obj.usuario.username,
                'nome_completo': obj.usuario.get_full_name()
            }
        return None
    
    def get_destinatario(self, obj):
        """Dados do destinatário (whisper)"""
        if obj.destinatario:
            return {
                'id': obj.destinatario.id,
                'username': obj.destinatario.username,
                'nome_completo': obj.destinatario.get_full_name()
            }
        return None
    
    def get_personagem(self, obj):
        """Dados do personagem"""
        if obj.personagem:
            return {
                'id': obj.personagem.id,
                'nome': obj.personagem.nome
            }
        return None
    
    def get_rolagem(self, obj):
        """Dados da rolagem"""
        if obj.rolagem:
            return {
                'id': obj.rolagem.id,
                'expressao': obj.rolagem.expressao,
                'resultado': obj.rolagem.resultado_final,
                'resultados_individuais': obj.rolagem.resultados_individuais
            }
        return None


class EnviarMensagemSerializer(serializers.Serializer):
    """Serializer para envio de mensagens"""
    
    conteudo = serializers.CharField(
        max_length=2000,
        help_text="Conteúdo da mensagem"
    )
    
    personagem_id = serializers.IntegerField(
        required=False,
        help_text="ID do personagem (opcional)"
    )
    
    destinatario_username = serializers.CharField(
        max_length=150,
        required=False,
        help_text="Username do destinatário para whisper (opcional)"
    )
    
    def validate_conteudo(self, value):
        """Validar conteúdo da mensagem"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Mensagem não pode estar vazia")
        return value
    
    def validate_personagem_id(self, value):
        """Validar se personagem existe e pertence ao usuário"""
        if value:
            request = self.context.get('request')
            if not request:
                raise serializers.ValidationError("Contexto inválido")
            
            try:
                personagem = Personagem.objects.get(id=value)
                if personagem.usuario != request.user:
                    raise serializers.ValidationError("Personagem não pertence ao usuário")
                return value
            except Personagem.DoesNotExist:
                raise serializers.ValidationError("Personagem não encontrado")
        return value
    
    def validate_destinatario_username(self, value):
        """Validar se destinatário existe"""
        if value:
            from usuarios.models import Usuario
            try:
                Usuario.objects.get(username=value)
                return value
            except Usuario.DoesNotExist:
                raise serializers.ValidationError("Usuário destinatário não encontrado")
        return value
    
    def validate(self, data):
        """Validações cruzadas"""
        conteudo = data.get('conteudo', '')
        destinatario = data.get('destinatario_username')
        
        # Se é whisper, deve ter destinatário
        if conteudo.startswith('/whisper') or conteudo.startswith('/w'):
            if not destinatario:
                raise serializers.ValidationError({
                    'destinatario_username': 'Whisper requer destinatário'
                })
        
        return data


class ComandoChatSerializer(serializers.Serializer):
    """Serializer para comandos de chat"""
    
    comando = serializers.CharField(
        max_length=200,
        help_text="Comando a ser executado (ex: /roll 1d20+5)"
    )
    
    personagem_id = serializers.IntegerField(
        required=False,
        help_text="ID do personagem (opcional)"
    )
    
    def validate_comando(self, value):
        """Validar formato do comando"""
        value = value.strip()
        if not value.startswith('/'):
            raise serializers.ValidationError("Comando deve começar com '/'")
        return value


class EstatisticasChatSerializer(serializers.Serializer):
    """Serializer para estatísticas do chat"""
    
    total_mensagens = serializers.IntegerField()
    mensagens_por_tipo = serializers.DictField()
    participantes_online = serializers.IntegerField()
    total_participantes = serializers.IntegerField()
    mensagens_hoje = serializers.IntegerField()
    comandos_mais_usados = serializers.DictField()
    usuarios_mais_ativos = serializers.ListField()