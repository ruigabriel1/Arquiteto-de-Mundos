// Hook personalizado para gerenciar conexões WebSocket

import { useState, useEffect, useRef, useCallback } from 'react';
import { getWebSocketBaseUrl } from '../services/api';
import {
  WebSocketMessage,
  WebSocketSendMessage,
  ConnectionStatus,
  Mensagem,
  TypingUser,
} from '../types';

interface UseWebSocketOptions {
  salaId?: number;
  autoConnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
  heartbeatInterval?: number;
  typingTimeout?: number;
}

interface UseWebSocketReturn {
  // Estado da conexão
  status: ConnectionStatus;
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  
  // Funções de controle
  connect: (salaId?: number) => void;
  disconnect: () => void;
  sendMessage: (data: WebSocketSendMessage) => boolean;
  
  // Funções específicas do chat
  enviarMensagem: (conteudo: string, personagemId?: number, destinatarioUsername?: string) => boolean;
  executarComando: (comando: string, personagemId?: number) => boolean;
  marcarDigitando: (isTyping: boolean) => void;
  marcarComoLidas: () => void;
  
  // Dados do chat
  mensagens: Mensagem[];
  usuariosDigitando: TypingUser[];
  erros: string[];
  
  // Funções de callback
  onMessage: (callback: (message: WebSocketMessage) => void) => void;
  onConnect: (callback: () => void) => void;
  onDisconnect: (callback: (code?: number) => void) => void;
  onError: (callback: (error: string) => void) => void;
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketReturn => {
  const {
    salaId: initialSalaId,
    autoConnect = false,
    reconnectAttempts = 3,
    reconnectDelay = 3000,
    heartbeatInterval = 30000,
    typingTimeout = 3000,
  } = options;

  // Estado
  const [status, setStatus] = useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [usuariosDigitando, setUsuariosDigitando] = useState<TypingUser[]>([]);
  const [erros, setErros] = useState<string[]>([]);

  // Refs
  const socketRef = useRef<WebSocket | null>(null);
  const salaIdRef = useRef<number | undefined>(initialSalaId);
  const reconnectCountRef = useRef(0);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimerRef = useRef<NodeJS.Timeout | null>(null);
  const typingTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Callbacks
  const onMessageCallbacks = useRef<((message: WebSocketMessage) => void)[]>([]);
  const onConnectCallbacks = useRef<(() => void)[]>([]);
  const onDisconnectCallbacks = useRef<((code?: number) => void)[]>([]);
  const onErrorCallbacks = useRef<((error: string) => void)[]>([]);

  // Estado derivado
  const isConnected = status === ConnectionStatus.CONNECTED;

  // Limpar timers
  const clearTimers = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
      heartbeatTimerRef.current = null;
    }
    if (typingTimerRef.current) {
      clearTimeout(typingTimerRef.current);
      typingTimerRef.current = null;
    }
  }, []);

  // Limpar usuários digitando antigos
  const limparUsuariosDigitando = useCallback(() => {
    const agora = Date.now();
    setUsuariosDigitando(prev => 
      prev.filter(user => agora - user.timestamp < typingTimeout)
    );
  }, [typingTimeout]);

  // Configurar heartbeat
  const iniciarHeartbeat = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
    }
    
    heartbeatTimerRef.current = setInterval(() => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ action: 'ping' }));
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  // Conectar WebSocket
  const connect = useCallback((salaId?: number) => {
    const targetSalaId = salaId || salaIdRef.current;
    
    if (!targetSalaId) {
      console.error('ID da sala é necessário para conectar');
      return;
    }

    if (socketRef.current) {
      disconnect();
    }

    salaIdRef.current = targetSalaId;
    setStatus(ConnectionStatus.CONNECTING);
    setErros([]);

    try {
      const wsUrl = `${getWebSocketBaseUrl()}/ws/chat/sala/${targetSalaId}/`;
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        setStatus(ConnectionStatus.CONNECTED);
        reconnectCountRef.current = 0;
        iniciarHeartbeat();
        
        onConnectCallbacks.current.forEach(callback => callback());
      };

      socket.onclose = (event) => {
        setStatus(ConnectionStatus.DISCONNECTED);
        clearTimers();
        
        onDisconnectCallbacks.current.forEach(callback => callback(event.code));

        // Tentar reconectar se não foi fechamento manual
        if (event.code !== 1000 && reconnectCountRef.current < reconnectAttempts) {
          setStatus(ConnectionStatus.RECONNECTING);
          reconnectCountRef.current++;
          
          reconnectTimerRef.current = setTimeout(() => {
            connect(targetSalaId);
          }, reconnectDelay);
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setStatus(ConnectionStatus.ERROR);
        
        const errorMsg = 'Erro na conexão WebSocket';
        setErros(prev => [...prev, errorMsg]);
        onErrorCallbacks.current.forEach(callback => callback(errorMsg));
      };

      socket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          
          // Processar diferentes tipos de mensagem
          switch (message.type) {
            case 'chat_message':
              if (message.mensagem) {
                setMensagens(prev => [...prev, message.mensagem!]);
              }
              break;

            case 'user_typing':
              if (message.usuario_id && message.usuario_nome) {
                setUsuariosDigitando(prev => {
                  const filtered = prev.filter(u => u.usuario_id !== message.usuario_id);
                  if (message.is_typing) {
                    return [...filtered, {
                      usuario_id: message.usuario_id!,
                      usuario_nome: message.usuario_nome!,
                      timestamp: Date.now()
                    }];
                  }
                  return filtered;
                });
              }
              break;

            case 'error':
              const errorMsg = message.message || 'Erro desconhecido';
              setErros(prev => [...prev, errorMsg]);
              onErrorCallbacks.current.forEach(callback => callback(errorMsg));
              break;

            default:
              break;
          }
          
          onMessageCallbacks.current.forEach(callback => callback(message));
        } catch (error) {
          console.error('Erro ao processar mensagem WebSocket:', error);
        }
      };

    } catch (error) {
      console.error('Erro ao criar WebSocket:', error);
      setStatus(ConnectionStatus.ERROR);
    }
  }, [reconnectAttempts, reconnectDelay, iniciarHeartbeat, clearTimers]);

  // Desconectar WebSocket
  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close(1000, 'Desconexão manual');
      socketRef.current = null;
    }
    clearTimers();
    setStatus(ConnectionStatus.DISCONNECTED);
    setUsuariosDigitando([]);
  }, [clearTimers]);

  // Enviar dados via WebSocket
  const sendMessage = useCallback((data: WebSocketSendMessage): boolean => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket não está conectado');
      return false;
    }

    try {
      socketRef.current.send(JSON.stringify(data));
      return true;
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      return false;
    }
  }, []);

  // Funções específicas do chat
  const enviarMensagem = useCallback((
    conteudo: string, 
    personagemId?: number, 
    destinatarioUsername?: string
  ): boolean => {
    return sendMessage({
      action: 'send_message',
      message: conteudo,
      personagem_id: personagemId,
      destinatario_username: destinatarioUsername,
    });
  }, [sendMessage]);

  const executarComando = useCallback((comando: string, personagemId?: number): boolean => {
    return sendMessage({
      action: 'execute_command',
      command: comando,
      personagem_id: personagemId,
    });
  }, [sendMessage]);

  const marcarDigitando = useCallback((isTyping: boolean) => {
    sendMessage({
      action: 'typing',
      is_typing: isTyping,
    });

    // Auto-parar de digitar após timeout
    if (isTyping) {
      if (typingTimerRef.current) {
        clearTimeout(typingTimerRef.current);
      }
      typingTimerRef.current = setTimeout(() => {
        marcarDigitando(false);
      }, typingTimeout);
    }
  }, [sendMessage, typingTimeout]);

  const marcarComoLidas = useCallback(() => {
    sendMessage({ action: 'mark_read' });
  }, [sendMessage]);

  // Funções de callback
  const onMessage = useCallback((callback: (message: WebSocketMessage) => void) => {
    onMessageCallbacks.current.push(callback);
    return () => {
      onMessageCallbacks.current = onMessageCallbacks.current.filter(cb => cb !== callback);
    };
  }, []);

  const onConnect = useCallback((callback: () => void) => {
    onConnectCallbacks.current.push(callback);
    return () => {
      onConnectCallbacks.current = onConnectCallbacks.current.filter(cb => cb !== callback);
    };
  }, []);

  const onDisconnect = useCallback((callback: (code?: number) => void) => {
    onDisconnectCallbacks.current.push(callback);
    return () => {
      onDisconnectCallbacks.current = onDisconnectCallbacks.current.filter(cb => cb !== callback);
    };
  }, []);

  const onError = useCallback((callback: (error: string) => void) => {
    onErrorCallbacks.current.push(callback);
    return () => {
      onErrorCallbacks.current = onErrorCallbacks.current.filter(cb => cb !== callback);
    };
  }, []);

  // Efeitos
  useEffect(() => {
    if (autoConnect && initialSalaId) {
      connect(initialSalaId);
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, initialSalaId, connect, disconnect]);

  // Limpar usuários digitando periodicamente
  useEffect(() => {
    const interval = setInterval(limparUsuariosDigitando, 1000);
    return () => clearInterval(interval);
  }, [limparUsuariosDigitando]);

  // Limpar ao desmontar
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    // Estado
    status,
    isConnected,
    lastMessage,
    
    // Controle
    connect,
    disconnect,
    sendMessage,
    
    // Chat
    enviarMensagem,
    executarComando,
    marcarDigitando,
    marcarComoLidas,
    
    // Dados
    mensagens,
    usuariosDigitando,
    erros,
    
    // Callbacks
    onMessage,
    onConnect,
    onDisconnect,
    onError,
  };
};