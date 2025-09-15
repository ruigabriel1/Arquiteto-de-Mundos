// Tipos para o sistema de Chat/Mensagens

export interface Usuario {
  id: number;
  username: string;
  nome_completo: string;
  first_name?: string;
  last_name?: string;
  email?: string;
}

export interface Personagem {
  id: number;
  nome: string;
  classe?: string;
  nivel?: number;
  usuario: number;
}

export interface Campanha {
  id: number;
  nome: string;
  descricao?: string;
  sistema: 'D&D5E' | 'T20';
  mestre: Usuario;
  participantes: Usuario[];
  data_criacao: string;
  ativa: boolean;
}

export interface SalaChat {
  id: number;
  nome: string;
  descricao?: string;
  campanha: Campanha;
  campanha_nome?: string;
  comandos_habilitados: boolean;
  rolagens_publicas: boolean;
  historico_visivel: boolean;
  max_mensagens_historico: number;
  participantes_online: number;
  ultima_mensagem_conteudo?: string;
  ultima_mensagem_timestamp?: string;
  mensagens_nao_lidas: number;
  data_criacao: string;
  data_atualizacao: string;
}

export interface ParticipacaoChat {
  id: number;
  usuario: Usuario;
  usuario_nome: string;
  username: string;
  online: boolean;
  mutado: boolean;
  is_moderador: boolean;
  mensagens_nao_lidas: number;
  notificacoes_habilitadas: boolean;
  primeira_conexao: string;
  ultima_conexao: string;
  ultima_mensagem_vista?: string;
}

export enum TipoMensagem {
  NORMAL = 'NORMAL',
  WHISPER = 'WHISPER',
  COMANDO_ACAO = 'COMANDO_ACAO',
  COMANDO_ROLAGEM = 'COMANDO_ROLAGEM',
  SISTEMA = 'SISTEMA'
}

export interface RolagemDados {
  id: number;
  expressao: string;
  resultado: number;
  resultados_individuais: number[];
}

export interface Mensagem {
  id: number;
  tipo: TipoMensagem;
  tipo_display: string;
  conteudo: string;
  usuario?: Usuario;
  usuario_nome?: string;
  destinatario?: Usuario;
  personagem?: Personagem;
  personagem_nome?: string;
  rolagem?: RolagemDados;
  metadados?: Record<string, any>;
  editada: boolean;
  timestamp: string;
  timestamp_edicao?: string;
}

// Tipos para WebSocket
export interface WebSocketMessage {
  type: 'chat_message' | 'user_status' | 'user_typing' | 'system_notification' | 'error' | 'pong' | 'whisper_message' | 'messages_marked_read';
  mensagem?: Mensagem;
  message?: string;
  action?: 'entrou' | 'saiu';
  usuario_id?: number;
  usuario_nome?: string;
  is_typing?: boolean;
  level?: 'info' | 'warning' | 'error' | 'success';
  timestamp?: string;
  destinatario_id?: number;
}

export interface WebSocketSendMessage {
  action: 'send_message' | 'execute_command' | 'typing' | 'mark_read' | 'ping';
  message?: string;
  command?: string;
  personagem_id?: number;
  destinatario_username?: string;
  is_typing?: boolean;
}

// Tipos para notificações
export interface NotificacaoWebSocket {
  type: 'notification' | 'campaign_invite' | 'character_update' | 'error';
  message: string;
  category?: 'general' | 'campaign' | 'character' | 'system';
  level?: 'info' | 'warning' | 'error' | 'success';
  data?: Record<string, any>;
  timestamp?: string;
  
  // Para convites de campanha
  campaign_id?: number;
  campaign_name?: string;
  inviter_name?: string;
  
  // Para atualizações de personagem
  character_id?: number;
  character_name?: string;
  update_type?: string;
}

// Estados de conexão WebSocket
export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

// Configurações do Chat
export interface ChatConfig {
  enableSound: boolean;
  enableNotifications: boolean;
  theme: 'light' | 'dark';
  fontSize: 'small' | 'medium' | 'large';
  showTimestamps: boolean;
  compactMode: boolean;
}

// Estado do usuário digitando
export interface TypingUser {
  usuario_id: number;
  usuario_nome: string;
  timestamp: number;
}

// Filtros para mensagens
export interface MessageFilters {
  tipo?: TipoMensagem[];
  usuario?: number[];
  personagem?: number[];
  dataInicio?: string;
  dataFim?: string;
  busca?: string;
}

// Resposta da API de estatísticas
export interface EstatisticasChat {
  total_mensagens: number;
  mensagens_por_tipo: Record<string, number>;
  participantes_online: number;
  total_participantes: number;
  mensagens_hoje: number;
  comandos_mais_usados: Record<string, number>;
  usuarios_mais_ativos: string[];
}

// Paginação
export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

// Tipos para formulários
export interface EnviarMensagemForm {
  conteudo: string;
  personagem_id?: number;
  destinatario_username?: string;
}

export interface ComandoChatForm {
  comando: string;
  personagem_id?: number;
}

// Tipos de erro
export interface ChatError {
  message: string;
  code?: string | number;
  timestamp: string;
}