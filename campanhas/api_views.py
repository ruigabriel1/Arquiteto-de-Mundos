"""
Views para API REST de campanhas
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404

from .models import Campanha, ParticipacaoCampanha, ConviteCampanha
from usuarios.models import Usuario
from .serializers import (
    CampanhaSerializer, CampanhaCreateSerializer, CampanhaListSerializer,
    ConviteCampanhaSerializer, ConvidarJogadorSerializer, ResponderConviteSerializer
)


class CampanhaListCreateView(generics.ListCreateAPIView):
    """Endpoint para listar e criar campanhas"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CampanhaCreateSerializer
        return CampanhaListSerializer
    
    def get_queryset(self):
        """Filtrar campanhas baseado nos parâmetros"""
        queryset = Campanha.objects.select_related(
            'organizador', 'sistema_jogo'
        ).prefetch_related('participacoes__usuario')
        
        # Filtro por tipo
        tipo = self.request.query_params.get('tipo')
        if tipo == 'minhas':
            # Campanhas que o usuário é organizador
            queryset = queryset.filter(organizador=self.request.user)
        elif tipo == 'participando':
            # Campanhas que o usuário participa
            queryset = queryset.filter(
                participacoes__usuario=self.request.user,
                participacoes__ativo=True
            )
        elif tipo == 'abertas':
            # Campanhas com vagas e ativas
            queryset = queryset.filter(estado='ativa')
            # Filtrar apenas as que têm vagas (será feito na consulta)
        
        # Filtro por sistema
        sistema = self.request.query_params.get('sistema')
        if sistema:
            queryset = queryset.filter(sistema_jogo__codigo=sistema)
        
        # Filtro por busca
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(nome__icontains=search)
        
        return queryset.order_by('-data_atualizacao')


class CampanhaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint para visualizar, editar e deletar campanha"""
    
    serializer_class = CampanhaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Campanha.objects.select_related(
            'organizador', 'sistema_jogo'
        ).prefetch_related('participacoes__usuario')
    
    def get_object(self):
        """Verificar permissões de acesso"""
        campanha = super().get_object()
        
        # Verificar se pode visualizar
        if not self.pode_visualizar_campanha(campanha):
            self.permission_denied(
                self.request, message="Você não tem permissão para acessar esta campanha."
            )
        
        return campanha
    
    def pode_visualizar_campanha(self, campanha):
        """Verifica se o usuário pode visualizar a campanha"""
        user = self.request.user
        
        # Organizador pode sempre visualizar
        if campanha.organizador == user:
            return True
        
        # Participantes ativos podem visualizar
        if campanha.participacoes.filter(usuario=user, ativo=True).exists():
            return True
        
        # Campanhas abertas todos podem visualizar
        if campanha.estado in ['ativa', 'planejamento']:
            return True
        
        return False
    
    def update(self, request, *args, **kwargs):
        """Apenas o organizador pode editar"""
        campanha = self.get_object()
        
        if campanha.organizador != request.user:
            return Response(
                {'error': 'Apenas o organizador pode editar a campanha.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Apenas o organizador pode deletar"""
        campanha = self.get_object()
        
        if campanha.organizador != request.user:
            return Response(
                {'error': 'Apenas o organizador pode deletar a campanha.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def convidar_jogador_view(request, campanha_id):
    """Endpoint para convidar jogador para campanha"""
    campanha = get_object_or_404(Campanha, id=campanha_id)
    
    # Verificar se é o organizador
    if campanha.organizador != request.user:
        return Response(
            {'error': 'Apenas o organizador pode convidar jogadores.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Verificar se a campanha tem vagas
    if not campanha.tem_vagas:
        return Response(
            {'error': 'A campanha está lotada.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = ConvidarJogadorSerializer(
        data=request.data,
        context={'campanha': campanha, 'organizador': request.user}
    )
    
    if serializer.is_valid():
        # Buscar o usuário
        usuario = Usuario.objects.get(id=serializer.validated_data['usuario_id'])
        
        # Criar convite
        convite = ConviteCampanha.objects.create(
            campanha=campanha,
            convidado=usuario,
            convidado_por=request.user,
            mensagem=serializer.validated_data.get('mensagem', ''),
            data_expiracao=timezone.now() + timedelta(
                days=serializer.validated_data['dias_expiracao']
            )
        )
        
        return Response({
            'message': f'Convite enviado para {usuario.nome_completo}!',
            'convite': ConviteCampanhaSerializer(convite).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(
        {'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def meus_convites_view(request):
    """Endpoint para listar convites do usuário"""
    convites = ConviteCampanha.objects.filter(
        convidado=request.user
    ).select_related(
        'campanha__organizador', 'campanha__sistema_jogo', 'convidado_por'
    ).order_by('-data_convite')
    
    # Filtro por estado
    estado = request.query_params.get('estado')
    if estado:
        convites = convites.filter(estado=estado)
    
    serializer = ConviteCampanhaSerializer(convites, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def responder_convite_view(request, convite_id):
    """Endpoint para responder a um convite"""
    convite = get_object_or_404(
        ConviteCampanha,
        id=convite_id,
        convidado=request.user
    )
    
    serializer = ResponderConviteSerializer(
        data=request.data,
        context={'convite': convite}
    )
    
    if serializer.is_valid():
        resposta = serializer.validated_data['resposta']
        
        # Atualizar convite
        convite.data_resposta = timezone.now()
        
        if resposta == 'aceitar':
            convite.estado = 'aceito'
            
            # Criar participação na campanha
            ParticipacaoCampanha.objects.create(
                usuario=request.user,
                campanha=convite.campanha
            )
            
            message = f'Você foi adicionado à campanha "{convite.campanha.nome}"!'
            
        else:  # recusar
            convite.estado = 'recusado'
            message = 'Convite recusado.'
        
        convite.save()
        
        return Response({
            'message': message,
            'convite': ConviteCampanhaSerializer(convite).data
        })
    
    return Response(
        {'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def sair_campanha_view(request, campanha_id):
    """Endpoint para sair de uma campanha"""
    campanha = get_object_or_404(Campanha, id=campanha_id)
    
    # Verificar se o usuário participa da campanha
    try:
        participacao = ParticipacaoCampanha.objects.get(
            campanha=campanha,
            usuario=request.user,
            ativo=True
        )
    except ParticipacaoCampanha.DoesNotExist:
        return Response(
            {'error': 'Você não participa desta campanha.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Organizador não pode sair da própria campanha
    if campanha.organizador == request.user:
        return Response(
            {'error': 'O organizador não pode sair da própria campanha. Delete a campanha se necessário.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Marcar participação como inativa
    participacao.ativo = False
    participacao.data_saida = timezone.now()
    participacao.save()
    
    return Response({
        'message': f'Você saiu da campanha "{campanha.nome}".'
    })
