"""
Serializers para API REST de campanhas
"""

from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from .models import Campanha, ParticipacaoCampanha, ConviteCampanha
from usuarios.serializers import UsuarioPublicoSerializer
from sistema_unificado.models import SistemaJogo


class SistemaJogoSimpleSerializer(serializers.ModelSerializer):
    """Serializer simples para sistema de jogo"""
    
    class Meta:
        model = SistemaJogo
        fields = ['id', 'nome', 'codigo', 'versao']


class ParticipacaoCampanhaSerializer(serializers.ModelSerializer):
    """Serializer para participação em campanha"""
    
    usuario = UsuarioPublicoSerializer(read_only=True)
    dias_participando = serializers.SerializerMethodField()
    
    class Meta:
        model = ParticipacaoCampanha
        fields = [
            'id', 'usuario', 'data_entrada', 'data_saida', 
            'ativo', 'observacoes', 'dias_participando'
        ]
    
    def get_dias_participando(self, obj):
        """Calcula dias de participação"""
        if obj.data_saida:
            delta = obj.data_saida - obj.data_entrada
        else:
            delta = timezone.now() - obj.data_entrada
        return delta.days


class CampanhaSerializer(serializers.ModelSerializer):
    """Serializer completo para campanha"""
    
    organizador = UsuarioPublicoSerializer(read_only=True)
    sistema_jogo = SistemaJogoSimpleSerializer(read_only=True)
    participacoes = ParticipacaoCampanhaSerializer(many=True, read_only=True)
    
    # Campos calculados
    num_jogadores = serializers.ReadOnlyField()
    tem_vagas = serializers.ReadOnlyField()
    duracao_dias = serializers.ReadOnlyField()
    
    class Meta:
        model = Campanha
        fields = [
            'id', 'nome', 'descricao', 'organizador', 'sistema_jogo',
            'nivel_inicial', 'nivel_maximo', 'max_jogadores',
            'ia_ativa', 'configuracoes_ia', 'personalidade_gm',
            'estado', 'data_criacao', 'data_inicio', 'data_ultima_sessao',
            'configuracoes_gerais', 'participacoes',
            # Campos calculados
            'num_jogadores', 'tem_vagas', 'duracao_dias'
        ]
        read_only_fields = ['data_criacao', 'data_ultima_sessao']


class CampanhaCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de campanha"""
    
    sistema_jogo_id = serializers.IntegerField()
    
    class Meta:
        model = Campanha
        fields = [
            'nome', 'descricao', 'sistema_jogo_id',
            'nivel_inicial', 'nivel_maximo', 'max_jogadores',
            'ia_ativa', 'configuracoes_ia', 'personalidade_gm',
            'configuracoes_gerais'
        ]
    
    def validate_sistema_jogo_id(self, value):
        """Validar se o sistema de jogo existe"""
        try:
            SistemaJogo.objects.get(id=value, ativo=True)
        except SistemaJogo.DoesNotExist:
            raise serializers.ValidationError("Sistema de jogo não encontrado")
        return value
    
    def validate(self, data):
        """Validações gerais"""
        if data['nivel_inicial'] > data['nivel_maximo']:
            raise serializers.ValidationError(
                "Nível inicial não pode ser maior que o máximo"
            )
        
        if data['max_jogadores'] < 2:
            raise serializers.ValidationError(
                "Uma campanha precisa ter pelo menos 2 jogadores"
            )
        
        return data
    
    def create(self, validated_data):
        """Criar campanha com mestre"""
        sistema_jogo_id = validated_data.pop('sistema_jogo_id')
        sistema_jogo = SistemaJogo.objects.get(id=sistema_jogo_id)
        
        campanha = Campanha.objects.create(
            organizador=self.context['request'].user,
            sistema_jogo=sistema_jogo,
            **validated_data
        )
        return campanha


class CampanhaListSerializer(serializers.ModelSerializer):
    """Serializer para lista de campanhas (dados resumidos)"""
    
    organizador = UsuarioPublicoSerializer(read_only=True)
    sistema_jogo = SistemaJogoSimpleSerializer(read_only=True)
    
    # Campos calculados
    num_jogadores = serializers.ReadOnlyField()
    tem_vagas = serializers.ReadOnlyField()
    
    class Meta:
        model = Campanha
        fields = [
            'id', 'nome', 'descricao', 'organizador', 'sistema_jogo',
            'nivel_inicial', 'nivel_maximo', 'max_jogadores',
            'estado', 'ia_ativa', 'data_criacao',
            'num_jogadores', 'tem_vagas'
        ]


class ConviteCampanhaSerializer(serializers.ModelSerializer):
    """Serializer para convites de campanha"""
    
    campanha = CampanhaListSerializer(read_only=True)
    convidado = UsuarioPublicoSerializer(read_only=True)
    convidado_por = UsuarioPublicoSerializer(read_only=True)
    expirado = serializers.ReadOnlyField()
    
    class Meta:
        model = ConviteCampanha
        fields = [
            'id', 'campanha', 'convidado', 'convidado_por',
            'estado', 'mensagem', 'data_convite', 'data_resposta',
            'data_expiracao', 'expirado'
        ]
        read_only_fields = ['data_convite', 'data_resposta']


class ConvidarJogadorSerializer(serializers.Serializer):
    """Serializer para convidar jogador"""
    
    usuario_id = serializers.IntegerField()
    mensagem = serializers.CharField(max_length=500, required=False, allow_blank=True)
    dias_expiracao = serializers.IntegerField(default=7, min_value=1, max_value=30)
    
    def validate_usuario_id(self, value):
        """Validar se o usuário existe"""
        from usuarios.models import Usuario
        
        try:
            usuario = Usuario.objects.get(id=value, is_active=True)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado")
        
        # Verificar se não é o próprio organizador
        if usuario == self.context['organizador']:
            raise serializers.ValidationError("Você não pode se convidar")
        
        # Verificar se já não está na campanha
        campanha = self.context['campanha']
        if campanha.participacoes.filter(usuario=usuario, ativo=True).exists():
            raise serializers.ValidationError("Usuário já participa desta campanha")
        
        # Verificar se já não tem convite pendente
        if campanha.convites.filter(
            convidado=usuario, 
            estado='pendente'
        ).exists():
            raise serializers.ValidationError("Usuário já possui convite pendente")
        
        return value


class ResponderConviteSerializer(serializers.Serializer):
    """Serializer para responder convite"""
    
    OPCOES_RESPOSTA = [
        ('aceitar', 'Aceitar'),
        ('recusar', 'Recusar'),
    ]
    
    resposta = serializers.ChoiceField(choices=OPCOES_RESPOSTA)
    
    def validate(self, data):
        """Validações"""
        convite = self.context['convite']
        
        if convite.estado != 'pendente':
            raise serializers.ValidationError("Este convite não está mais disponível")
        
        if convite.expirado:
            raise serializers.ValidationError("Este convite expirou")
        
        return data