"""
Testes para o sistema de participação em campanhas
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import Campanha, CampaignParticipant
from .utils import CampaignParticipationManager
from sistema_unificado.models import SistemaJogo
from personagens.models import Personagem

User = get_user_model()


class CampaignParticipationTestCase(TestCase):
    """Testes para participação em campanhas"""

    def setUp(self):
        """Configurar dados de teste"""
        # Criar usuários
        self.organizador = User.objects.create_user(
            username='organizador',
            email='organizador@test.com',
            password='testpass123',
            nome_completo='Organizador Teste'
        )
        
        self.jogador1 = User.objects.create_user(
            username='jogador1',
            email='jogador1@test.com',
            password='testpass123',
            nome_completo='Jogador Um'
        )
        
        self.jogador2 = User.objects.create_user(
            username='jogador2',
            email='jogador2@test.com',
            password='testpass123',
            nome_completo='Jogador Dois'
        )

        # Criar sistema de jogo
        self.sistema = SistemaJogo.objects.create(
            nome='D&D 5e Test',
            descricao='Sistema de teste',
            ativo=True
        )

        # Criar campanha
        self.campanha = Campanha.objects.create(
            nome='Campanha de Teste',
            descricao='Uma campanha para testes',
            organizador=self.organizador,
            sistema_jogo=self.sistema,
            estado='planejamento',
            max_jogadores=4
        )

        # Criar personagens
        self.personagem1_jogador1 = Personagem.objects.create(
            nome='Guerreiro Teste',
            usuario=self.jogador1,
            campanha=self.campanha,  # Personagem requer campanha
            sistema_jogo=self.sistema,
            nivel=1
        )
        
        self.personagem2_jogador1 = Personagem.objects.create(
            nome='Mago Teste',
            usuario=self.jogador1,
            campanha=self.campanha,
            sistema_jogo=self.sistema,
            nivel=2
        )
        
        self.personagem1_jogador2 = Personagem.objects.create(
            nome='Ladino Teste',
            usuario=self.jogador2,
            campanha=self.campanha,
            sistema_jogo=self.sistema,
            nivel=1
        )

        self.client = Client()

    def test_usuario_pode_participar_campanha_publica(self):
        """Testar se usuário pode participar de campanha pública"""
        resultado = CampaignParticipationManager.pode_usuario_participar(
            self.jogador1, self.campanha
        )
        
        self.assertTrue(resultado['pode_participar'])
        self.assertEqual(resultado['motivo'], 'Pode participar.')

    def test_organizador_nao_pode_participar_da_propria_campanha(self):
        """Testar se organizador não pode participar da própria campanha"""
        resultado = CampaignParticipationManager.pode_usuario_participar(
            self.organizador, self.campanha
        )
        
        self.assertFalse(resultado['pode_participar'])
        self.assertIn('organizador', resultado['motivo'].lower())

    def test_participar_de_campanha_com_personagem(self):
        """Testar participação em campanha com personagem definido"""
        participacao = CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha, self.personagem1_jogador1
        )
        
        self.assertEqual(participacao.usuario, self.jogador1)
        self.assertEqual(participacao.campanha, self.campanha)
        self.assertEqual(participacao.personagem, self.personagem1_jogador1)
        self.assertEqual(participacao.status, 'aguardando')

    def test_participar_de_campanha_sem_personagem(self):
        """Testar participação em campanha sem personagem (status pendente)"""
        participacao = CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha
        )
        
        self.assertEqual(participacao.usuario, self.jogador1)
        self.assertEqual(participacao.campanha, self.campanha)
        self.assertIsNone(participacao.personagem)
        self.assertEqual(participacao.status, 'pendente')

    def test_regra_um_personagem_por_usuario_por_campanha(self):
        """Testar regra de um personagem por usuário por campanha"""
        # Primeiro participa com personagem1
        CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha, self.personagem1_jogador1
        )
        
        # Tentar participar novamente com personagem2 deve falhar
        with self.assertRaises(ValidationError) as context:
            CampaignParticipationManager.participar_de_campanha(
                self.jogador1, self.campanha, self.personagem2_jogador1
            )
        
        self.assertIn('já está participando', str(context.exception))

    def test_mesmo_personagem_nao_pode_ser_usado_em_multiplas_campanhas(self):
        """Testar se o mesmo personagem não pode ser usado em múltiplas campanhas"""
        # Criar segunda campanha
        campanha2 = Campanha.objects.create(
            nome='Segunda Campanha',
            descricao='Outra campanha para teste',
            organizador=self.organizador,
            sistema_jogo=self.sistema,
            estado='planejamento'
        )
        
        # Participar da primeira campanha
        CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha, self.personagem1_jogador1
        )
        
        # Tentar usar o mesmo personagem na segunda campanha deve falhar
        with self.assertRaises(ValidationError) as context:
            CampaignParticipationManager.participar_de_campanha(
                self.jogador1, campanha2, self.personagem1_jogador1
            )
        
        self.assertIn('já está sendo usado', str(context.exception))

    def test_definir_personagem_para_participacao_pendente(self):
        """Testar definição de personagem para participação pendente"""
        # Participar sem personagem
        participacao = CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha
        )
        self.assertEqual(participacao.status, 'pendente')
        
        # Definir personagem
        participacao_atualizada = CampaignParticipationManager.definir_personagem(
            participacao.id, self.personagem1_jogador1
        )
        
        self.assertEqual(participacao_atualizada.personagem, self.personagem1_jogador1)
        self.assertEqual(participacao_atualizada.status, 'aguardando')

    def test_aprovar_participacao(self):
        """Testar aprovação de participação"""
        # Participar da campanha
        participacao = CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha, self.personagem1_jogador1
        )
        self.assertEqual(participacao.status, 'aguardando')
        
        # Aprovar participação
        participacao_aprovada = CampaignParticipationManager.aprovar_participacao(
            participacao.id, self.organizador
        )
        
        self.assertEqual(participacao_aprovada.status, 'ativo')

    def test_apenas_organizador_pode_aprovar(self):
        """Testar se apenas organizador pode aprovar participações"""
        participacao = CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha, self.personagem1_jogador1
        )
        
        # Outro usuário tentar aprovar deve falhar
        with self.assertRaises(ValidationError) as context:
            CampaignParticipationManager.aprovar_participacao(
                participacao.id, self.jogador2
            )
        
        self.assertIn('organizador', str(context.exception).lower())

    def test_sair_da_campanha(self):
        """Testar saída de campanha"""
        # Participar e ser aprovado
        participacao = CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha, self.personagem1_jogador1
        )
        CampaignParticipationManager.aprovar_participacao(
            participacao.id, self.organizador
        )
        
        # Sair da campanha
        sucesso = CampaignParticipationManager.sair_da_campanha(
            self.jogador1, self.campanha, "Motivo pessoal"
        )
        
        self.assertTrue(sucesso)
        participacao.refresh_from_db()
        self.assertEqual(participacao.status, 'inativo')
        self.assertIsNotNone(participacao.data_saida)

    def test_campanha_sem_vagas_nao_aceita_participantes(self):
        """Testar se campanha sem vagas não aceita novos participantes"""
        # Definir campanha com apenas 1 vaga
        self.campanha.max_jogadores = 1
        self.campanha.save()
        
        # Primeiro jogador participa
        CampaignParticipationManager.participar_de_campanha(
            self.jogador1, self.campanha, self.personagem1_jogador1
        )
        
        # Segundo jogador não deve conseguir participar
        resultado = CampaignParticipationManager.pode_usuario_participar(
            self.jogador2, self.campanha
        )
        
        self.assertFalse(resultado['pode_participar'])
        self.assertIn('vagas', resultado['motivo'].lower())

    def test_campanha_inativa_nao_aceita_participantes(self):
        """Testar se campanha inativa não aceita participantes"""
        self.campanha.estado = 'encerrada'
        self.campanha.save()
        
        resultado = CampaignParticipationManager.pode_usuario_participar(
            self.jogador1, self.campanha
        )
        
        self.assertFalse(resultado['pode_participar'])
        self.assertIn('não está aceitando', resultado['motivo'].lower())
