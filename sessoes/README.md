# Sistema de Sessões - Unified Chronicles

## Visão Geral

O sistema de sessões implementa a regra fundamental **"Um Personagem por Usuário por Sessão"**, garantindo que cada usuário possa participar de uma sessão apenas com um único personagem, e que cada personagem seja usado por apenas um usuário em cada sessão.

## Modelos Principais

### SessionParticipant

Modelo central que vincula usuários, personagens e sessões. Garante as regras de negócio através de constraints no banco de dados.

**Campos principais:**
- `usuario`: Usuário que participa da sessão
- `personagem`: Personagem usado na sessão
- `sessao`: Sessão de jogo
- `status`: Status da participação (ativo, inativo, banido, aguardando)
- `data_entrada`: Quando se juntou à sessão
- `aprovado_por`: Quem aprovou a participação
- `observacoes`: Notas sobre a participação

**Constraints de integridade:**
- Um usuário só pode ter um personagem ativo/aguardando por sessão
- Um personagem só pode ser usado por um usuário ativo/aguardando por sessão

### SessaoJogo

Modelo básico para sessões de jogo.

**Campos principais:**
- `titulo`: Nome da sessão
- `mestre`: Usuário que conduz a sessão
- `max_participantes`: Limite de jogadores
- `ativa`: Se está aceitando novos participantes
- `descricao`: Descrição da sessão

## Funcionalidades

### Validações Automáticas

O sistema valida automaticamente:

1. **Propriedade do Personagem**: Usuário só pode usar personagens que criou
2. **Disponibilidade do Personagem**: Personagem deve estar ativo
3. **Unicidade por Sessão**: Um usuário por personagem por sessão
4. **Vagas Disponíveis**: Respeita limite máximo de participantes

### Status de Participação

- **`aguardando`**: Participação pendente de aprovação
- **`ativo`**: Participando ativamente da sessão
- **`inativo`**: Saiu da sessão voluntariamente
- **`banido`**: Removido da sessão pelo mestre

### Gerenciamento via Utils

A classe `SessionParticipationManager` oferece métodos para:

- `participar_de_sessao()`: Solicitar participação
- `aprovar_participacao()`: Aprovar solicitação (apenas mestre)
- `sair_da_sessao()`: Sair voluntariamente
- `get_sessoes_do_usuario()`: Listar sessões do usuário
- `pode_usuario_participar()`: Verificar elegibilidade

## Exemplos de Uso

### Participar de uma Sessão

```python
from sessoes.utils import SessionParticipationManager
from sessoes.models import SessaoJogo
from personagens.models import Personagem

# Buscar sessão e personagem
sessao = SessaoJogo.objects.get(id=1)
personagem = usuario.personagens.filter(ativo=True).first()

# Tentar participar
try:
    participacao = SessionParticipationManager.participar_de_sessao(
        usuario, personagem, sessao
    )
    print(f"Solicitação enviada! Status: {participacao.status}")
except ValidationError as e:
    print(f"Erro: {e}")
```

### Aprovar Participação (Mestre)

```python
# Mestre aprovando participação
participacao_id = 1
mestre = request.user

try:
    participacao = SessionParticipationManager.aprovar_participacao(
        participacao_id, mestre
    )
    print(f"Participação aprovada para {participacao.usuario.username}")
except ValidationError as e:
    print(f"Erro na aprovação: {e}")
```

### Verificar Elegibilidade

```python
resultado = SessionParticipationManager.pode_usuario_participar(usuario, sessao)

if resultado['pode_participar']:
    print("Usuário pode participar!")
else:
    print(f"Não pode participar: {resultado['motivo']}")
```

## Interface de Administração

O Django Admin oferece interface completa para gerenciar:

- **Sessões**: Criar, editar, ver participantes
- **Participações**: Aprovar, banir, ver histórico
- **Ações em lote**: Aprovar múltiplas participações
- **Filtros avançados**: Por status, data, mestre, etc.

### Recursos do Admin

- Status colorido para fácil identificação
- Contadores de participantes e vagas
- Ações personalizadas (aprovar, banir, inativar)
- Inlines para ver participantes na página da sessão

## Testes

Suite completa de testes cobrindo:

- Criação e validação de participações
- Regras de negócio (um personagem por usuário)
- Transições de status
- Métodos utilitários
- Constraints de banco de dados

Execute os testes:
```bash
python manage.py test sessoes
```

## Próximos Passos

Funcionalidades planejadas:

1. **Interface Web**: Views para participar de sessões
2. **Notificações**: Alertas para aprovações/convites
3. **Histórico**: Log detalhado de mudanças
4. **Integração Chat**: Vincular sessões ao sistema de chat
5. **Agendamento**: Sistema de agendamento de sessões
6. **Convites**: Sistema de convites para sessões privadas

## Arquitetura

O sistema foi projetado com:

- **Separação de responsabilidades**: Models, utils e admin separados
- **Validação em múltiplas camadas**: Banco de dados + Python
- **Flexibilidade**: Fácil extensão para novos recursos
- **Testabilidade**: Cobertura completa de testes
- **Internacionalização**: Suporte a PT-BR desde o início

## Considerações Técnicas

- Uses `UniqueConstraint` com condições para performance
- Indexes otimizados para consultas frequentes
- Soft deletes via status (não remove dados históricos)
- JSONField para metadados extensíveis
- Select_related para otimizar queries

## Contribuição

Para contribuir com o sistema de sessões:

1. Executar testes existentes
2. Adicionar testes para novas funcionalidades
3. Seguir padrões de código existentes
4. Atualizar documentação conforme necessário

---

Este sistema estabelece as fundações sólidas para gerenciamento de sessões de RPG no Unified Chronicles, garantindo integridade de dados e uma experiência consistente para os usuários.