/**
 * Sistema de Modo de Jogo - Arquiteto de Mundos
 * Implementa o comportamento de Mestre IA durante sessões ativas
 */

class GameSessionManager {
    constructor(sessaoId) {
        this.sessaoId = sessaoId;
        this.estado = 'configuracao';
        this.turnoAtual = 0;
        this.faseAtual = 'aguardando';
        this.personagemAtual = null;
        this.statusInterval = null;
        
        this.initializeElements();
        this.attachEventListeners();
        this.startStatusPolling();
    }
    
    initializeElements() {
        // Elementos principais da interface
        this.chatContainer = document.querySelector('.chat-container');
        this.messageInput = document.querySelector('#message-input');
        this.sendButton = document.querySelector('#send-message');
        this.statusIndicator = document.querySelector('.status-sessao');
        
        // Botões de controle
        this.iniciarJogoBtn = document.querySelector('#iniciar-modo-jogo');
        this.pausarBtn = document.querySelector('#pausar-sessao');
        this.retomarBtn = document.querySelector('#retomar-sessao');
        this.encerrarBtn = document.querySelector('#encerrar-sessao');
        
        // Elementos de status
        this.turnoDisplay = document.querySelector('#turno-atual');
        this.faseDisplay = document.querySelector('#fase-atual');
        this.aguardandoDisplay = document.querySelector('#aguardando-jogadores');
    }
    
    attachEventListeners() {
        // Botão de iniciar modo de jogo
        if (this.iniciarJogoBtn) {
            this.iniciarJogoBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.ativarModoJogo();
            });
        }
        
        // Botões de controle de sessão
        if (this.pausarBtn) {
            this.pausarBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.pausarSessao();
            });
        }
        
        if (this.retomarBtn) {
            this.retomarBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.retomarSessao();
            });
        }
        
        if (this.encerrarBtn) {
            this.encerrarBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.encerrarSessao();
            });
        }
        
        // Input de mensagens - intercepta TODOS os eventos
        if (this.messageInput && this.sendButton) {
            // Remove event listeners existentes
            this.sendButton.removeAttribute('onclick');
            this.messageInput.removeAttribute('onkeypress');
            
            this.sendButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.processarAcaoJogador();
            });
            
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.processarAcaoJogador();
                }
            });
        }
        
        // Sobrescreve funções globais do template para evitar conflito
        window.enviarMensagem = () => this.processarAcaoJogador();
        window.ativarModoJogo = () => this.ativarModoJogo();
        
        // Atalhos de teclado
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                e.stopPropagation();
                this.processarAcaoJogador();
            }
        });
    }
    
    async ativarModoJogo() {
        try {
            this.showLoading('Ativando modo de jogo...');
            
            const response = await this.makeRequest('/arquiteto/api/ativar-modo-jogo/', {
                method: 'POST',
                body: JSON.stringify({
                    sessao_id: this.sessaoId
                })
            });
            
            if (response.sucesso) {
                this.estado = 'ativa';
                this.atualizarInterface(response);
                this.adicionarMensagemSistema('🎲 MODO DE JOGO ATIVADO', 'Eu agora sou o Mestre da sessão!');
                this.exibirSituacaoInicial(response.modo_jogo.situacao);
                this.mostrarChamadaJogadores(response.aguardo_acoes.mensagem_chamada);
            } else {
                this.showError('Erro ao ativar modo de jogo: ' + (response.erro || 'Erro desconhecido'));
            }
        } catch (error) {
            this.showError('Erro de conexão: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    async processarAcaoJogador() {
        const acao = this.messageInput.value.trim();
        if (!acao) return;
        
        try {
            // Mostra a ação do jogador imediatamente
            this.adicionarMensagemJogador(acao);
            this.messageInput.value = '';
            
            // Mostrar indicador de digitação
            this.mostrarIndicadorDigitacao();
            
            const response = await this.makeRequest('/arquiteto/api/processar-acao/', {
                method: 'POST',
                body: JSON.stringify({
                    sessao_id: this.sessaoId,
                    acao: acao
                })
            });
            
            // Esconder indicador de digitação
            this.esconderIndicadorDigitacao();
            
            if (response.sucesso) {
                this.processarRespostaAcao(response.resultado);
            } else {
                this.showError('Erro ao processar ação: ' + (response.erro || 'Erro desconhecido'));
            }
        } catch (error) {
            this.esconderIndicadorDigitacao();
            this.showError('Erro de conexão: ' + error.message);
        }
    }
    
    async pausarSessao() {
        try {
            const response = await this.makeRequest('/arquiteto/api/pausar-sessao/', {
                method: 'POST',
                body: JSON.stringify({
                    sessao_id: this.sessaoId
                })
            });
            
            if (response.sucesso) {
                this.estado = 'pausada';
                this.atualizarBotoesControle();
                this.adicionarMensagemSistema('⏸️ SESSÃO PAUSADA', response.resultado.mensagem);
            }
        } catch (error) {
            this.showError('Erro ao pausar sessão: ' + error.message);
        }
    }
    
    async retomarSessao() {
        try {
            const response = await this.makeRequest('/arquiteto/api/retomar-sessao/', {
                method: 'POST',
                body: JSON.stringify({
                    sessao_id: this.sessaoId
                })
            });
            
            if (response.sucesso) {
                this.estado = 'ativa';
                this.atualizarBotoesControle();
                this.adicionarMensagemSistema('▶️ SESSÃO RETOMADA', response.resultado.mensagem);
            }
        } catch (error) {
            this.showError('Erro ao retomar sessão: ' + error.message);
        }
    }
    
    async encerrarSessao() {
        const confirmacao = confirm('Tem certeza que deseja encerrar esta sessão? Esta ação não pode ser desfeita.');
        if (!confirmacao) return;
        
        try {
            const resumo = prompt('Digite um resumo da sessão (opcional):') || '';
            
            const response = await this.makeRequest('/arquiteto/api/encerrar-sessao/', {
                method: 'POST',
                body: JSON.stringify({
                    sessao_id: this.sessaoId,
                    resumo_final: resumo
                })
            });
            
            if (response.sucesso) {
                this.estado = 'encerrada';
                this.stopStatusPolling();
                this.atualizarBotoesControle();
                this.adicionarMensagemSistema('🏁 SESSÃO ENCERRADA', 'Obrigado por jogarem!');
                
                // Redirecionar após 3 segundos
                setTimeout(() => {
                    window.location.href = '/arquiteto/';
                }, 3000);
            }
        } catch (error) {
            this.showError('Erro ao encerrar sessão: ' + error.message);
        }
    }
    
    processarRespostaAcao(resultado) {
        if (resultado.erro) {
            this.adicionarMensagemErro(resultado.erro);
            return;
        }
        
        if (resultado.acao_confirmada) {
            this.adicionarMensagemConfirmacao(resultado.acao_confirmada);
        }
        
        if (resultado.aguardando) {
            this.mostrarAguardandoJogadores(resultado.aguardando);
            this.adicionarMensagemSistema('⏳ Aguardando', resultado.mensagem);
        }
        
        if (resultado.turno_processado) {
            this.processarTurnoCompleto(resultado);
        }
        
        if (resultado.mensagem) {
            this.adicionarMensagemMestre(resultado.mensagem);
        }
    }
    
    processarTurnoCompleto(resultado) {
        this.turnoAtual = resultado.proximo_turno;
        
        // Mostra as ações processadas
        this.adicionarMensagemSistema(
            `✅ Turno ${resultado.numero_turno} Processado`,
            resultado.acoes_processadas.join('\n')
        );
        
        // Mostra a narrativa resultado
        if (resultado.narrativa_resultado) {
            this.adicionarMensagemMestre(resultado.narrativa_resultado);
        }
        
        // Atualiza interface
        this.atualizarTurno(resultado.proximo_turno);
        this.limparAguardandoJogadores();
        
        // Se há nova situação gerada, exibe imediatamente
        if (resultado.nova_situacao) {
            setTimeout(() => {
                this.exibirNovaSituacao(resultado.nova_situacao);
            }, 2000);
        }
    }
    
    exibirNovaSituacao(nova_situacao) {
        // Exibe a nova situação gerada pela IA
        this.adicionarMensagemMestre(nova_situacao.situacao);
        
        // Mostra chamada para os jogadores
        this.mostrarChamadaJogadores(nova_situacao.chamada_jogadores);
        
        // Indica se foi gerada por IA ou fallback
        if (nova_situacao.gerada_por_ia) {
            this.adicionarMensagemSistema(
                '🤖 IA Ativa', 
                'Situação gerada dinamicamente pela inteligência artificial!'
            );
        }
    }
    
    // Interface visual
    exibirSituacaoInicial(situacao) {
        this.adicionarMensagemMestre(situacao);
    }
    
    adicionarMensagemMestre(conteudo) {
        this.adicionarMensagem(conteudo, 'ia-gm', '🤖 IA GM', '#7c3aed');
    }
    
    adicionarMensagemJogador(conteudo) {
        this.adicionarMensagem(conteudo, 'jogador', '👤 Você', '#3b82f6');
    }
    
    adicionarMensagemSistema(titulo, conteudo) {
        this.adicionarMensagem(`**${titulo}**\n${conteudo}`, 'sistema', '⚙️ Sistema', '#10b981');
    }
    
    adicionarMensagemConfirmacao(conteudo) {
        this.adicionarMensagem(conteudo, 'confirmacao', '✅ Confirmado', '#059669');
    }
    
    adicionarMensagemErro(erro) {
        this.adicionarMensagem(erro, 'erro', '❌ Erro', '#dc2626');
    }
    
    adicionarMensagem(conteudo, tipo, autor, cor) {
        // Encontra o container correto (pode ser .chat-container ou #chat-container)
        const container = document.getElementById('chat-container') || document.querySelector('.chat-container');
        if (!container) return;
        
        const messageDiv = document.createElement('div');
        
        // Usa classes do template existente se possível
        if (tipo === 'ia-gm' || tipo === 'ia') {
            messageDiv.className = 'chat-message ia';
        } else if (tipo === 'jogador' || tipo === 'user') {
            messageDiv.className = 'chat-message user';
        } else {
            messageDiv.className = 'chat-message system';
        }
        
        const timestamp = new Date().toLocaleTimeString();
        const conteudoFormatado = this.formatarConteudo(conteudo);
        
        messageDiv.innerHTML = `
            <div class="message-header" style="color: ${cor || ''}">
                <strong>${autor}</strong>
                <span class="text-muted">${timestamp}</span>
            </div>
            <div class="message-content">${conteudoFormatado}</div>
        `;
        
        // Insere antes do indicador de digitação se existir
        const typingIndicator = container.querySelector('#typing-indicator');
        if (typingIndicator) {
            container.insertBefore(messageDiv, typingIndicator);
        } else {
            container.appendChild(messageDiv);
        }
        
        this.scrollToBottom();
        
        // Remove mensagem de boas-vindas se ainda estiver presente
        const welcomeMsg = container.querySelector('#welcome-message');
        if (welcomeMsg && this.estado === 'ativa') {
            welcomeMsg.remove();
        }
    }
    
    formatarConteudo(conteudo) {
        // Converte markdown básico para HTML
        return conteudo
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }
    
    mostrarChamadaJogadores(mensagem) {
        this.adicionarMensagem(mensagem, 'chamada-jogadores', '📢 Chamada', '#f59e0b');
    }
    
    mostrarAguardandoJogadores(jogadores) {
        if (this.aguardandoDisplay) {
            this.aguardandoDisplay.textContent = `Aguardando: ${jogadores}`;
        }
    }
    
    limparAguardandoJogadores() {
        if (this.aguardandoDisplay) {
            this.aguardandoDisplay.textContent = '';
        }
    }
    
    atualizarTurno(turno) {
        if (this.turnoDisplay) {
            this.turnoDisplay.textContent = `Turno ${turno}`;
        }
        this.turnoAtual = turno;
    }
    
    atualizarInterface(response) {
        this.atualizarBotoesControle();
        this.atualizarStatus(response);
    }
    
    atualizarBotoesControle() {
        // Controla visibilidade dos botões baseado no estado
        if (this.iniciarJogoBtn) {
            this.iniciarJogoBtn.style.display = this.estado === 'configuracao' ? 'inline-block' : 'none';
        }
        
        if (this.pausarBtn) {
            this.pausarBtn.style.display = this.estado === 'ativa' ? 'inline-block' : 'none';
        }
        
        if (this.retomarBtn) {
            this.retomarBtn.style.display = this.estado === 'pausada' ? 'inline-block' : 'none';
        }
        
        if (this.encerrarBtn) {
            this.encerrarBtn.disabled = this.estado === 'encerrada';
        }
        
        // Controla input de mensagens
        if (this.messageInput && this.sendButton) {
            const habilitado = this.estado === 'ativa';
            this.messageInput.disabled = !habilitado;
            this.sendButton.disabled = !habilitado;
            
            if (habilitado) {
                this.messageInput.placeholder = 'Digite sua ação...';
            } else {
                this.messageInput.placeholder = 'Sessão não está ativa...';
            }
        }
    }
    
    atualizarStatus(response) {
        if (response && response.status) {
            const status = response.status;
            this.atualizarTurno(status.turno_atual || this.turnoAtual);
            this.mostrarAguardandoJogadores(status.aguardando_personagens?.join(', ') || '');
        }
    }
    
    // Polling de status
    startStatusPolling() {
        this.statusInterval = setInterval(async () => {
            if (this.estado === 'ativa' || this.estado === 'pausada') {
                await this.verificarStatus();
            }
        }, 5000); // Verifica status a cada 5 segundos
    }
    
    stopStatusPolling() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = null;
        }
    }
    
    async verificarStatus() {
        try {
            const response = await this.makeRequest(`/arquiteto/api/status-sessao/${this.sessaoId}/`);
            if (response.sucesso) {
                this.atualizarStatus(response);
            }
        } catch (error) {
            console.error('Erro ao verificar status:', error);
        }
    }
    
    // Utilitários
    scrollToBottom() {
        const container = document.getElementById('chat-container') || document.querySelector('.chat-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }
    
    mostrarIndicadorDigitacao() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.style.display = 'block';
            this.scrollToBottom();
        }
    }
    
    esconderIndicadorDigitacao() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    showLoading(message) {
        // Implementar loading indicator
        console.log('Loading:', message);
    }
    
    hideLoading() {
        // Remover loading indicator
        console.log('Loading finished');
    }
    
    showError(message) {
        this.adicionarMensagemErro(message);
        console.error('Game Session Error:', message);
    }
    
    async makeRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };
        
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    getCSRFToken() {
        const cookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
}

// Inicialização automática quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    // Verifica se estamos em uma página de sessão
    const sessaoIdElement = document.querySelector('[data-sessao-id]');
    if (sessaoIdElement) {
        const sessaoId = sessaoIdElement.dataset.sessaoId;
        window.gameSession = new GameSessionManager(sessaoId);
        console.log('🎮 Game Session Manager inicializado para sessão:', sessaoId);
    }
});

// CSS adicional para as mensagens do jogo
const additionalCSS = `
.message.ia-gm {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(139, 92, 246, 0.1));
    border-left: 4px solid #7c3aed;
}

.message.jogador {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(96, 165, 250, 0.1));
    border-left: 4px solid #3b82f6;
}

.message.sistema {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(52, 211, 153, 0.1));
    border-left: 4px solid #10b981;
}

.message.confirmacao {
    background: linear-gradient(135deg, rgba(5, 150, 105, 0.2), rgba(16, 185, 129, 0.1));
    border-left: 4px solid #059669;
}

.message.erro {
    background: linear-gradient(135deg, rgba(220, 38, 38, 0.2), rgba(248, 113, 113, 0.1));
    border-left: 4px solid #dc2626;
}

.message.chamada-jogadores {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(251, 191, 36, 0.1));
    border-left: 4px solid #f59e0b;
    animation: pulse 2s infinite;
}

.message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
}

.timestamp {
    opacity: 0.7;
    font-size: 0.75rem;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}
`;

// Injeta CSS adicional
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);