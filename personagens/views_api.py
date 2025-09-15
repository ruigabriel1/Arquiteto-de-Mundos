"""
Views da API REST para Personagens
"""

from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Personagem, HistoricoPersonagem, BackupPersonagem
from .serializers import (
    PersonagemListSerializer, PersonagemDetailSerializer,
    PersonagemCreateSerializer, PersonagemUpdateSerializer,
    HistoricoPersonagemSerializer, BackupPersonagemSerializer
)
from campanhas.models import ParticipacaoCampanha


class PersonagemPermission(permissions.BasePermission):
    """
    Permissões customizadas para personagens:
    - Usuário pode ver/editar apenas seus próprios personagens
    - Organizador da campanha pode ver/editar personagens de sua campanha
    - Superusuário pode fazer tudo
    - O verdadeiro "Mestre" é o Arquiteto IA, não um usuário humano
    """
    
    def has_permission(self, request, view):
        # Usuário deve estar autenticado
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Superusuário pode tudo
        if request.user.is_superuser:
            return True
        
        # Dono do personagem pode fazer tudo com seu personagem
        if obj.usuario == request.user:
            return True
        
        # Organizador da campanha pode ver/editar personagens de sua campanha
        if obj.campanha and obj.campanha.organizador == request.user:
            return True
        
        # Caso contrário, negar acesso
        return False


class PersonagemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD completo de personagens
    
    - GET /api/personagens/ - Listar personagens do usuário
    - POST /api/personagens/ - Criar novo personagem
    - GET /api/personagens/{id}/ - Detalhes do personagem
    - PUT/PATCH /api/personagens/{id}/ - Atualizar personagem
    - DELETE /api/personagens/{id}/ - Excluir personagem
    """
    
    permission_classes = [IsAuthenticated, PersonagemPermission]
    
    def get_serializer_class(self):
        """Escolher serializer baseado na ação"""
        if self.action == 'list':
            return PersonagemListSerializer
        elif self.action == 'create':
            return PersonagemCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PersonagemUpdateSerializer
        else:
            return PersonagemDetailSerializer
    
    def get_queryset(self):
        """
        Filtrar personagens baseado no usuário:
        - Usuário vê seus próprios personagens
        - Organizador vê personagens das campanhas que organiza
        - O Arquiteto IA (verdadeiro Mestre) tem acesso via sistema interno
        """
        user = self.request.user
        
        if user.is_superuser:
            return Personagem.objects.all()
        
        # Personagens próprios do usuário
        personagens_proprios = Q(usuario=user)
        
        # Personagens de campanhas que o usuário é organizador
        campanhas_como_organizador = Q(campanha__organizador=user)
        
        return Personagem.objects.filter(
            personagens_proprios | campanhas_como_organizador
        ).select_related(
            'usuario', 'sistema_jogo', 'campanha'
        ).distinct()
    
    def perform_create(self, serializer):
        """Criar personagem e registrar no histórico"""
        personagem = serializer.save()
        
        # Registrar criação no histórico
        HistoricoPersonagem.objects.create(
            personagem=personagem,
            usuario_mudanca=self.request.user,
            tipo='outro',
            descricao=f'Personagem {personagem.nome} criado'
        )
        
        # Criar backup inicial
        BackupPersonagem.objects.create(
            personagem=personagem,
            motivo_backup='criacao_inicial',
            dados_personagem=personagem.to_dict()
        )
    
    def perform_update(self, serializer):
        """Atualizar personagem e criar backup se necessário"""
        personagem_antigo = self.get_object()
        
        # Criar backup antes de mudanças significativas
        mudancas_significativas = self._verificar_mudancas_significativas(
            personagem_antigo, serializer.validated_data
        )
        
        if mudancas_significativas:
            BackupPersonagem.objects.create(
                personagem=personagem_antigo,
                motivo_backup='antes_atualizacao_significativa',
                dados_personagem=personagem_antigo.to_dict()
            )
        
        # Salvar as mudanças
        serializer.save()
    
    def perform_destroy(self, instance):
        """Excluir personagem e registrar no histórico"""
        
        # Criar backup final antes da exclusão
        BackupPersonagem.objects.create(
            personagem=instance,
            motivo_backup='antes_exclusao',
            dados_personagem=instance.to_dict()
        )
        
        # Registrar exclusão no histórico
        HistoricoPersonagem.objects.create(
            personagem=instance,
            usuario_mudanca=self.request.user,
            tipo='outro',
            descricao=f'Personagem {instance.nome} excluído'
        )
        
        # Marcar como inativo ao invés de excluir fisicamente
        instance.ativo = False
        instance.save()
    
    def _verificar_mudancas_significativas(self, personagem, dados_novos):
        """Verificar se as mudanças são significativas o suficiente para backup"""
        
        campos_significativos = [
            'nivel', 'forca', 'destreza', 'constituicao', 
            'inteligencia', 'sabedoria', 'carisma'
        ]
        
        for campo in campos_significativos:
            valor_novo = dados_novos.get(campo)
            if valor_novo is not None and getattr(personagem, campo) != valor_novo:
                return True
        
        return False
    
    @action(detail=True, methods=['get'])
    def historico(self, request, pk=None):
        """
        GET /api/personagens/{id}/historico/
        Obter histórico de mudanças do personagem
        """
        personagem = self.get_object()
        historico = HistoricoPersonagem.objects.filter(
            personagem=personagem
        ).order_by('-data_mudanca')
        
        serializer = HistoricoPersonagemSerializer(historico, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def backups(self, request, pk=None):
        """
        GET /api/personagens/{id}/backups/
        Obter backups do personagem
        """
        personagem = self.get_object()
        backups = BackupPersonagem.objects.filter(
            personagem=personagem
        ).order_by('-data_backup')
        
        serializer = BackupPersonagemSerializer(backups, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restaurar_backup(self, request, pk=None):
        """
        POST /api/personagens/{id}/restaurar_backup/
        Restaurar personagem de um backup específico
        """
        personagem = self.get_object()
        backup_id = request.data.get('backup_id')
        
        if not backup_id:
            return Response(
                {'error': 'backup_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            backup = BackupPersonagem.objects.get(
                id=backup_id, 
                personagem=personagem
            )
        except BackupPersonagem.DoesNotExist:
            return Response(
                {'error': 'Backup não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Criar backup antes da restauração
        BackupPersonagem.objects.create(
            personagem=personagem,
            motivo_backup='antes_restauracao',
            dados_personagem=personagem.to_dict()
        )
        
        # Restaurar dados do backup
        personagem.from_dict(backup.dados_personagem)
        personagem.save()
        
        # Registrar restauração no histórico
        HistoricoPersonagem.objects.create(
            personagem=personagem,
            usuario_mudanca=request.user,
            tipo='outro',
            descricao=f'Restaurado do backup de {backup.data_backup.strftime("%d/%m/%Y %H:%M")}'
        )
        
        # Retornar personagem atualizado
        serializer = PersonagemDetailSerializer(personagem)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def curar(self, request, pk=None):
        """
        POST /api/personagens/{id}/curar/
        Curar pontos de vida do personagem
        """
        personagem = self.get_object()
        pontos_cura = request.data.get('pontos_cura', 0)
        
        if not isinstance(pontos_cura, int) or pontos_cura <= 0:
            return Response(
                {'error': 'pontos_cura deve ser um número positivo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calcular nova vida
        vida_atual = personagem.pontos_vida_atual
        vida_maxima = personagem.pontos_vida_maximo
        nova_vida = min(vida_atual + pontos_cura, vida_maxima)
        
        personagem.pontos_vida_atual = nova_vida
        personagem.save()
        
        # Registrar no histórico
        HistoricoPersonagem.objects.create(
            personagem=personagem,
            usuario_mudanca=request.user,
            tipo='cura',
            descricao=f'Curou {pontos_cura} pontos de vida ({vida_atual} → {nova_vida})'
        )
        
        return Response({
            'pontos_vida_anteriores': vida_atual,
            'pontos_curados': pontos_cura,
            'pontos_vida_atuais': nova_vida,
            'pontos_vida_maximos': vida_maxima
        })
    
    @action(detail=True, methods=['post'])
    def causar_dano(self, request, pk=None):
        """
        POST /api/personagens/{id}/causar_dano/
        Causar dano ao personagem
        """
        personagem = self.get_object()
        pontos_dano = request.data.get('pontos_dano', 0)
        
        if not isinstance(pontos_dano, int) or pontos_dano <= 0:
            return Response(
                {'error': 'pontos_dano deve ser um número positivo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calcular nova vida
        vida_atual = personagem.pontos_vida_atual
        nova_vida = max(vida_atual - pontos_dano, 0)
        
        personagem.pontos_vida_atual = nova_vida
        personagem.save()
        
        # Registrar no histórico
        HistoricoPersonagem.objects.create(
            personagem=personagem,
            usuario_mudanca=request.user,
            tipo='dano',
            descricao=f'Recebeu {pontos_dano} pontos de dano ({vida_atual} → {nova_vida})'
        )
        
        # Verificar se o personagem morreu
        morreu = nova_vida == 0
        
        return Response({
            'pontos_vida_anteriores': vida_atual,
            'pontos_dano_recebidos': pontos_dano,
            'pontos_vida_atuais': nova_vida,
            'morreu': morreu
        })
    
    @action(detail=True, methods=['post'])
    def subir_nivel(self, request, pk=None):
        """
        POST /api/personagens/{id}/subir_nivel/
        Subir nível do personagem
        """
        personagem = self.get_object()
        
        if personagem.nivel >= 20:
            return Response(
                {'error': 'Personagem já está no nível máximo (20)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        nivel_anterior = personagem.nivel
        personagem.nivel += 1
        
        # Recalcular pontos de vida máximos
        personagem.calcular_pontos_vida_maximos()
        
        # Curar completamente ao subir de nível (opcional)
        personagem.pontos_vida_atual = personagem.pontos_vida_maximo
        
        personagem.save()
        
        # Registrar no histórico
        HistoricoPersonagem.objects.create(
            personagem=personagem,
            usuario_mudanca=request.user,
            tipo='subida_nivel',
            descricao=f'Subiu do nível {nivel_anterior} para {personagem.nivel}'
        )
        
        # Criar backup após subir de nível
        BackupPersonagem.objects.create(
            personagem=personagem,
            motivo_backup='subiu_nivel',
            dados_personagem=personagem.to_dict()
        )
        
        return Response({
            'nivel_anterior': nivel_anterior,
            'nivel_atual': personagem.nivel,
            'pontos_vida_maximos': personagem.pontos_vida_maximo
        })
    
    @action(detail=False, methods=['get'])
    def por_campanha(self, request):
        """
        GET /api/personagens/por_campanha/?campanha_id={id}
        Listar personagens de uma campanha específica
        """
        campanha_id = request.query_params.get('campanha_id')
        
        if not campanha_id:
            return Response(
                {'error': 'campanha_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se o usuário tem acesso à campanha
        try:
            participante = ParticipacaoCampanha.objects.get(
                campanha_id=campanha_id,
                usuario=request.user
            )
        except ParticipacaoCampanha.DoesNotExist:
            return Response(
                {'error': 'Você não tem acesso a esta campanha'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Buscar personagens da campanha
        personagens = Personagem.objects.filter(
            campanha_id=campanha_id
        ).select_related('usuario', 'sistema_jogo')
        
        serializer = PersonagemListSerializer(personagens, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """
        GET /api/personagens/estatisticas/
        Estatísticas dos personagens do usuário
        """
        user = request.user
        personagens = Personagem.objects.filter(usuario=user)
        
        estatisticas = {
            'total_personagens': personagens.count(),
            'por_nivel': {},
            'por_sistema': {},
            'por_status': {},
            'nivel_medio': 0
        }
        
        if personagens.exists():
            # Estatísticas por nível
            for nivel in range(1, 21):
                count = personagens.filter(nivel=nivel).count()
                if count > 0:
                    estatisticas['por_nivel'][nivel] = count
            
            # Estatísticas por sistema
            for personagem in personagens:
                sistema = personagem.sistema_jogo.nome if personagem.sistema_jogo else 'Não definido'
                estatisticas['por_sistema'][sistema] = (
                    estatisticas['por_sistema'].get(sistema, 0) + 1
                )
            
            # Estatísticas por status
            for personagem in personagens:
                status_p = 'ativo' if personagem.ativo else 'inativo'
                estatisticas['por_status'][status_p] = (
                    estatisticas['por_status'].get(status_p, 0) + 1
                )
            
            # Nível médio
            niveis = [p.nivel for p in personagens]
            estatisticas['nivel_medio'] = sum(niveis) / len(niveis)
        
        return Response(estatisticas)
