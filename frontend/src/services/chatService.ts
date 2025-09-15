// Serviço para API de Chat/Mensagens

import { api } from './api';
import {
  SalaChat,
  ParticipacaoChat,
  Mensagem,
  PaginatedResponse,
  EnviarMensagemForm,
  ComandoChatForm,
  EstatisticasChat,
} from '../types';

// Endpoints da API
const ENDPOINTS = {
  SALAS: '/api/mensagens/api/salas',
  MENSAGENS: '/api/mensagens/api/mensagens',
  PARTICIPACOES: '/api/mensagens/api/participacoes',
};

export class ChatService {
  // === SALAS DE CHAT ===
  
  /**
   * Listar salas de chat do usuário
   */
  static async listarSalas(): Promise<SalaChat[]> {
    return api.get<SalaChat[]>(ENDPOINTS.SALAS);
  }

  /**
   * Obter detalhes de uma sala específica
   */
  static async obterSala(salaId: number): Promise<SalaChat> {
    return api.get<SalaChat>(`${ENDPOINTS.SALAS}/${salaId}/`);
  }

  /**
   * Entrar em uma sala de chat
   */
  static async entrarNaSala(salaId: number): Promise<{ sucesso: string; participacao: ParticipacaoChat }> {
    return api.post(`${ENDPOINTS.SALAS}/${salaId}/entrar/`);
  }

  /**
   * Sair de uma sala de chat
   */
  static async sairDaSala(salaId: number): Promise<{ sucesso: string }> {
    return api.post(`${ENDPOINTS.SALAS}/${salaId}/sair/`);
  }

  /**
   * Listar participantes de uma sala
   */
  static async listarParticipantes(salaId: number): Promise<ParticipacaoChat[]> {
    return api.get<ParticipacaoChat[]>(`${ENDPOINTS.SALAS}/${salaId}/participantes/`);
  }

  /**
   * Obter estatísticas de uma sala
   */
  static async obterEstatisticas(salaId: number): Promise<EstatisticasChat> {
    return api.get<EstatisticasChat>(`${ENDPOINTS.SALAS}/${salaId}/estatisticas/`);
  }

  // === MENSAGENS ===

  /**
   * Listar histórico de mensagens
   */
  static async listarMensagens(
    params: {
      sala_id?: number;
      page?: number;
      page_size?: number;
    } = {}
  ): Promise<PaginatedResponse<Mensagem>> {
    const searchParams = new URLSearchParams();
    
    if (params.sala_id) searchParams.append('sala_id', params.sala_id.toString());
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.page_size) searchParams.append('page_size', params.page_size.toString());
    
    const queryString = searchParams.toString();
    const url = queryString ? `${ENDPOINTS.MENSAGENS}/?${queryString}` : ENDPOINTS.MENSAGENS;
    
    return api.get<PaginatedResponse<Mensagem>>(url);
  }

  /**
   * Obter detalhes de uma mensagem específica
   */
  static async obterMensagem(mensagemId: number): Promise<Mensagem> {
    return api.get<Mensagem>(`${ENDPOINTS.MENSAGENS}/${mensagemId}/`);
  }

  /**
   * Enviar mensagem via API REST (alternativa ao WebSocket)
   */
  static async enviarMensagem(
    salaId: number,
    dados: EnviarMensagemForm
  ): Promise<Mensagem> {
    return api.post<Mensagem>(`${ENDPOINTS.MENSAGENS}/enviar/`, {
      sala_id: salaId,
      ...dados,
    });
  }

  /**
   * Executar comando via API REST (alternativa ao WebSocket)
   */
  static async executarComando(
    salaId: number,
    dados: ComandoChatForm
  ): Promise<Mensagem> {
    return api.post<Mensagem>(`${ENDPOINTS.MENSAGENS}/comando/`, {
      sala_id: salaId,
      ...dados,
    });
  }

  /**
   * Marcar mensagens como lidas
   */
  static async marcarComoLidas(salaId: number): Promise<{ sucesso: string }> {
    return api.post(`${ENDPOINTS.MENSAGENS}/marcar_lidas/`, {
      sala_id: salaId,
    });
  }

  // === PARTICIPAÇÕES ===

  /**
   * Listar participações do usuário
   */
  static async listarParticipacoes(): Promise<ParticipacaoChat[]> {
    return api.get<ParticipacaoChat[]>(ENDPOINTS.PARTICIPACOES);
  }

  /**
   * Obter participação específica
   */
  static async obterParticipacao(participacaoId: number): Promise<ParticipacaoChat> {
    return api.get<ParticipacaoChat>(`${ENDPOINTS.PARTICIPACOES}/${participacaoId}/`);
  }

  /**
   * Atualizar configurações de participação
   */
  static async atualizarConfiguracoes(
    participacaoId: number,
    configuracoes: {
      mutado?: boolean;
      notificacoes_habilitadas?: boolean;
    }
  ): Promise<ParticipacaoChat> {
    return api.patch<ParticipacaoChat>(
      `${ENDPOINTS.PARTICIPACOES}/${participacaoId}/configuracoes/`,
      configuracoes
    );
  }

  // === FUNÇÕES AUXILIARES ===

  /**
   * Buscar mensagens por texto
   */
  static async buscarMensagens(
    salaId: number,
    termo: string,
    params: {
      page?: number;
      page_size?: number;
    } = {}
  ): Promise<PaginatedResponse<Mensagem>> {
    const searchParams = new URLSearchParams();
    searchParams.append('sala_id', salaId.toString());
    searchParams.append('search', termo);
    
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.page_size) searchParams.append('page_size', params.page_size.toString());
    
    return api.get<PaginatedResponse<Mensagem>>(`${ENDPOINTS.MENSAGENS}/?${searchParams.toString()}`);
  }

  /**
   * Obter mensagens mais recentes de uma sala
   */
  static async obterMensagensRecentes(
    salaId: number,
    limite: number = 50
  ): Promise<Mensagem[]> {
    const response = await this.listarMensagens({
      sala_id: salaId,
      page_size: limite,
    });
    return response.results.reverse(); // API retorna mais recentes primeiro, mas queremos ordem cronológica
  }

  /**
   * Verificar se há novas mensagens
   */
  static async verificarNovasMensagens(
    salaId: number,
    ultimaMensagemId?: number
  ): Promise<{ temNovas: boolean; mensagens: Mensagem[] }> {
    const mensagens = await this.obterMensagensRecentes(salaId, 10);
    
    if (!ultimaMensagemId) {
      return { temNovas: mensagens.length > 0, mensagens };
    }
    
    const novasMensagens = mensagens.filter(msg => msg.id > ultimaMensagemId);
    return { temNovas: novasMensagens.length > 0, mensagens: novasMensagens };
  }

  /**
   * Obter contagem de mensagens não lidas por sala
   */
  static async obterMensagensNaoLidas(): Promise<Record<number, number>> {
    const salas = await this.listarSalas();
    const contadores: Record<number, number> = {};
    
    salas.forEach(sala => {
      contadores[sala.id] = sala.mensagens_nao_lidas || 0;
    });
    
    return contadores;
  }

  /**
   * Validar comando antes de enviar
   */
  static validarComando(comando: string): { valido: boolean; erro?: string } {
    if (!comando.startsWith('/')) {
      return { valido: false, erro: 'Comando deve começar com /' };
    }

    if (comando.trim().length < 2) {
      return { valido: false, erro: 'Comando muito curto' };
    }

    if (comando.length > 200) {
      return { valido: false, erro: 'Comando muito longo' };
    }

    return { valido: true };
  }

  /**
   * Formatar timestamp para exibição
   */
  static formatarTimestamp(timestamp: string): string {
    const data = new Date(timestamp);
    const agora = new Date();
    const diferenca = agora.getTime() - data.getTime();
    
    // Menos de 1 minuto
    if (diferenca < 60000) {
      return 'Agora';
    }
    
    // Menos de 1 hora
    if (diferenca < 3600000) {
      const minutos = Math.floor(diferenca / 60000);
      return `${minutos}m`;
    }
    
    // Mesmo dia
    if (agora.toDateString() === data.toDateString()) {
      return data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }
    
    // Dias diferentes
    return data.toLocaleDateString('pt-BR', { 
      day: '2-digit', 
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  /**
   * Extrair menções de uma mensagem (@usuario)
   */
  static extrairMencoes(conteudo: string): string[] {
    const regex = /@(\w+)/g;
    const mencoes: string[] = [];
    let match;
    
    while ((match = regex.exec(conteudo)) !== null) {
      mencoes.push(match[1]);
    }
    
    return mencoes;
  }

  /**
   * Verificar se mensagem é comando
   */
  static isComando(conteudo: string): boolean {
    return conteudo.trim().startsWith('/');
  }

  /**
   * Obter tipo de comando
   */
  static obterTipoComando(conteudo: string): string | null {
    if (!this.isComando(conteudo)) {
      return null;
    }
    
    const match = conteudo.match(/^\/(\w+)/);
    return match ? match[1].toLowerCase() : null;
  }
}