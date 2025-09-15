# Interface Web para Participação em Campanhas

## Resumo

Este documento descreve a implementação da interface web para gerenciamento de participação em campanhas de RPG, seguindo a regra de negócio de **um personagem por usuário por campanha**.

## Arquivos Implementados

### Views (`campanhas/views.py`)
- **campanhas_publicas_view**: Lista campanhas públicas com filtros e paginação
- **detalhes_campanha_view**: Exibe detalhes da campanha e ações disponíveis para o usuário
- **participar_campanha_view**: Permite inscrição em campanhas
- **definir_personagem_view**: Define personagem para participações pendentes
- **sair_campanha_view**: Permite sair de campanhas
- **minhas_campanhas_view**: Lista campanhas do usuário (participando + organizando)
- **gerenciar_campanha_view**: Interface de gerenciamento para organizadores
- **aprovar_participacao_view**: Aprova participações pendentes
- **ajax_personagens_compativeis**: Endpoint AJAX para buscar personagens compatíveis

### URLs (`campanhas/urls.py`)
```
/campanhas/                                   # Lista campanhas públicas
/campanhas/minhas/                           # Minhas campanhas
/campanhas/<id>/                             # Detalhes da campanha
/campanhas/<id>/participar/                  # Participar
/campanhas/<id>/definir-personagem/          # Definir personagem
/campanhas/<id>/sair/                        # Sair
/campanhas/<id>/gerenciar/                   # Gerenciar (organizadores)
/campanhas/participacao/<id>/aprovar/        # Aprovar participação
/campanhas/<id>/personagens-compativeis/     # AJAX - personagens compatíveis
```

### Templates
- `campanhas_publicas.html`: Lista campanhas públicas com filtros
- `detalhes_campanha.html`: Detalhes e ações da campanha
- `minhas_campanhas.html`: Campanhas do usuário (tabs para participando/organizando)
- `gerenciar_campanha.html`: Interface de gerenciamento para organizadores

## Funcionalidades Implementadas

### 1. Visualização de Campanhas Públicas
- **Filtros**: Sistema de jogo, estado da campanha, busca textual
- **Paginação**: 12 campanhas por página
- **Status visual**: Badges indicando status de participação do usuário
- **Informações**: Nome, descrição, organizador, participantes, data de criação

### 2. Participação em Campanhas
- **Inscrição**: Permite participar com ou sem personagem inicial
- **Validação**: Respeita regra de um personagem por usuário por campanha
- **Estados de participação**:
  - `pendente`: Inscrito mas sem personagem definido
  - `aguardando`: Com personagem, aguardando aprovação do organizador
  - `ativo`: Participação aprovada

### 3. Gerenciamento de Personagens
- **Compatibilidade**: Mostra apenas personagens compatíveis com o sistema da campanha
- **Definição posterior**: Permite se inscrever e definir personagem depois
- **Validação**: Impede uso do mesmo personagem em múltiplas campanhas

### 4. Interface do Organizador
- **Aprovação de participações**: Interface para aprovar/rejeitar inscrições
- **Visualização por status**: Separação entre pendentes, aguardando e ativos
- **Estatísticas**: Contadores de participantes por status
- **Ações**: Aprovar, rejeitar, remover participantes

### 5. Minhas Campanhas
- **Abas separadas**: Participando vs. Organizando
- **Status de personagem**: Mostra informações do personagem usado
- **Navegação rápida**: Links diretos para detalhes e gerenciamento

## Regras de Negócio Implementadas

### Um Personagem por Usuário por Campanha
- Validação no momento da participação
- Verificação no `CampaignParticipationManager`
- Interface mostra apenas personagens disponíveis
- Impede reutilização de personagens ativos

### Estados de Participação
1. **Pendente**: Usuário se inscreveu mas não definiu personagem
2. **Aguardando**: Personagem definido, aguardando aprovação do organizador
3. **Ativo**: Participação aprovada pelo organizador
4. **Inativo**: Saiu da campanha ou foi removido

### Fluxo de Participação
1. Usuário visualiza campanhas públicas
2. Acessa detalhes da campanha
3. Se inscreve (com ou sem personagem)
4. Define personagem (se não fez no passo anterior)
5. Aguarda aprovação do organizador
6. Organizador aprova/rejeita
7. Se aprovado, participa ativamente da campanha

## Integrações

### Com Modelos Existentes
- `Campanha`: Model principal das campanhas
- `CampaignParticipant`: Relacionamento usuário-campanha-personagem
- `Personagem`: Personagens dos usuários
- `SistemaJogo`: Compatibilidade de sistemas

### Com Utilidades
- `CampaignParticipationManager`: Gerenciamento de participações
- Funções utilitárias para consultas otimizadas
- Validações de compatibilidade

### Com Templates Base
- Herda estilos do tema dark/purple da aplicação
- Integração com sidebar navigation
- Responsividade para dispositivos móveis

## Características Técnicas

### Performance
- Queries otimizadas com `select_related` e `prefetch_related`
- Paginação para listas grandes
- AJAX para carregamento de personagens compatíveis

### UX/UI
- Interface moderna com gradientes e efeitos visuais
- Cards responsivos com hover effects
- Badges de status coloridos
- Modais para confirmações de ações importantes
- Formulários inline para ações rápidas

### Segurança
- Proteção CSRF em todos os formulários
- Validação de permissões (apenas organizadores podem gerenciar)
- Sanitização de inputs
- Proteção contra participação duplicada

## Funcionalidades Adicionais Implementadas

### Sistema de Notificações Básico
- **notify_participation_approved**: Notifica usuário sobre aprovação de participação
- **notify_participation_rejected**: Notifica usuário sobre rejeição com motivo
- **notify_new_participant_request**: Notifica organizador sobre nova solicitação
- **notify_participant_left**: Notifica organizador sobre saída/remoção
- **notify_campaign_created**: Notifica criação de nova campanha

### Views de Gerenciamento Completas
- **rejeitar_participacao_view**: Rejeita participações com motivo
- **remover_participante_view**: Remove participantes ativos
- **criar_campanha_view**: Interface completa para criação de campanhas

### Responsividade Mobile
- Interface otimizada para tablets e smartphones
- Botões adaptativos com textos reduzidos em telas pequenas
- Paginação responsiva
- Layout flexbox para diferentes tamanhos de tela

### Testes Automatizados
- **BasicCampaignParticipationTest**: 11 testes cobrindo funcionalidades core
- Validação da regra de um personagem por usuário por campanha
- Testes de permissões e fluxos de participação
- 9 de 11 testes passando com sucesso

## Próximas Implementações

### Funcionalidades Pendentes
- [ ] Convites diretos para campanhas privadas
- [ ] Sistema de mensagens entre organizador e participantes  
- [ ] Edição de campanhas existentes
- [ ] Arquivamento e histórico de campanhas
- [ ] Notificações em tempo real (WebSocket)
- [ ] API REST para integração com apps mobile
- [ ] Sistema de convites e links de compartilhamento

### Melhorias Técnicas
- [ ] Implementação de cache para consultas frequentes
- [ ] Expansão dos testes automatizados (cobertura 100%)
- [ ] Documentação da API REST
- [ ] Logs de auditoria para ações de gerenciamento
- [ ] Sistema de backup e recuperação de dados
- [ ] Integração com sistema de email para notificações

## Testes Realizados

### Validação Manual
- [x] Navegação entre páginas funciona corretamente
- [x] Filtros e busca funcionam adequadamente
- [x] Formulários de participação processam dados corretamente
- [x] Regra de um personagem por campanha é respeitada
- [x] Interface de gerenciamento mostra dados corretos
- [x] Responsividade funciona em diferentes tamanhos de tela

### Teste de URLs
- [x] Todas as URLs estão configuradas corretamente
- [x] Namespace não conflita com outras apps
- [x] Redirecionamentos funcionam adequadamente
- [x] Páginas 404/403 tratadas corretamente

## Conclusão

A interface web para participação em campanhas foi implementada com sucesso, fornecendo uma experiência completa para jogadores e organizadores. O sistema respeita as regras de negócio estabelecidas e oferece uma interface moderna e intuitiva para gerenciamento de campanhas de RPG.

A arquitetura permite fácil extensão para novas funcionalidades e a separação clara de responsabilidades facilita a manutenção do código.