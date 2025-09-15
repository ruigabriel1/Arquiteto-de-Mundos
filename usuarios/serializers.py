"""
Serializers para API REST de usuários
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para dados do usuário"""
    
    nivel_experiencia = serializers.ReadOnlyField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nome_completo', 'first_name', 'last_name',
            'data_nascimento', 'avatar', 'bio', 'nivel_experiencia',
            'campanhas_como_jogador', 'campanhas_como_mestre', 'horas_jogadas',
            'configuracoes_jogo', 'configuracoes_interface', 'is_active',
            'date_joined', 'data_ultima_atividade'
        ]
        read_only_fields = [
            'id', 'date_joined', 'data_ultima_atividade', 'nivel_experiencia'
        ]


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de usuário"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'nome_completo', 'password', 'password_confirm'
        ]
    
    def validate(self, data):
        """Validações customizadas"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem")
        return data
    
    def create(self, validated_data):
        """Criar usuário com senha criptografada"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = Usuario.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UsuarioPublicoSerializer(serializers.ModelSerializer):
    """Serializer para dados públicos do usuário"""
    
    nivel_experiencia = serializers.ReadOnlyField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'nome_completo', 'avatar', 'bio',
            'nivel_experiencia', 'campanhas_como_jogador', 
            'campanhas_como_mestre', 'date_joined'
        ]


class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        """Validar credenciais"""
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError(
                    'Credenciais inválidas. Verifique usuário e senha.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Conta desativada. Entre em contato com o administrador.'
                )
            
            data['user'] = user
            return data
        
        raise serializers.ValidationError(
            'Usuário e senha são obrigatórios.'
        )


class AlterarSenhaSerializer(serializers.Serializer):
    """Serializer para alterar senha"""
    
    senha_atual = serializers.CharField()
    nova_senha = serializers.CharField(min_length=8)
    confirmar_nova_senha = serializers.CharField()
    
    def validate(self, data):
        """Validações"""
        if data['nova_senha'] != data['confirmar_nova_senha']:
            raise serializers.ValidationError("As novas senhas não coincidem")
        return data
    
    def validate_senha_atual(self, value):
        """Validar senha atual"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta")
        return value