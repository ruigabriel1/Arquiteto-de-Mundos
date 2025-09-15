// Componente principal da sala de chat

import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { ChatService } from '../services/chatService';
import { SalaChat, Mensagem, ParticipacaoChat, ConnectionStatus } from '../types';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import UserList from './UserList';
import ConnectionIndicator from './ConnectionIndicator';
import TypingIndicator from './TypingIndicator';

interface ChatRoomProps {
  salaId: number;
  className?: string;
}

const ChatRoom: React.FC<ChatRoomProps> = ({ salaId, className = '' }) => {
  // Estado local
  const [sala, setSala] = useState<SalaChat | null>(null);
  const [participantes, setParticipantes] = useState<ParticipacaoChat[]>([]);
  const [mensagensHistorico, setMensagensHistorico] = useState<Mensagem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUserList, setShowUserList] = useState(false);

  // Hook WebSocket
  const {
    status,
    isConnected,
    connect,
    disconnect,
    enviarMensagem,
    executarComando,
    marcarDigitando,
    marcarComoLidas,
    mensagens: mensagensWebSocket,
    usuariosDigitando,
    erros,
    onMessage,
    onConnect,
    onDisconnect,
  } = useWebSocket({
    salaId,
    autoConnect: true,
    reconnectAttempts: 5,
  });

  // Refs
  const messageListRef = useRef<HTMLDivElement>(null);
  const isLoadingHistoryRef = useRef(false);

  // Combinar mensagens do histórico com mensagens do WebSocket
  const todasMensagens = [...mensagensHistorico, ...mensagensWebSocket];

  // Carregar dados iniciais
  useEffect(() => {
    const carregarDados = async () => {
      try {
        setLoading(true);
        setError(null);

        // Carregar informações da sala
        const salaData = await ChatService.obterSala(salaId);
        setSala(salaData);

        // Carregar participantes
        const participantesData = await ChatService.listarParticipantes(salaId);
        setParticipantes(participantesData);

        // Carregar histórico de mensagens
        const historicoData = await ChatService.obterMensagensRecentes(salaId, 50);
        setMensagensHistorico(historicoData);

        // Entrar na sala via API
        await ChatService.entrarNaSala(salaId);

      } catch (err: any) {
        console.error('Erro ao carregar dados da sala:', err);
        setError(err.message || 'Erro ao carregar sala de chat');
      } finally {
        setLoading(false);
      }
    };

    if (salaId) {
      carregarDados();
    }

    // Cleanup ao sair
    return () => {
      if (salaId && !isLoadingHistoryRef.current) {
        ChatService.sairDaSala(salaId).catch(console.error);
      }
    };
  }, [salaId]);

  // Marcar mensagens como lidas quando conectar
  useEffect(() => {
    if (isConnected) {
      marcarComoLidas();
      // Também marcar via API
      ChatService.marcarComoLidas(salaId).catch(console.error);
    }
  }, [isConnected, salaId, marcarComoLidas]);

  // Escutar mensagens do WebSocket
  useEffect(() => {
    const unsubscribe = onMessage((message) => {
      switch (message.type) {
        case 'user_status':
          // Atualizar lista de participantes quando alguém entra/sai
          ChatService.listarParticipantes(salaId)
            .then(setParticipantes)
            .catch(console.error);
          break;

        case 'system_notification':
          // Mostrar notificação do sistema
          console.log('Notificação:', message.message);
          break;

        default:
          break;
      }
    });

    return unsubscribe;
  }, [onMessage, salaId]);

  // Scroll automático para última mensagem
  useEffect(() => {
    if (messageListRef.current && todasMensagens.length > 0) {
      const scrollElement = messageListRef.current;
      const isNearBottom = 
        scrollElement.scrollHeight - scrollElement.scrollTop - scrollElement.clientHeight < 100;

      if (isNearBottom) {
        setTimeout(() => {
          scrollElement.scrollTo({
            top: scrollElement.scrollHeight,
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  }, [todasMensagens]);

  // Handlers
  const handleSendMessage = (content: string, personagemId?: number, destinatarioUsername?: string) => {
    const sucesso = enviarMensagem(content, personagemId, destinatarioUsername);
    
    if (!sucesso) {
      // Fallback para API REST se WebSocket não estiver disponível
      ChatService.enviarMensagem(salaId, {
        conteudo: content,
        personagem_id: personagemId,
        destinatario_username: destinatarioUsername,
      })
      .then((mensagem) => {
        setMensagensHistorico(prev => [...prev, mensagem]);
      })
      .catch((err) => {
        console.error('Erro ao enviar mensagem via API:', err);
        setError('Erro ao enviar mensagem');
      });
    }
  };

  const handleExecuteCommand = (comando: string, personagemId?: number) => {
    const sucesso = executarComando(comando, personagemId);
    
    if (!sucesso) {
      // Fallback para API REST
      ChatService.executarComando(salaId, {
        comando,
        personagem_id: personagemId,
      })
      .then((mensagem) => {
        setMensagensHistorico(prev => [...prev, mensagem]);
      })
      .catch((err) => {
        console.error('Erro ao executar comando via API:', err);
        setError('Erro ao executar comando');
      });
    }
  };

  const handleToggleUserList = () => {
    setShowUserList(!showUserList);
  };

  const handleReconnect = () => {
    connect(salaId);
  };

  const handleLoadMoreHistory = async () => {
    if (isLoadingHistoryRef.current || mensagensHistorico.length === 0) return;

    try {
      isLoadingHistoryRef.current = true;
      const ultimaMensagem = mensagensHistorico[0];
      
      // Carregar mensagens anteriores (implementar paginação na API)
      const novasMensagens = await ChatService.listarMensagens({
        sala_id: salaId,
        page: Math.floor(mensagensHistorico.length / 50) + 1,
        page_size: 50,
      });

      if (novasMensagens.results.length > 0) {
        setMensagensHistorico(prev => [...novasMensagens.results.reverse(), ...prev]);
      }
    } catch (err) {
      console.error('Erro ao carregar mais mensagens:', err);
    } finally {
      isLoadingHistoryRef.current = false;
    }
  };

  // Render loading state
  if (loading) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-gray-600">Carregando sala de chat...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error && !sala) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <div className="text-center space-y-4">
          <div className="text-red-600 text-xl">⚠️</div>
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-gray-50">
        <div className="flex items-center space-x-3">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {sala?.nome || 'Chat'}
            </h2>
            <p className="text-sm text-gray-600">
              {sala?.campanha.nome} • {participantes.filter(p => p.online).length} online
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <ConnectionIndicator 
            status={status}
            onReconnect={handleReconnect}
          />
          
          <button
            onClick={handleToggleUserList}
            className="p-2 rounded-lg hover:bg-gray-200 relative"
            title="Participantes"
          >
            👥
            {participantes.filter(p => p.online).length > 0 && (
              <span className="absolute -top-1 -right-1 bg-green-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                {participantes.filter(p => p.online).length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 text-sm">
          {error}
          <button 
            onClick={() => setError(null)}
            className="float-right font-bold"
          >
            ×
          </button>
        </div>
      )}

      {/* WebSocket errors */}
      {erros.length > 0 && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 text-sm">
          {erros[erros.length - 1]}
        </div>
      )}

      {/* Main content */}
      <div className="flex flex-1 min-h-0">
        {/* Messages area */}
        <div className="flex-1 flex flex-col">
          <div
            ref={messageListRef}
            className="flex-1 overflow-y-auto"
            onScroll={(e) => {
              const element = e.target as HTMLDivElement;
              // Carregar mais mensagens quando chegar no topo
              if (element.scrollTop === 0 && mensagensHistorico.length > 0) {
                handleLoadMoreHistory();
              }
            }}
          >
            <MessageList
              mensagens={todasMensagens}
              onLoadMore={handleLoadMoreHistory}
              loading={isLoadingHistoryRef.current}
            />
          </div>

          {/* Typing indicator */}
          {usuariosDigitando.length > 0 && (
            <div className="px-4 py-2 border-t">
              <TypingIndicator usuarios={usuariosDigitando} />
            </div>
          )}

          {/* Message input */}
          <div className="border-t">
            <MessageInput
              onSendMessage={handleSendMessage}
              onExecuteCommand={handleExecuteCommand}
              onTyping={marcarDigitando}
              disabled={!isConnected && status !== ConnectionStatus.CONNECTING}
              placeholder={
                isConnected 
                  ? "Digite sua mensagem ou comando..."
                  : "Conectando..."
              }
            />
          </div>
        </div>

        {/* User list sidebar */}
        {showUserList && (
          <div className="w-64 border-l bg-gray-50">
            <UserList
              participantes={participantes}
              onClose={() => setShowUserList(false)}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatRoom;