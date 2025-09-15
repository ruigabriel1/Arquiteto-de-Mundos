"""
Testes para os modelos e funcionalidades de sessões
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import SessionParticipant, SessaoJogo
from .utils import SessionParticipationManager
from personagens.models import Personagem
from campanhas.models import Campanha
from sistema_unificado.models import SistemaJogo

User = get_user_model()


class SessionParticipantModelTest(TestCase):
    """Testes para o modelo SessionParticipant"""
    
    def setUp(self):
        """Configurar dados de teste"""
        # Criar usuários
        self.usuario1 = User.objects.create_user(
            username='jogador1',
            email='jogador1@unified-chronicles.local',
            password='teste123',
            nome_completo='Jogador Um'
        )
        
        self.usuario2 = User.objects.create_user(
            username='jogador2',
            email='jogador2@unified-chronicles.local',
            password='teste123',
            nome_completo='Jogador Dois'
        )
        
        self.mestre = User.objects.create_user(
            username='mestre',
            email='mestre@unified-chronicles.local',
            password='teste123',
            nome_completo='Mestre da Sessão'
        )
        
        # Criar sessão
        self.sessao = SessaoJogo.objects.create(
            titulo='Sessão de Teste',
            descricao='Uma sessão para testes',
            mestre=self.mestre,
            max_participantes=4
        )
        
        # Criar sistema de jogo para os personagens
        self.sistema = SistemaJogo.objects.create(
            nome='D&D 5e',
            codigo='dnd5e',
            versao='5.1'
        )
        
        # Criar campanha para os personagens
        self.campanha = Campanha.objects.create(
            nome='Campanha de Teste',
            descricao='Uma campanha para testes',
            organizador=self.mestre,
            sistema_jogo=self.sistema
        )
        
        # Criar personagens reais
        self.personagem1 = Personagem.objects.create(
            nome='Personagem 1',
            usuario=self.usuario1,
            campanha=self.campanha,
            sistema_jogo=self.sistema
        )
        
        self.personagem2 = Personagem.objects.create(
            nome='Personagem 2',
            usuario=self.usuario2,
            campanha=self.campanha,
            sistema_jogo=self.sistema
        )
    
    def test_criar_participacao_basica(self):
        """Testar criação básica de participação"""
        participacao = SessionParticipant(
            usuario=self.usuario1,
            personagem=self.personagem1,
            sessao=self.sessao,
            status='aguardando'
        )
        
        # Não deve gerar erro
        self.assertEqual(participacao.usuario, self.usuario1)
        self.assertEqual(participacao.status, 'aguardando')
        self.assertTrue(participacao.pode_jogar)
        self.assertFalse(participacao.esta_ativo)
    
    def test_aprovar_participacao(self):
        """Testar aprovação de participação"""
        participacao = SessionParticipant(
            usuario=self.usuario1,
            personagem=self.personagem1,
            sessao=self.sessao,
            status='aguardando'
        )
        
        # Aprovar
        participacao.aprovar(aprovado_por_user=self.mestre)
        
        self.assertEqual(participacao.status, 'ativo')
        self.assertEqual(participacao.aprovado_por, self.mestre)
        self.assertIsNotNone(participacao.data_aprovacao)
        self.assertTrue(participacao.esta_ativo)
        self.assertTrue(participacao.pode_jogar)
    
    def test_banir_participante(self):
        """Testar banimento de participante"""
        participacao = SessionParticipant(
            usuario=self.usuario1,
            personagem=self.personagem1,
            sessao=self.sessao,
            status='ativo'
        )
        
        # Banir
        participacao.banir(motivo='Comportamento inadequado')
        
        self.assertEqual(participacao.status, 'banido')
        self.assertIsNotNone(participacao.data_saida)
        self.assertIn('Banido: Comportamento inadequado', participacao.observacoes)
        self.assertFalse(participacao.esta_ativo)
        self.assertFalse(participacao.pode_jogar)
    
    def test_sair_da_sessao(self):
        """Testar saída voluntária da sessão"""
        participacao = SessionParticipant(
            usuario=self.usuario1,
            personagem=self.personagem1,
            sessao=self.sessao,
            status='ativo'
        )
        
        # Sair
        participacao.sair_da_sessao()
        
        self.assertEqual(participacao.status, 'inativo')
        self.assertIsNotNone(participacao.data_saida)
        self.assertFalse(participacao.esta_ativo)
        self.assertFalse(participacao.pode_jogar)
    
    def test_string_representation(self):
        """Testar representação string do modelo"""
        participacao = SessionParticipant(
            usuario=self.usuario1,
            personagem=self.personagem1,
            sessao=self.sessao
        )
        
        expected = f"{self.usuario1.username} - {self.personagem1.nome} em {self.sessao.titulo}"
        self.assertEqual(str(participacao), expected)


class SessaoJogoModelTest(TestCase):
    """Testes para o modelo SessaoJogo"""
    
    def setUp(self):
        """Configurar dados de teste"""
        self.mestre = User.objects.create_user(
            username='mestre',
            email='mestre@unified-chronicles.local',
            password='teste123',
            nome_completo='Mestre da Sessão'
        )
        
        self.sessao = SessaoJogo.objects.create(
            titulo='Sessão de Teste',
            descricao='Uma sessão para testes',
            mestre=self.mestre,
            max_participantes=3
        )
    
    def test_criar_sessao_basica(self):
        """Testar criação básica de sessão"""
        self.assertEqual(self.sessao.titulo, 'Sessão de Teste')
        self.assertEqual(self.sessao.mestre, self.mestre)
        self.assertTrue(self.sessao.ativa)
        self.assertEqual(self.sessao.max_participantes, 3)
    
    def test_vagas_disponiveis(self):
        """Testar cálculo de vagas disponíveis"""
        # Inicialmente deve ter 3 vagas
        self.assertEqual(self.sessao.vagas_disponiveis(), 3)
        
        # Criar um participante ativo
        usuario = User.objects.create_user(
            username='jogador',
            email='jogador@unified-chronicles.local',
            password='teste123'
        )
        
        # Criar sistema e campanha para o personagem
        sistema = SistemaJogo.objects.create(
            nome='D&D 5e',
            codigo='dnd5e',
            versao='5.1'
        )
        
        campanha = Campanha.objects.create(
            nome='Campanha Teste',
            descricao='Teste',
            organizador=self.mestre,
            sistema_jogo=sistema
        )
        
        # Criar personagem real
        personagem = Personagem.objects.create(
            nome='Personagem Teste',
            usuario=usuario,
            campanha=campanha,
            sistema_jogo=sistema
        )
        
        participacao = SessionParticipant.objects.create(
            usuario=usuario,
            personagem=personagem,
            sessao=self.sessao,
            status='ativo'
        )
        
        # Deve ter 2 vagas
        self.assertEqual(self.sessao.vagas_disponiveis(), 2)
    
    def test_pode_aceitar_participante(self):
        """Testar se pode aceitar participante"""
        # Inicialmente deve poder aceitar
        self.assertTrue(self.sessao.pode_aceitar_participante())
        
        # Desativar sessão
        self.sessao.ativa = False
        self.sessao.save()
        
        # Não deve poder aceitar
        self.assertFalse(self.sessao.pode_aceitar_participante())
    
    def test_get_participantes_ativos(self):
        """Testar obtenção de participantes ativos"""
        # Inicialmente não deve ter participantes
        self.assertEqual(self.sessao.get_participantes_ativos().count(), 0)
        
        # Criar usuários e participações
        usuario1 = User.objects.create_user(
            username='jogador1',
            email='jogador1@unified-chronicles.local',
            password='teste123'
        )
        
        usuario2 = User.objects.create_user(
            username='jogador2',
            email='jogador2@unified-chronicles.local',
            password='teste123'
        )
        
        # Criar sistema e campanha para os personagens
        sistema = SistemaJogo.objects.create(
            nome='D&D 5e',
            codigo='dnd5e',
            versao='5.1'
        )
        
        campanha = Campanha.objects.create(
            nome='Campanha Teste',
            descricao='Teste',
            organizador=self.mestre,
            sistema_jogo=sistema
        )
        
        # Criar personagens reais
        personagem1 = Personagem.objects.create(
            nome='Personagem 1',
            usuario=usuario1,
            campanha=campanha,
            sistema_jogo=sistema
        )
        
        personagem2 = Personagem.objects.create(
            nome='Personagem 2',
            usuario=usuario2,
            campanha=campanha,
            sistema_jogo=sistema
        )
        
        # Criar participações
        SessionParticipant.objects.create(
            usuario=usuario1,
            personagem=personagem1,
            sessao=self.sessao,
            status='ativo'
        )
        
        SessionParticipant.objects.create(
            usuario=usuario2,
            personagem=personagem2,
            sessao=self.sessao,
            status='aguardando'  # Este não deve contar
        )
        
        # Deve retornar apenas 1 participante ativo
        self.assertEqual(self.sessao.get_participantes_ativos().count(), 1)
    
    def test_string_representation(self):
        """Testar representação string do modelo"""
        self.assertEqual(str(self.sessao), 'Sessão de Teste')


class SessionParticipationManagerTest(TestCase):
    """Testes para o gerenciador de participações"""
    
    def setUp(self):
        """Configurar dados de teste"""
        self.usuario = User.objects.create_user(
            username='jogador',
            email='jogador@unified-chronicles.local',
            password='teste123',
            nome_completo='Jogador'
        )
        
        self.mestre = User.objects.create_user(
            username='mestre',
            email='mestre@unified-chronicles.local',
            password='teste123',
            nome_completo='Mestre'
        )
        
        self.sessao = SessaoJogo.objects.create(
            titulo='Sessão de Teste',
            mestre=self.mestre,
            max_participantes=2
        )
        
        # Criar sistema e campanha
        sistema = SistemaJogo.objects.create(
            nome='D&D 5e',
            codigo='dnd5e',
            versao='5.1'
        )
        
        campanha = Campanha.objects.create(
            nome='Campanha Teste',
            descricao='Teste',
            organizador=self.mestre,
            sistema_jogo=sistema
        )
        
        # Criar personagem real
        self.personagem = Personagem.objects.create(
            nome='Personagem Teste',
            usuario=self.usuario,
            campanha=campanha,
            sistema_jogo=sistema
        )
    
    def test_pode_usuario_participar_sessao_ativa(self):
        """Testar se usuário pode participar de sessão ativa"""
        resultado = SessionParticipationManager.pode_usuario_participar(
            self.usuario, self.sessao
        )
        
        self.assertTrue(resultado['pode_participar'])
        self.assertEqual(resultado['motivo'], 'Pode participar.')
    
    def test_pode_usuario_participar_sessao_inativa(self):
        """Testar se usuário pode participar de sessão inativa"""
        self.sessao.ativa = False
        self.sessao.save()
        
        resultado = SessionParticipationManager.pode_usuario_participar(
            self.usuario, self.sessao
        )
        
        self.assertFalse(resultado['pode_participar'])
        self.assertEqual(resultado['motivo'], 'A sessão não está ativa.')
    
    def test_get_sessoes_do_usuario(self):
        """Testar obtenção de sessões do usuário"""
        # Criar participação
        SessionParticipant.objects.create(
            usuario=self.usuario,
            personagem=self.personagem,
            sessao=self.sessao,
            status='ativo'
        )
        
        sessoes = SessionParticipationManager.get_sessoes_do_usuario(self.usuario)
        
        self.assertEqual(sessoes.count(), 1)
        self.assertEqual(sessoes.first().sessao, self.sessao)
    
    def test_get_sessoes_do_usuario_com_filtro(self):
        """Testar obtenção de sessões do usuário com filtro de status"""
        # Criar participações com diferentes status
        SessionParticipant.objects.create(
            usuario=self.usuario,
            personagem=self.personagem,
            sessao=self.sessao,
            status='ativo'
        )
        
        # Criar segunda sessão
        sessao2 = SessaoJogo.objects.create(
            titulo='Sessão 2',
            mestre=self.mestre
        )
        
        # Criar sistema e campanha para o segundo personagem
        sistema2 = SistemaJogo.objects.create(
            nome='Tormenta 20',
            codigo='t20',
            versao='1.0'
        )
        
        campanha2 = Campanha.objects.create(
            nome='Campanha Teste 2',
            descricao='Teste 2',
            organizador=self.mestre,
            sistema_jogo=sistema2
        )
        
        personagem2 = Personagem.objects.create(
            nome='Personagem 2',
            usuario=self.usuario,
            campanha=campanha2,
            sistema_jogo=sistema2
        )
        
        SessionParticipant.objects.create(
            usuario=self.usuario,
            personagem=personagem2,
            sessao=sessao2,
            status='inativo'
        )
        
        # Filtrar apenas ativas
        sessoes_ativas = SessionParticipationManager.get_sessoes_do_usuario(
            self.usuario, status_filter=['ativo']
        )
        
        self.assertEqual(sessoes_ativas.count(), 1)
        self.assertEqual(sessoes_ativas.first().status, 'ativo')
    
    def test_sair_da_sessao(self):
        """Testar saída de sessão"""
        # Criar participação ativa
        SessionParticipant.objects.create(
            usuario=self.usuario,
            personagem=self.personagem,
            sessao=self.sessao,
            status='ativo'
        )
        
        # Sair da sessão
        resultado = SessionParticipationManager.sair_da_sessao(
            self.usuario, self.sessao, motivo='Teste de saída'
        )
        
        self.assertTrue(resultado)
        
        # Verificar se foi marcado como inativo
        participacao = SessionParticipant.objects.get(
            usuario=self.usuario, sessao=self.sessao
        )
        
        self.assertEqual(participacao.status, 'inativo')
        self.assertIn('Saída: Teste de saída', participacao.observacoes)
    
    def test_sair_da_sessao_nao_participando(self):
        """Testar saída de sessão quando não está participando"""
        resultado = SessionParticipationManager.sair_da_sessao(
            self.usuario, self.sessao
        )
        
        self.assertFalse(resultado)