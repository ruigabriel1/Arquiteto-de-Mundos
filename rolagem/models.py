"""
Modelos para Sistema de Rolagem de Dados - D&D 5e e Tormenta20
"""

import json
import random
import re
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

Usuario = get_user_model()


class TipoRolagem(models.TextChoices):
    """Tipos de rolagem disponíveis"""
    
    TESTE_ATRIBUTO = 'teste_atributo', _('Teste de Atributo')
    TESTE_PERICIA = 'teste_pericia', _('Teste de Perícia') 
    TESTE_RESISTENCIA = 'teste_resistencia', _('Teste de Resistência')
    ATAQUE = 'ataque', _('Rolagem de Ataque')
    DANO = 'dano', _('Rolagem de Dano')
    INICIATIVA = 'iniciativa', _('Iniciativa')
    PONTOS_VIDA = 'pontos_vida', _('Pontos de Vida')
    CUSTOM = 'custom', _('Rolagem Personalizada')
    

class ModificadorTipo(models.TextChoices):
    """Tipos de modificador na rolagem"""
    
    NORMAL = 'normal', _('Normal')
    VANTAGEM = 'vantagem', _('Vantagem')
    DESVANTAGEM = 'desvantagem', _('Desvantagem')


class RolagemDado(models.Model):
    """Modelo para armazenar rolagens de dados"""
    
    # Quem fez a rolagem
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='rolagens',
        verbose_name=_("Usuário")
    )
    
    # Em qual campanha foi feita
    campanha = models.ForeignKey(
        'campanhas.Campanha',
        on_delete=models.CASCADE,
        related_name='rolagens',
        null=True,
        blank=True,
        verbose_name=_("Campanha")
    )
    
    # Qual personagem fez a rolagem (se aplicável)
    personagem = models.ForeignKey(
        'personagens.Personagem',
        on_delete=models.CASCADE,
        related_name='rolagens',
        null=True,
        blank=True,
        verbose_name=_("Personagem")
    )
    
    # Tipo da rolagem
    tipo = models.CharField(
        _("Tipo"),
        max_length=20,
        choices=TipoRolagem.choices,
        default=TipoRolagem.CUSTOM
    )
    
    # Modificador (vantagem/desvantagem)
    modificador = models.CharField(
        _("Modificador"),
        max_length=15,
        choices=ModificadorTipo.choices,
        default=ModificadorTipo.NORMAL
    )
    
    # Expressão da rolagem (ex: "1d20+5", "3d6+2")
    expressao = models.CharField(
        _("Expressão"),
        max_length=200,
        help_text=_("Expressão da rolagem (ex: 1d20+5, 3d6)")
    )
    
    # Resultado individual de cada dado
    resultados_individuais = models.JSONField(
        _("Resultados Individuais"),
        help_text=_("Lista dos resultados de cada dado"),
        default=list
    )
    
    # Resultado final (após aplicar modificadores)
    resultado_final = models.IntegerField(
        _("Resultado Final"),
        help_text=_("Resultado final da rolagem")
    )
    
    # Resultado bruto (soma dos dados sem modificadores)
    resultado_bruto = models.IntegerField(
        _("Resultado Bruto"),
        help_text=_("Soma dos dados sem modificadores")
    )
    
    # Modificador aplicado
    modificador_valor = models.IntegerField(
        _("Modificador Valor"),
        default=0,
        help_text=_("Valor do modificador aplicado (+/-)")
    )
    
    # Descrição da rolagem
    descricao = models.CharField(
        _("Descrição"),
        max_length=200,
        blank=True,
        help_text=_("Descrição do que está sendo testado")
    )
    
    # Metadados adicionais (DC, contexto, etc.)
    metadados = models.JSONField(
        _("Metadados"),
        default=dict,
        blank=True,
        help_text=_("Informações adicionais (DC, contexto, etc.)")
    )
    
    # Timestamps
    data_rolagem = models.DateTimeField(
        _("Data da Rolagem"),
        default=timezone.now
    )
    
    # Visibilidade da rolagem
    publica = models.BooleanField(
        _("Pública"),
        default=True,
        help_text=_("Visível para outros jogadores da campanha")
    )
    
    # Se é rolagem secreta (só o mestre vê)
    secreta = models.BooleanField(
        _("Secreta"),
        default=False,
        help_text=_("Apenas mestre pode ver o resultado")
    )
    
    class Meta:
        verbose_name = _("Rolagem de Dado")
        verbose_name_plural = _("Rolagens de Dados")
        ordering = ['-data_rolagem']
        indexes = [
            models.Index(fields=['usuario', 'campanha']),
            models.Index(fields=['campanha', 'data_rolagem']),
            models.Index(fields=['personagem', 'tipo']),
        ]
    
    def __str__(self):
        personagem_str = f" ({self.personagem.nome})" if self.personagem else ""
        return f"{self.expressao} = {self.resultado_final}{personagem_str}"
    
    @classmethod
    def rolar_dados(cls, expressao, usuario, campanha=None, personagem=None, 
                   tipo=TipoRolagem.CUSTOM, modificador=ModificadorTipo.NORMAL,
                   descricao="", metadados=None):
        """
        Método principal para rolar dados
        """
        parser = ParserDados(expressao)
        resultado = parser.rolar(modificador)
        
        rolagem = cls.objects.create(
            usuario=usuario,
            campanha=campanha,
            personagem=personagem,
            tipo=tipo,
            modificador=modificador,
            expressao=expressao,
            resultados_individuais=resultado['dados_individuais'],
            resultado_final=resultado['resultado_final'],
            resultado_bruto=resultado['resultado_bruto'],
            modificador_valor=resultado['modificador'],
            descricao=descricao,
            metadados=metadados or {}
        )
        
        return rolagem
    
    def to_dict(self):
        """Converte rolagem para dicionário"""
        return {
            'id': self.id,
            'usuario': self.usuario.username,
            'personagem': self.personagem.nome if self.personagem else None,
            'tipo': self.get_tipo_display(),
            'modificador': self.get_modificador_display(),
            'expressao': self.expressao,
            'resultados_individuais': self.resultados_individuais,
            'resultado_final': self.resultado_final,
            'resultado_bruto': self.resultado_bruto,
            'modificador_valor': self.modificador_valor,
            'descricao': self.descricao,
            'metadados': self.metadados,
            'data_rolagem': self.data_rolagem.isoformat(),
            'publica': self.publica,
            'secreta': self.secreta
        }


class ParserDados:
    """Parser inteligente para expressões de dados"""
    
    def __init__(self, expressao):
        self.expressao = expressao.strip().lower().replace(' ', '')
        self.dados = []
        self.modificador = 0
        self.parse()
    
    def parse(self):
        """Parse da expressão de dados"""
        
        # Padrão: 1d20+5, 3d6-2, 2d8, d20, etc.
        padrao = r'(\d*)d(\d+)([+-]\d+)?'
        matches = re.findall(padrao, self.expressao)
        
        if not matches:
            # Tentar número simples
            try:
                self.modificador = int(self.expressao)
                return
            except ValueError:
                raise ValueError(f"Expressão inválida: {self.expressao}")
        
        total_modificador = 0
        
        for match in matches:
            quantidade_str, faces_str, mod_str = match
            
            quantidade = int(quantidade_str) if quantidade_str else 1
            faces = int(faces_str)
            
            if quantidade < 1 or quantidade > 100:
                raise ValueError("Quantidade de dados deve estar entre 1 e 100")
            
            if faces not in [4, 6, 8, 10, 12, 20, 100]:
                raise ValueError(f"Dado d{faces} não é suportado")
            
            self.dados.append({
                'quantidade': quantidade,
                'faces': faces
            })
            
            if mod_str:
                total_modificador += int(mod_str)
        
        self.modificador = total_modificador
    
    def rolar(self, tipo_modificador=ModificadorTipo.NORMAL):
        """Executa a rolagem"""
        
        if not self.dados and self.modificador:
            # Apenas modificador, sem dados
            return {
                'dados_individuais': [],
                'resultado_bruto': 0,
                'modificador': self.modificador,
                'resultado_final': self.modificador
            }
        
        dados_individuais = []
        resultado_bruto = 0
        
        for dado_config in self.dados:
            quantidade = dado_config['quantidade']
            faces = dado_config['faces']
            
            for _ in range(quantidade):
                if tipo_modificador == ModificadorTipo.VANTAGEM:
                    # Rolar duas vezes, pegar o maior
                    roll1 = random.randint(1, faces)
                    roll2 = random.randint(1, faces)
                    resultado = max(roll1, roll2)
                    dados_individuais.append({
                        'faces': faces,
                        'resultado': resultado,
                        'rolagens': [roll1, roll2],
                        'tipo': 'vantagem'
                    })
                elif tipo_modificador == ModificadorTipo.DESVANTAGEM:
                    # Rolar duas vezes, pegar o menor
                    roll1 = random.randint(1, faces)
                    roll2 = random.randint(1, faces)
                    resultado = min(roll1, roll2)
                    dados_individuais.append({
                        'faces': faces,
                        'resultado': resultado,
                        'rolagens': [roll1, roll2],
                        'tipo': 'desvantagem'
                    })
                else:
                    # Rolagem normal
                    resultado = random.randint(1, faces)
                    dados_individuais.append({
                        'faces': faces,
                        'resultado': resultado,
                        'tipo': 'normal'
                    })
                
                resultado_bruto += resultado
        
        resultado_final = resultado_bruto + self.modificador
        
        return {
            'dados_individuais': dados_individuais,
            'resultado_bruto': resultado_bruto,
            'modificador': self.modificador,
            'resultado_final': resultado_final
        }


class TemplateRolagem(models.Model):
    """Templates de rolagem para facilitar rolagens comuns"""
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='templates_rolagem',
        verbose_name=_("Usuário")
    )
    
    nome = models.CharField(
        _("Nome"),
        max_length=100,
        help_text=_("Nome do template (ex: 'Ataque de Espada')")
    )
    
    expressao = models.CharField(
        _("Expressão"),
        max_length=200,
        help_text=_("Expressão da rolagem")
    )
    
    tipo = models.CharField(
        _("Tipo"),
        max_length=20,
        choices=TipoRolagem.choices,
        default=TipoRolagem.CUSTOM
    )
    
    descricao = models.TextField(
        _("Descrição"),
        blank=True,
        help_text=_("Descrição do que esse template faz")
    )
    
    configuracoes = models.JSONField(
        _("Configurações"),
        default=dict,
        help_text=_("Configurações adicionais do template")
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Template de Rolagem")
        verbose_name_plural = _("Templates de Rolagem")
        unique_together = ['usuario', 'nome']
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.expressao})"
