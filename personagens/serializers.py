"""
Serializers para API REST de Personagens
"""

from rest_framework import serializers
from .models import Personagem, HistoricoPersonagem, BackupPersonagem
from sistema_unificado.models import SistemaJogo, ConteudoSistema
from campanhas.models import Campanha


class SistemaJogoSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para sistema de jogo"""
    
    class Meta:
        model = SistemaJogo
        fields = ['id', 'nome', 'versao']


class CampanhaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para campanha"""
    
    mestre_nome = serializers.CharField(source='mestre.get_full_name', read_only=True)
    
    class Meta:
        model = Campanha
        fields = ['id', 'nome', 'mestre_nome', 'status']


class PersonagemListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de personagens"""
    
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    sistema_nome = serializers.CharField(source='sistema_jogo.nome', read_only=True)
    campanha_nome = serializers.CharField(source='campanha.nome', read_only=True)
    
    class Meta:
        model = Personagem
        fields = [
            'id', 'nome', 'nivel', 'usuario_nome', 'sistema_nome', 
            'campanha_nome', 'ativo',
            'pontos_vida_atual', 'pontos_vida_maximo', 'data_criacao'
        ]


class PersonagemDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para visualização de personagem"""
    
    usuario = serializers.StringRelatedField()
    sistema_jogo = SistemaJogoSimpleSerializer(read_only=True)
    campanha = CampanhaSimpleSerializer(read_only=True)
    
    # Campos calculados
    modificador_forca = serializers.SerializerMethodField()
    modificador_destreza = serializers.SerializerMethodField()
    modificador_constituicao = serializers.SerializerMethodField()
    modificador_inteligencia = serializers.SerializerMethodField()
    modificador_sabedoria = serializers.SerializerMethodField()
    modificador_carisma = serializers.SerializerMethodField()
    
    class Meta:
        model = Personagem
        fields = [
            'id', 'nome', 'nivel', 'experiencia', 'usuario', 'sistema_jogo',
            'campanha', 'ativo',
            
            # Atributos
            'forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma',
            'modificador_forca', 'modificador_destreza', 'modificador_constituicao',
            'modificador_inteligencia', 'modificador_sabedoria', 'modificador_carisma',
            
            # Pontos de Vida e Defesas
            'pontos_vida_maximo', 'pontos_vida_atual', 'pontos_vida_temporario',
            'classe_armadura', 'iniciativa',
            
            # Equipamentos e Inventário
            'equipamentos', 'inventario', 'dinheiro',
            
            # RPG
            'personalidade', 'historia', 'anotacoes_jogador', 'anotacoes_mestre',
            
            # Timestamps
            'data_criacao', 'data_atualizacao'
        ]
    
    def get_modificador_forca(self, obj):
        return obj.calcular_modificador(obj.forca)
    
    def get_modificador_destreza(self, obj):
        return obj.calcular_modificador(obj.destreza)
    
    def get_modificador_constituicao(self, obj):
        return obj.calcular_modificador(obj.constituicao)
    
    def get_modificador_inteligencia(self, obj):
        return obj.calcular_modificador(obj.inteligencia)
    
    def get_modificador_sabedoria(self, obj):
        return obj.calcular_modificador(obj.sabedoria)
    
    def get_modificador_carisma(self, obj):
        return obj.calcular_modificador(obj.carisma)


class PersonagemCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de personagem"""
    
    class Meta:
        model = Personagem
        fields = [
            'nome', 'sistema_jogo', 'campanha',
            'forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma',
            'personalidade', 'historia'
        ]
    
    def validate(self, data):
        """Validações customizadas"""
        
        # Verificar se o usuário pode criar personagem nesta campanha
        campanha = data.get('campanha')
        if campanha:
            request = self.context.get('request')
            if request and request.user:
                # Verificar se o usuário é participante da campanha (usando ParticipacaoCampanha)
                from campanhas.models import ParticipacaoCampanha
                if not ParticipacaoCampanha.objects.filter(campanha=campanha, usuario=request.user).exists():
                    raise serializers.ValidationError({
                        'campanha': 'Você não é participante desta campanha'
                    })
        
        # Validar valores de atributos (3-18 para D&D padrão)
        atributos = ['forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma']
        for attr in atributos:
            valor = data.get(attr)
            if valor is not None and (valor < 3 or valor > 18):
                raise serializers.ValidationError({
                    attr: f'Valor deve estar entre 3 e 18. Valor fornecido: {valor}'
                })
        
        return data
    
    def create(self, validated_data):
        """Criar personagem com valores calculados"""
        
        # Definir o usuário como o usuário autenticado
        validated_data['usuario'] = self.context['request'].user
        
        # Criar o personagem
        personagem = super().create(validated_data)
        
        # Calcular pontos de vida baseado na constituição e classe
        personagem.calcular_pontos_vida_iniciais()
        
        # Calcular classe de armadura base
        personagem.calcular_classe_armadura()
        
        # Calcular iniciativa
        personagem.calcular_iniciativa()
        
        personagem.save()
        
        return personagem


class PersonagemUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de personagem"""
    
    class Meta:
        model = Personagem
        fields = [
            'nome', 'nivel', 'experiencia',
            'forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma',
            'pontos_vida_atual', 'pontos_vida_temporario',
            'equipamentos',
            'personalidade', 'historia', 'anotacoes_jogador'
        ]
    
    def validate_nivel(self, value):
        """Validar nível do personagem"""
        if value < 1 or value > 20:
            raise serializers.ValidationError('Nível deve estar entre 1 e 20')
        return value
    
    def validate_pontos_vida_atual(self, value):
        """Validar pontos de vida atuais"""
        if value < 0:
            raise serializers.ValidationError('Pontos de vida não podem ser negativos')
        return value
    
    def update(self, instance, validated_data):
        """Atualizar personagem e recalcular valores"""
        
        # Salvar valores antigos para histórico
        valores_antigos = {
            'nivel': instance.nivel,
            'pontos_vida_atual': instance.pontos_vida_atual,
            'forca': instance.forca,
            'destreza': instance.destreza,
            'constituicao': instance.constituicao,
            'inteligencia': instance.inteligencia,
            'sabedoria': instance.sabedoria,
            'carisma': instance.carisma
        }
        
        # Atualizar campos
        personagem = super().update(instance, validated_data)
        
        # Recalcular valores se atributos mudaram
        atributos_mudaram = any(
            validated_data.get(attr) != valores_antigos.get(attr)
            for attr in ['forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma']
        )
        
        if atributos_mudaram:
            personagem.calcular_classe_armadura()
            personagem.calcular_iniciativa()
        
        # Recalcular pontos de vida máximos se nível ou constituição mudou
        if (validated_data.get('nivel') != valores_antigos['nivel'] or
            validated_data.get('constituicao') != valores_antigos['constituicao']):
            personagem.calcular_pontos_vida_maximos()
        
        personagem.save()
        
        # Registrar no histórico mudanças significativas
        mudancas = []
        for campo, valor_antigo in valores_antigos.items():
            valor_novo = getattr(personagem, campo)
            if valor_novo != valor_antigo:
                mudancas.append(f'{campo}: {valor_antigo} → {valor_novo}')
        
        if mudancas:
            HistoricoPersonagem.objects.create(
                personagem=personagem,
                usuario=self.context['request'].user,
                acao='atualizacao',
                detalhes=', '.join(mudancas)
            )
        
        return personagem


class HistoricoPersonagemSerializer(serializers.ModelSerializer):
    """Serializer para histórico de mudanças do personagem"""
    
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = HistoricoPersonagem
        fields = ['id', 'acao', 'detalhes', 'usuario_nome', 'timestamp']


class BackupPersonagemSerializer(serializers.ModelSerializer):
    """Serializer para backups de personagem"""
    
    class Meta:
        model = BackupPersonagem
        fields = ['id', 'motivo', 'dados_backup', 'created_at']