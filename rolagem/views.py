"""
Views da API REST para Sistema de Rolagem de Dados
"""

from django.db.models import Q, Count, Avg, Max, Min
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import RolagemDado, TemplateRolagem, TipoRolagem, ModificadorTipo
from .serializers import (
    RolagemDadoListSerializer, RolagemDadoDetailSerializer,
    RolarDadosSerializer, RolarAtributoSerializer,
    TemplateRolagemSerializer, EstatisticasRolagemSerializer
)
from personagens.models import Personagem
from campanhas.models import ParticipacaoCampanha


class RolagemPermission(permissions.BasePermission):
    """
    Permissões para rolagens:
    - Usuário vê suas próprias rolagens
    - Mestre da campanha vê rolagens da campanha (exceto secretas)
    - Jogadores veem rolagens públicas da campanha
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Superusuário pode tudo
        if request.user.is_superuser:
            return True
        
        # Dono da rolagem pode ver
        if obj.usuario == request.user:
            return True
        
        # Se é rolagem secreta, apenas o dono e o mestre podem ver
        if obj.secreta:
            if obj.campanha and obj.campanha.mestre == request.user:
                return True
            return False
        
        # Se é pública e o usuário é participante da campanha
        if obj.publica and obj.campanha:
            if obj.campanha.mestre == request.user:
                return True
            
            # Verificar se é participante
            return ParticipacaoCampanha.objects.filter(
                campanha=obj.campanha, usuario=request.user
            ).exists()
        
        return False


class RolagemDadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de rolagens de dados
    
    - GET /api/rolagem/ - Listar rolagens do usuário/campanha
    - POST /api/rolagem/rolar/ - Fazer nova rolagem
    - GET /api/rolagem/{id}/ - Detalhes da rolagem
    - DELETE /api/rolagem/{id}/ - Excluir rolagem
    """
    
    permission_classes = [IsAuthenticated, RolagemPermission]
    
    def get_serializer_class(self):
        """Escolher serializer baseado na ação"""
        if self.action == 'list':
            return RolagemDadoListSerializer
        elif self.action == 'rolar':
            return RolarDadosSerializer
        elif self.action == 'rolar_atributo':
            return RolarAtributoSerializer
        else:
            return RolagemDadoDetailSerializer
    
    def get_queryset(self):
        """
        Filtrar rolagens baseado no usuário e campanha
        """
        user = self.request.user
        
        if user.is_superuser:
            return RolagemDado.objects.all()
        
        # Rolagens próprias
        rolagens_proprias = Q(usuario=user)
        
        # Rolagens públicas de campanhas que participa
        campanhas_participante = ParticipacaoCampanha.objects.filter(
            usuario=user
        ).values_list('campanha_id', flat=True)
        
        rolagens_campanhas = Q(
            campanha_id__in=campanhas_participante,
            publica=True,
            secreta=False
        )
        
        # Rolagens de campanhas que é mestre (incluindo secretas)
        rolagens_mestre = Q(campanha__mestre=user)
        
        return RolagemDado.objects.filter(
            rolagens_proprias | rolagens_campanhas | rolagens_mestre
        ).select_related(
            'usuario', 'campanha', 'personagem'
        ).distinct().order_by('-data_rolagem')
    
    def create(self, request, *args, **kwargs):
        """Desabilitar criação direta - usar action 'rolar'"""
        return Response(
            {'error': 'Use o endpoint /rolar/ para fazer rolagens'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def update(self, request, *args, **kwargs):
        """Desabilitar edição de rolagens"""
        return Response(
            {'error': 'Rolagens não podem ser editadas'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """Desabilitar edição parcial"""
        return self.update(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def rolar(self, request):
        """
        POST /api/rolagem/rolar/
        Fazer nova rolagem de dados
        """
        serializer = RolarDadosSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                rolagem = serializer.save()
                response_serializer = RolagemDadoDetailSerializer(rolagem)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': f'Erro ao criar rolagem: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def rolar_atributo(self, request):
        """
        POST /api/rolagem/rolar_atributo/
        Rolar teste de atributo de personagem
        """
        serializer = RolarAtributoSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                personagem_id = serializer.validated_data['personagem_id']
                atributo = serializer.validated_data['atributo']
                modificador = serializer.validated_data.get('modificador', ModificadorTipo.NORMAL)
                dc = serializer.validated_data.get('dc')
                descricao = serializer.validated_data.get('descricao', '')
                
                # Buscar personagem
                personagem = Personagem.objects.get(id=personagem_id)
                
                # Obter valor do atributo e modificador
                valor_atributo = getattr(personagem, atributo)
                mod_atributo = personagem.calcular_modificador(valor_atributo)
                
                # Criar expressão da rolagem
                expressao = f"1d20{'+' if mod_atributo >= 0 else ''}{mod_atributo}"
                
                # Preparar metadados
                metadados = {
                    'atributo': atributo,
                    'valor_atributo': valor_atributo,
                    'modificador_atributo': mod_atributo
                }
                
                if dc:
                    metadados['dc'] = dc
                
                if not descricao:
                    descricao = f"Teste de {atributo.title()}"
                
                # Fazer rolagem
                rolagem = RolagemDado.rolar_dados(
                    expressao=expressao,
                    usuario=request.user,
                    campanha=personagem.campanha,
                    personagem=personagem,
                    tipo=TipoRolagem.TESTE_ATRIBUTO,
                    modificador=modificador,
                    descricao=descricao,
                    metadados=metadados
                )
                
                # Verificar sucesso se DC foi fornecida
                resultado = {
                    'rolagem': RolagemDadoDetailSerializer(rolagem).data
                }
                
                if dc:
                    sucesso = rolagem.resultado_final >= dc
                    resultado['sucesso'] = sucesso
                    resultado['dc'] = dc
                    resultado['margem'] = rolagem.resultado_final - dc
                
                return Response(resultado, status=status.HTTP_201_CREATED)
                
            except Personagem.DoesNotExist:
                return Response(
                    {'error': 'Personagem não encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {'error': f'Erro ao rolar atributo: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def por_campanha(self, request):
        """
        GET /api/rolagem/por_campanha/?campanha_id={id}
        Listar rolagens de uma campanha específica
        """
        campanha_id = request.query_params.get('campanha_id')
        
        if not campanha_id:
            return Response(
                {'error': 'campanha_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se o usuário tem acesso à campanha
        try:
            from campanhas.models import Campanha
            campanha = Campanha.objects.get(id=campanha_id)
            
            # Verificar acesso
            if not (campanha.mestre == request.user or
                   ParticipacaoCampanha.objects.filter(
                       campanha=campanha, usuario=request.user
                   ).exists()):
                return Response(
                    {'error': 'Você não tem acesso a esta campanha'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
        except Campanha.DoesNotExist:
            return Response(
                {'error': 'Campanha não encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Filtrar rolagens
        rolagens = RolagemDado.objects.filter(
            campanha_id=campanha_id
        )
        
        # Se não for mestre, esconder rolagens secretas
        if campanha.mestre != request.user:
            rolagens = rolagens.filter(secreta=False)
        
        rolagens = rolagens.select_related(
            'usuario', 'personagem'
        ).order_by('-data_rolagem')
        
        serializer = RolagemDadoListSerializer(rolagens, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """
        GET /api/rolagem/estatisticas/
        Estatísticas das rolagens do usuário
        """
        user = request.user
        rolagens = RolagemDado.objects.filter(usuario=user)
        
        if not rolagens.exists():
            return Response({
                'total_rolagens': 0,
                'por_tipo': {},
                'por_resultado': {},
                'media_resultado': 0,
                'rolagem_mais_alta': 0,
                'rolagem_mais_baixa': 0,
                'dados_mais_usados': {}
            })
        
        # Estatísticas básicas
        agregados = rolagens.aggregate(
            total=Count('id'),
            media=Avg('resultado_final'),
            maior=Max('resultado_final'),
            menor=Min('resultado_final')
        )
        
        # Estatísticas por tipo
        por_tipo = {}
        for tipo in TipoRolagem.choices:
            count = rolagens.filter(tipo=tipo[0]).count()
            if count > 0:
                por_tipo[tipo[1]] = count
        
        # Distribuição de resultados (faixas)
        por_resultado = {
            '1-5': rolagens.filter(resultado_final__range=(1, 5)).count(),
            '6-10': rolagens.filter(resultado_final__range=(6, 10)).count(),
            '11-15': rolagens.filter(resultado_final__range=(11, 15)).count(),
            '16-20': rolagens.filter(resultado_final__range=(16, 20)).count(),
            '21+': rolagens.filter(resultado_final__gte=21).count()
        }
        
        # Dados mais usados (análise das expressões)
        dados_mais_usados = {}
        for rolagem in rolagens:
            expressao = rolagem.expressao.lower()
            if 'd20' in expressao:
                dados_mais_usados['d20'] = dados_mais_usados.get('d20', 0) + 1
            if 'd6' in expressao:
                dados_mais_usados['d6'] = dados_mais_usados.get('d6', 0) + 1
            if 'd8' in expressao:
                dados_mais_usados['d8'] = dados_mais_usados.get('d8', 0) + 1
            if 'd10' in expressao:
                dados_mais_usados['d10'] = dados_mais_usados.get('d10', 0) + 1
            if 'd12' in expressao:
                dados_mais_usados['d12'] = dados_mais_usados.get('d12', 0) + 1
        
        estatisticas = {
            'total_rolagens': agregados['total'],
            'por_tipo': por_tipo,
            'por_resultado': por_resultado,
            'media_resultado': round(agregados['media'] or 0, 2),
            'rolagem_mais_alta': agregados['maior'] or 0,
            'rolagem_mais_baixa': agregados['menor'] or 0,
            'dados_mais_usados': dados_mais_usados
        }
        
        serializer = EstatisticasRolagemSerializer(estatisticas)
        return Response(serializer.data)


class TemplateRolagemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de templates de rolagem
    """
    
    serializer_class = TemplateRolagemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Apenas templates do usuário"""
        return TemplateRolagem.objects.filter(
            usuario=self.request.user
        ).order_by('nome')
    
    @action(detail=True, methods=['post'])
    def usar(self, request, pk=None):
        """
        POST /api/templates/{id}/usar/
        Usar template para fazer rolagem
        """
        template = self.get_object()
        
        # Parâmetros opcionais
        campanha_id = request.data.get('campanha_id')
        personagem_id = request.data.get('personagem_id')
        modificador = request.data.get('modificador', ModificadorTipo.NORMAL)
        descricao = request.data.get('descricao', template.descricao)
        
        try:
            # Preparar dados da rolagem
            dados_rolagem = {
                'expressao': template.expressao,
                'tipo': template.tipo,
                'modificador': modificador,
                'descricao': descricao or f'Usando template: {template.nome}',
                'metadados': template.configuracoes
            }
            
            if campanha_id:
                dados_rolagem['campanha_id'] = campanha_id
            
            if personagem_id:
                dados_rolagem['personagem_id'] = personagem_id
            
            # Usar serializer de rolagem para fazer a rolagem
            serializer = RolarDadosSerializer(
                data=dados_rolagem, 
                context={'request': request}
            )
            
            if serializer.is_valid():
                rolagem = serializer.save()
                response_serializer = RolagemDadoDetailSerializer(rolagem)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': f'Erro ao usar template: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
