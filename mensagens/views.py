"""
Views para API REST de Chat/Mensagens
"""

from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Case, When, IntegerField, Value
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import SalaChat, ParticipacaoChat, Mensagem, TipoMensagem
from .serializers import (
    SalaChatListSerializer, SalaChatDetailSerializer,
    ParticipacaoChatSerializer, MensagemListSerializer,
    MensagemDetailSerializer, EnviarMensagemSerializer,
    ComandoChatSerializer, EstatisticasChatSerializer
)
from campanhas.models import Campanha
from personagens.models import Personagem
from usuarios.models import Usuario


class MensagemPagination(PageNumberPagination):
    """Paginação específica para mensagens"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class SalaChatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para salas de chat
    
    Permite visualizar e interagir com salas de chat das campanhas
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SalaChatListSerializer
        return SalaChatDetailSerializer
    
    def get_queryset(self):
        """Retorna salas de chat onde o usuário pode participar"""
        user = self.request.user
        return SalaChat.objects.filter(
            campanha__participantes=user
        ).annotate(
            participantes_online=Count(
                'participacoes',
                filter=Q(participacoes__online=True)
            )
        ).prefetch_related(
            'campanha',
            'ultima_mensagem',
            'participacoes'
        ).order_by('-data_atualizacao')
    
    @action(detail=True, methods=['post'])
    def entrar(self, request, pk=None):
        """Entrar em uma sala de chat"""
        sala = get_object_or_404(SalaChat, pk=pk)
        
        # Verificar se usuário tem acesso à campanha
        if not sala.campanha.participantes.filter(id=request.user.id).exists():
            return Response(
                {'erro': 'Acesso negado à sala desta campanha'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Criar ou atualizar participação
        participacao, created = ParticipacaoChat.objects.get_or_create(
            sala=sala,
            usuario=request.user,
            defaults={
                'primeira_conexao': timezone.now(),
                'online': True
            }
        )
        
        if not created:
            participacao.online = True
            participacao.ultima_conexao = timezone.now()
            participacao.save()
        
        return Response({
            'sucesso': 'Entrou na sala de chat',
            'participacao': ParticipacaoChatSerializer(participacao).data
        })
    
    @action(detail=True, methods=['post'])
    def sair(self, request, pk=None):
        """Sair de uma sala de chat"""
        sala = get_object_or_404(SalaChat, pk=pk)
        
        try:
            participacao = ParticipacaoChat.objects.get(
                sala=sala,
                usuario=request.user
            )
            participacao.online = False
            participacao.save()
            
            return Response({'sucesso': 'Saiu da sala de chat'})
        except ParticipacaoChat.DoesNotExist:
            return Response(
                {'erro': 'Usuário não está na sala'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True)
    def participantes(self, request, pk=None):
        """Listar participantes da sala"""
        sala = get_object_or_404(SalaChat, pk=pk)
        
        # Verificar acesso
        if not sala.campanha.participantes.filter(id=request.user.id).exists():
            return Response(
                {'erro': 'Acesso negado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        participacoes = sala.participacoes.select_related('usuario').order_by(
            '-online', '-ultima_conexao'
        )
        
        serializer = ParticipacaoChatSerializer(participacoes, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def estatisticas(self, request, pk=None):
        """Estatísticas da sala de chat"""
        sala = get_object_or_404(SalaChat, pk=pk)
        
        # Verificar acesso
        if not sala.campanha.participantes.filter(id=request.user.id).exists():
            return Response(
                {'erro': 'Acesso negado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calcular estatísticas
        mensagens = sala.mensagens.all()
        hoje = timezone.now().date()
        
        stats = {
            'total_mensagens': mensagens.count(),
            'mensagens_por_tipo': dict(
                mensagens.values('tipo').annotate(
                    total=Count('tipo')
                ).values_list('tipo', 'total')
            ),
            'participantes_online': sala.participacoes.filter(online=True).count(),
            'total_participantes': sala.participacoes.count(),
            'mensagens_hoje': mensagens.filter(timestamp__date=hoje).count(),
            'comandos_mais_usados': dict(
                mensagens.filter(
                    tipo__in=[TipoMensagem.COMANDO_ROLAGEM, TipoMensagem.COMANDO_ACAO]
                ).extra(
                    select={'comando': "substring(conteudo from '^/(\\w+)')"}  
                ).values('comando').annotate(
                    total=Count('comando')
                ).order_by('-total')[:5].values_list('comando', 'total')
            ),
            'usuarios_mais_ativos': list(
                mensagens.values('usuario__username').annotate(
                    total=Count('usuario')
                ).order_by('-total')[:5].values_list('usuario__username', flat=True)
            )
        }
        
        serializer = EstatisticasChatSerializer(stats)
        return Response(serializer.data)


class MensagemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para mensagens de chat
    
    Permite visualizar histórico de mensagens e enviar novas mensagens
    """
    permission_classes = [IsAuthenticated]
    pagination_class = MensagemPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MensagemListSerializer
        return MensagemDetailSerializer
    
    def get_queryset(self):
        """Retorna mensagens das salas que o usuário pode acessar"""
        user = self.request.user
        sala_id = self.request.query_params.get('sala_id')
        
        # Base queryset - mensagens de salas que o usuário pode acessar
        queryset = Mensagem.objects.filter(
            sala__campanha__participantes=user
        ).select_related(
            'usuario', 'destinatario', 'personagem', 'rolagem', 'sala'
        )
        
        # Filtrar por sala específica
        if sala_id:
            queryset = queryset.filter(sala_id=sala_id)
        
        # Filtrar mensagens privadas (whisper)
        queryset = queryset.filter(
            Q(tipo__in=[
                TipoMensagem.NORMAL,
                TipoMensagem.COMANDO_ACAO,
                TipoMensagem.COMANDO_ROLAGEM,
                TipoMensagem.SISTEMA
            ]) |
            Q(tipo=TipoMensagem.WHISPER, usuario=user) |
            Q(tipo=TipoMensagem.WHISPER, destinatario=user)
        )
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['post'])
    def enviar(self, request):
        """Enviar nova mensagem"""
        sala_id = request.data.get('sala_id')
        
        if not sala_id:
            return Response(
                {'erro': 'sala_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar sala
        try:
            sala = SalaChat.objects.get(
                id=sala_id,
                campanha__participantes=request.user
            )
        except SalaChat.DoesNotExist:
            return Response(
                {'erro': 'Sala não encontrada ou acesso negado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar dados
        serializer = EnviarMensagemSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Processar mensagem
        resultado = self._processar_mensagem(
            sala, 
            request.user,
            serializer.validated_data
        )
        
        if 'erro' in resultado:
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
        
        # Retornar mensagem criada
        mensagem_serializer = MensagemDetailSerializer(resultado['mensagem'])
        return Response(mensagem_serializer.data, status=status.HTTP_201_CREATED)
    
    def _processar_mensagem(self, sala, usuario, dados):
        """Processar e criar mensagem"""
        conteudo = dados['conteudo']
        personagem_id = dados.get('personagem_id')
        destinatario_username = dados.get('destinatario_username')
        
        # Obter personagem se fornecido
        personagem = None
        if personagem_id:
            try:
                personagem = Personagem.objects.get(
                    id=personagem_id,
                    usuario=usuario
                )
            except Personagem.DoesNotExist:
                return {'erro': 'Personagem não encontrado'}
        
        # Obter destinatário se fornecido
        destinatario = None
        if destinatario_username:
            try:
                destinatario = Usuario.objects.get(username=destinatario_username)
            except Usuario.DoesNotExist:
                return {'erro': 'Destinatário não encontrado'}
        
        # Criar mensagem
        mensagem = Mensagem.objects.create(
            sala=sala,
            usuario=usuario,
            personagem=personagem,
            destinatario=destinatario,
            conteudo=conteudo
        )
        
        # Processar comando se necessário
        if conteudo.startswith('/'):
            resultado_comando = mensagem.processar_comando()
            if resultado_comando and 'erro' in resultado_comando:
                mensagem.delete()  # Remover mensagem com erro
                return resultado_comando
        
        # Atualizar participação do usuário
        try:
            participacao = ParticipacaoChat.objects.get(
                sala=sala,
                usuario=usuario
            )
            participacao.ultima_mensagem_vista = timezone.now()
            participacao.save()
        except ParticipacaoChat.DoesNotExist:
            # Criar participação se não existir
            ParticipacaoChat.objects.create(
                sala=sala,
                usuario=usuario,
                primeira_conexao=timezone.now(),
                online=True,
                ultima_mensagem_vista=timezone.now()
            )
        
        # Atualizar contador de mensagens não lidas para outros participantes
        outros_participantes = ParticipacaoChat.objects.filter(
            sala=sala
        ).exclude(usuario=usuario)
        
        for participacao in outros_participantes:
            if participacao.ultima_mensagem_vista < mensagem.timestamp:
                participacao.mensagens_nao_lidas += 1
                participacao.save()
        
        return {'mensagem': mensagem}
    
    @action(detail=False, methods=['post'])
    def comando(self, request):
        """Executar comando de chat"""
        sala_id = request.data.get('sala_id')
        
        if not sala_id:
            return Response(
                {'erro': 'sala_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar sala
        try:
            sala = SalaChat.objects.get(
                id=sala_id,
                campanha__participantes=request.user
            )
        except SalaChat.DoesNotExist:
            return Response(
                {'erro': 'Sala não encontrada ou acesso negado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar comando
        serializer = ComandoChatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        comando = serializer.validated_data['comando']
        personagem_id = serializer.validated_data.get('personagem_id')
        
        # Obter personagem se fornecido
        personagem = None
        if personagem_id:
            try:
                personagem = Personagem.objects.get(
                    id=personagem_id,
                    usuario=request.user
                )
            except Personagem.DoesNotExist:
                return Response(
                    {'erro': 'Personagem não encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Criar mensagem de comando
        mensagem = Mensagem.objects.create(
            sala=sala,
            usuario=request.user,
            personagem=personagem,
            conteudo=comando
        )
        
        # Processar comando
        resultado = mensagem.processar_comando()
        
        if resultado and 'erro' in resultado:
            mensagem.delete()
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
        
        # Retornar mensagem criada
        mensagem_serializer = MensagemDetailSerializer(mensagem)
        return Response(mensagem_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def marcar_lidas(self, request):
        """Marcar mensagens como lidas"""
        sala_id = request.data.get('sala_id')
        
        if not sala_id:
            return Response(
                {'erro': 'sala_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar sala
        try:
            sala = SalaChat.objects.get(
                id=sala_id,
                campanha__participantes=request.user
            )
        except SalaChat.DoesNotExist:
            return Response(
                {'erro': 'Sala não encontrada ou acesso negado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Atualizar participação
        try:
            participacao = ParticipacaoChat.objects.get(
                sala=sala,
                usuario=request.user
            )
            participacao.mensagens_nao_lidas = 0
            participacao.ultima_mensagem_vista = timezone.now()
            participacao.save()
            
            return Response({'sucesso': 'Mensagens marcadas como lidas'})
        except ParticipacaoChat.DoesNotExist:
            return Response(
                {'erro': 'Usuário não está na sala'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ParticipacaoChatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para participações em chat
    
    Permite gerenciar participação do usuário em salas de chat
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ParticipacaoChatSerializer
    
    def get_queryset(self):
        """Retorna participações do usuário atual"""
        return ParticipacaoChat.objects.filter(
            usuario=self.request.user
        ).select_related(
            'usuario', 'sala', 'sala__campanha'
        ).order_by('-ultima_conexao')
    
    @action(detail=True, methods=['patch'])
    def configuracoes(self, request, pk=None):
        """Atualizar configurações de participação"""
        participacao = get_object_or_404(
            ParticipacaoChat,
            pk=pk,
            usuario=request.user
        )
        
        # Campos permitidos para atualização
        campos_permitidos = ['mutado', 'notificacoes_habilitadas']
        
        for campo in campos_permitidos:
            if campo in request.data:
                setattr(participacao, campo, request.data[campo])
        
        participacao.save()
        
        serializer = self.get_serializer(participacao)
        return Response(serializer.data)
