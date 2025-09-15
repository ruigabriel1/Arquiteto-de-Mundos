"""
Testes básicos para participação em campanhas
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import Campanha, CampaignParticipant
from .utils import CampaignParticipationManager
from sistema_unificado.models import SistemaJogo

User = get_user_model()


class BasicCampaignParticipationTest(TestCase):
    """Testes básicos para validar a regra de um personagem por usuário por campanha"""

    def setUp(self):
        """Configurar dados básicos de teste"""
        # Usuários
        self.organizador = User.objects.create_user(
            username='org', email='org@test.com', password='test123'
        )
        self.jogador1 = User.objects.create_user(
            username='j1', email='j1@test.com', password='test123'
        )
        self.jogador2 = User.objects.create_user(
            username='j2', email='j2@test.com', password='test123'
        )

        # Sistema de jogo
        self.sistema = SistemaJogo.objects.create(
            nome='Test System', descricao='Teste', ativo=True
        )

        # Campanha
        self.campanha = Campanha.objects.create(
            nome='Test Campaign',
            descricao='Teste',
            organizador=self.organizador,
            sistema_jogo=self.sistema,
            max_jogadores=4
        )

    def test_campanha_criada_corretamente(self):
        """Testar se campanha foi criada corretamente"""
        self.assertEqual(self.campanha.nome, 'Test Campaign')
        self.assertEqual(self.campanha.organizador, self.organizador)

    def test_pode_participar_de_campanha(self):
        """Testar se usuário pode participar de campanha"""
        resultado = CampaignParticipationManager.pode_usuario_participar(
            self.jogador1, self.campanha
        )
        self.assertTrue(resultado['pode_participar'])

    def test_organizador_nao_pode_participar(self):
        """Testar se organizador não pode participar da própria campanha"""
        resultado = CampaignParticipationManager.pode_usuario_participar(
            self.organizador, self.campanha
        )
        self.assertFalse(resultado['pode_participar'])

    def test_participar_sem_personagem(self):
        """Testar participação sem personagem inicial"""
        participacao = CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha
        )
        
        self.assertEqual(participacao.usuario, self.jogador1)
        self.assertEqual(participacao.campanha, self.campanha)
        self.assertEqual(participacao.status, 'pendente')
        self.assertIsNone(participacao.personagem)

    def test_usuario_nao_pode_participar_duas_vezes(self):
        """Testar se usuário não pode participar duas vezes da mesma campanha"""
        # Primeira participação
        CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha
        )
        
        # Segunda tentativa deve falhar
        with self.assertRaises(ValidationError):
            CampaignParticipationManager.participar_de_campanha(
                self.jogador1, self.campanha
            )

    def test_aprovar_participacao(self):
        """Testar aprovação de participação"""
        # Criar participação
        participacao = CampaignParticipant.objects.create(
            usuario=self.jogador1,
            campanha=self.campanha,
            status='aguardando'
        )
        
        # Aprovar
        participacao_aprovada = CampaignParticipationManager.aprovar_participacao(
            participacao.id, self.organizador
        )
        
        self.assertEqual(participacao_aprovada.status, 'ativo')

    def test_apenas_organizador_pode_aprovar(self):
        """Testar se apenas organizador pode aprovar"""
        participacao = CampaignParticipant.objects.create(
            usuario=self.jogador1,
            campanha=self.campanha,
            status='aguardando'
        )
        
        # Outro usuário tentar aprovar deve falhar
        with self.assertRaises(ValidationError):
            CampaignParticipationManager.aprovar_participacao(
                participacao.id, self.jogador2
            )

    def test_sair_da_campanha(self):
        """Testar saída de campanha"""
        # Criar participação ativa
        CampaignParticipant.objects.create(
            usuario=self.jogador1,
            campanha=self.campanha,
            status='ativo'
        )
        
        # Sair da campanha
        sucesso = CampaignParticipationManager.sair_da_campanha(
            self.jogador1, self.campanha
        )
        
        self.assertTrue(sucesso)

    def test_campanha_sem_vagas(self):
        """Testar campanha sem vagas"""
        # Definir apenas 1 vaga
        self.campanha.max_jogadores = 1
        self.campanha.save()
        
        # Primeira participação
        CampaignParticipant.objects.create(
            usuario=self.jogador1,
            campanha=self.campanha,
            status='ativo'
        )
        
        # Segunda tentativa deve indicar sem vagas
        resultado = CampaignParticipationManager.pode_usuario_participar(
            self.jogador2, self.campanha
        )
        
        self.assertFalse(resultado['pode_participar'])
        self.assertIn('vagas', resultado['motivo'].lower())

    def test_get_campanhas_do_usuario(self):
        """Testar busca de campanhas do usuário"""
        # Criar participação
        CampaignParticipant.objects.create(
            usuario=self.jogador1,
            campanha=self.campanha,
            status='ativo'
        )
        
        participacoes = CampaignParticipationManager.get_campanhas_do_usuario(
            self.jogador1
        )
        
        self.assertEqual(participacoes.count(), 1)
        self.assertEqual(participacoes.first().campanha, self.campanha)

    def test_get_participantes_da_campanha(self):
        """Testar busca de participantes da campanha"""
        # Criar participação
        CampaignParticipant.objects.create(
            usuario=self.jogador1,
            campanha=self.campanha,
            status='ativo'
        )
        
        participantes = CampaignParticipationManager.get_participantes_da_campanha(
            self.campanha
        )
        
        self.assertEqual(participantes.count(), 1)
        self.assertEqual(participantes.first().usuario, self.jogador1)