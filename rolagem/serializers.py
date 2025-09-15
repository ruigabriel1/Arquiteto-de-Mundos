"""
Serializers para API REST de Rolagem de Dados
"""

from rest_framework import serializers
from .models import RolagemDado, TemplateRolagem, TipoRolagem, ModificadorTipo
from campanhas.models import Campanha
from personagens.models import Personagem


class RolagemDadoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de rolagens"""
    
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)
    campanha_nome = serializers.CharField(source='campanha.nome', read_only=True)
    personagem_nome = serializers.CharField(source='personagem.nome', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    modificador_display = serializers.CharField(source='get_modificador_display', read_only=True)
    
    class Meta:
        model = RolagemDado
        fields = [
            'id', 'usuario_nome', 'campanha_nome', 'personagem_nome',
            'tipo', 'tipo_display', 'modificador', 'modificador_display',
            'expressao', 'resultado_final', 'descricao', 'data_rolagem',
            'publica', 'secreta'
        ]


class RolagemDadoDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para visualização de rolagem"""
    
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)
    campanha_nome = serializers.CharField(source='campanha.nome', read_only=True)
    personagem_nome = serializers.CharField(source='personagem.nome', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    modificador_display = serializers.CharField(source='get_modificador_display', read_only=True)
    
    class Meta:
        model = RolagemDado
        fields = [
            'id', 'usuario_nome', 'campanha_nome', 'personagem_nome',
            'tipo', 'tipo_display', 'modificador', 'modificador_display',
            'expressao', 'resultados_individuais', 'resultado_final',
            'resultado_bruto', 'modificador_valor', 'descricao',
            'metadados', 'data_rolagem', 'publica', 'secreta'
        ]


class RolarDadosSerializer(serializers.Serializer):
    """Serializer para criar nova rolagem"""
    
    expressao = serializers.CharField(
        max_length=200,
        help_text="Expressão de dados (ex: 1d20+5, 3d6+2, d20)"
    )
    
    tipo = serializers.ChoiceField(
        choices=TipoRolagem.choices,
        default=TipoRolagem.CUSTOM,
        help_text="Tipo da rolagem"
    )
    
    modificador = serializers.ChoiceField(
        choices=ModificadorTipo.choices,
        default=ModificadorTipo.NORMAL,
        help_text="Modificador (normal, vantagem, desvantagem)"
    )
    
    campanha_id = serializers.IntegerField(
        required=False,
        help_text="ID da campanha (opcional)"
    )
    
    personagem_id = serializers.IntegerField(
        required=False,
        help_text="ID do personagem (opcional)"
    )
    
    descricao = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Descrição da rolagem"
    )
    
    publica = serializers.BooleanField(
        default=True,
        help_text="Visível para outros jogadores"
    )
    
    secreta = serializers.BooleanField(
        default=False,
        help_text="Apenas mestre pode ver"
    )
    
    metadados = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Metadados adicionais (DC, contexto, etc.)"
    )
    
    def validate_expressao(self, value):
        """Validar expressão de dados"""
        from .models import ParserDados
        
        try:
            # Testar se a expressão é válida
            parser = ParserDados(value)
            return value
        except ValueError as e:
            raise serializers.ValidationError(str(e))
    
    def validate(self, data):
        """Validações customizadas"""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Usuário não autenticado")
        
        # Validar campanha
        campanha_id = data.get('campanha_id')
        if campanha_id:
            try:
                campanha = Campanha.objects.get(id=campanha_id)
                # Verificar se usuário tem acesso à campanha
                from campanhas.models import ParticipacaoCampanha
                if not (campanha.mestre == request.user or 
                       ParticipacaoCampanha.objects.filter(
                           campanha=campanha, usuario=request.user
                       ).exists()):
                    raise serializers.ValidationError({
                        'campanha_id': 'Você não tem acesso a esta campanha'
                    })
                data['campanha'] = campanha
            except Campanha.DoesNotExist:
                raise serializers.ValidationError({
                    'campanha_id': 'Campanha não encontrada'
                })
        
        # Validar personagem
        personagem_id = data.get('personagem_id')
        if personagem_id:
            try:
                personagem = Personagem.objects.get(id=personagem_id)
                # Verificar se usuário é dono do personagem ou mestre da campanha
                if not (personagem.usuario == request.user or
                       (personagem.campanha and personagem.campanha.mestre == request.user)):
                    raise serializers.ValidationError({
                        'personagem_id': 'Você não pode rolar dados por este personagem'
                    })
                data['personagem'] = personagem
            except Personagem.DoesNotExist:
                raise serializers.ValidationError({
                    'personagem_id': 'Personagem não encontrado'
                })
        
        return data
    
    def create(self, validated_data):
        """Criar rolagem"""
        request = self.context['request']
        
        # Remover campos que não são do modelo
        campanha = validated_data.pop('campanha', None)
        personagem = validated_data.pop('personagem', None)
        validated_data.pop('campanha_id', None)
        validated_data.pop('personagem_id', None)
        
        # Criar rolagem usando o método do modelo
        rolagem = RolagemDado.rolar_dados(
            usuario=request.user,
            campanha=campanha,
            personagem=personagem,
            **validated_data
        )
        
        return rolagem


class RolarAtributoSerializer(serializers.Serializer):
    """Serializer para rolagem de teste de atributo do personagem"""
    
    personagem_id = serializers.IntegerField(
        help_text="ID do personagem"
    )
    
    atributo = serializers.ChoiceField(
        choices=[
            ('forca', 'Força'),
            ('destreza', 'Destreza'),
            ('constituicao', 'Constituição'),
            ('inteligencia', 'Inteligência'),
            ('sabedoria', 'Sabedoria'),
            ('carisma', 'Carisma')
        ],
        help_text="Atributo para testar"
    )
    
    modificador = serializers.ChoiceField(
        choices=ModificadorTipo.choices,
        default=ModificadorTipo.NORMAL,
        help_text="Vantagem/Desvantagem"
    )
    
    dc = serializers.IntegerField(
        required=False,
        help_text="Dificuldade do teste (opcional)"
    )
    
    descricao = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Descrição do teste"
    )
    
    def validate_personagem_id(self, value):
        """Validar personagem"""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Contexto inválido")
        
        try:
            personagem = Personagem.objects.get(id=value)
            if not (personagem.usuario == request.user or
                   (personagem.campanha and personagem.campanha.mestre == request.user)):
                raise serializers.ValidationError("Você não pode rolar dados por este personagem")
            return value
        except Personagem.DoesNotExist:
            raise serializers.ValidationError("Personagem não encontrado")


class TemplateRolagemSerializer(serializers.ModelSerializer):
    """Serializer para templates de rolagem"""
    
    class Meta:
        model = TemplateRolagem
        fields = [
            'id', 'nome', 'expressao', 'tipo', 'descricao',
            'configuracoes', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao']
    
    def validate_expressao(self, value):
        """Validar expressão do template"""
        from .models import ParserDados
        
        try:
            parser = ParserDados(value)
            return value
        except ValueError as e:
            raise serializers.ValidationError(f"Expressão inválida: {e}")
    
    def create(self, validated_data):
        """Criar template"""
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class EstatisticasRolagemSerializer(serializers.Serializer):
    """Serializer para estatísticas de rolagem"""
    
    total_rolagens = serializers.IntegerField()
    por_tipo = serializers.DictField()
    por_resultado = serializers.DictField()
    media_resultado = serializers.FloatField()
    rolagem_mais_alta = serializers.IntegerField()
    rolagem_mais_baixa = serializers.IntegerField()
    dados_mais_usados = serializers.DictField()