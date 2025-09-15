"""
Views para API REST de usuários
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.utils import timezone

from .models import Usuario
from .serializers import (
    UsuarioSerializer, UsuarioCreateSerializer, UsuarioPublicoSerializer,
    LoginSerializer, AlterarSenhaSerializer
)


class UsuarioCreateView(generics.CreateAPIView):
    """Endpoint para registro de novos usuários"""
    
    serializer_class = UsuarioCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Criar token para o usuário
        token, created = Token.objects.get_or_create(user=user)
        
        # Serializar dados do usuário criado
        user_data = UsuarioSerializer(user).data
        
        return Response({
            'message': 'Usuário criado com sucesso!',
            'user': user_data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class UsuarioProfileView(generics.RetrieveUpdateAPIView):
    """Endpoint para visualizar e editar perfil do usuário"""
    
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Retorna o próprio usuário logado"""
        return self.request.user


class UsuarioListView(generics.ListAPIView):
    """Endpoint para listar usuários (dados públicos)"""
    
    queryset = Usuario.objects.filter(is_active=True)
    serializer_class = UsuarioPublicoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtros opcionais"""
        queryset = super().get_queryset()
        
        # Filtro por busca
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                nome_completo__icontains=search
            ) | queryset.filter(
                username__icontains=search
            )
        
        return queryset.order_by('-date_joined')


class UsuarioDetailView(generics.RetrieveAPIView):
    """Endpoint para visualizar dados públicos de um usuário"""
    
    queryset = Usuario.objects.filter(is_active=True)
    serializer_class = UsuarioPublicoSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Endpoint para login"""
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Atualizar última atividade
        user.data_ultima_atividade = timezone.now()
        user.save(update_fields=['data_ultima_atividade'])
        
        # Criar/obter token
        token, created = Token.objects.get_or_create(user=user)
        
        # Fazer login na sessão
        login(request, user)
        
        return Response({
            'message': 'Login realizado com sucesso!',
            'user': UsuarioSerializer(user).data,
            'token': token.key
        })
    
    return Response(
        {'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Endpoint para logout"""
    try:
        # Deletar token
        token = Token.objects.get(user=request.user)
        token.delete()
    except Token.DoesNotExist:
        pass
    
    # Logout da sessão
    logout(request)
    
    return Response({
        'message': 'Logout realizado com sucesso!'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def alterar_senha_view(request):
    """Endpoint para alterar senha"""
    serializer = AlterarSenhaSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['nova_senha'])
        user.save()
        
        # Invalidar token atual
        try:
            token = Token.objects.get(user=user)
            token.delete()
        except Token.DoesNotExist:
            pass
        
        # Criar novo token
        new_token = Token.objects.create(user=user)
        
        return Response({
            'message': 'Senha alterada com sucesso!',
            'token': new_token.key
        })
    
    return Response(
        {'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def estatisticas_view(request):
    """Endpoint para estatísticas do usuário"""
    user = request.user
    
    # Calcular estatísticas
    total_personagens = user.personagens.count()
    personagens_ativos = user.personagens.filter(ativo=True).count()
    campanhas_participando = user.campanhas_participando.filter(
        participacoes__ativo=True
    ).count()
    
    return Response({
        'usuario': user.username,
        'nivel_experiencia': user.nivel_experiencia,
        'horas_jogadas': user.horas_jogadas,
        'campanhas_como_mestre': user.campanhas_como_mestre,
        'campanhas_como_jogador': user.campanhas_como_jogador,
        'campanhas_ativas': campanhas_participando,
        'total_personagens': total_personagens,
        'personagens_ativos': personagens_ativos,
        'membro_desde': user.date_joined,
        'pode_mestrar': user.pode_mestrar()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def atualizar_configuracoes_view(request):
    """Endpoint para atualizar configurações do usuário"""
    user = request.user
    
    # Configurações de jogo
    if 'configuracoes_jogo' in request.data:
        user.configuracoes_jogo.update(request.data['configuracoes_jogo'])
    
    # Configurações de interface
    if 'configuracoes_interface' in request.data:
        user.configuracoes_interface.update(request.data['configuracoes_interface'])
    
    user.save(update_fields=['configuracoes_jogo', 'configuracoes_interface'])
    
    return Response({
        'message': 'Configurações atualizadas com sucesso!',
        'configuracoes_jogo': user.configuracoes_jogo,
        'configuracoes_interface': user.configuracoes_interface
    })
