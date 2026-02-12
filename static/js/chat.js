// Cliente de chat minimalista
class ChatClient {
    constructor() {
        this.sesionId = this.generarSesionId();
        this.modeloListo = false;
        this.enviando = false;
        
        this.initElements();
        this.initEvents();
        this.verificarEstado();
    }
    
    generarSesionId() {
        return 'sesion_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    initElements() {
        this.messagesContainer = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.statusIndicator = document.getElementById('status-indicator');
        this.statusText = document.getElementById('status-text');
    }
    
    initEvents() {
        this.sendButton.addEventListener('click', () => this.enviarMensaje());
        
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.enviarMensaje();
            }
        });
        
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = (this.messageInput.scrollHeight) + 'px';
        });
    }
    
    async verificarEstado() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            this.modeloListo = data.modelo_cargado;
            
            if (this.modeloListo) {
                this.statusIndicator.className = 'status-online';
                this.statusText.textContent = 'Modelo listo';
                this.sendButton.disabled = false;
                this.messageInput.disabled = false;
                this.messageInput.focus();
                this.agregarMensajeAsistente('✅ Modelo cargado. ¡Puedes empezar a chatear!');
            } else {
                this.statusIndicator.className = 'status-offline';
                this.statusText.textContent = 'Cargando modelo...';
                this.sendButton.disabled = true;
                this.messageInput.disabled = true;
                setTimeout(() => this.verificarEstado(), 2000);
            }
        } catch (error) {
            console.error('Error verificando estado:', error);
            setTimeout(() => this.verificarEstado(), 5000);
        }
    }
    
    async enviarMensaje() {
        if (this.enviando || !this.modeloListo) return;
        
        const mensaje = this.messageInput.value.trim();
        if (!mensaje) return;
        
        this.enviando = true;
        this.sendButton.disabled = true;
        
        this.agregarMensajeUsuario(mensaje);
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    mensaje: mensaje,
                    sesion_id: this.sesionId
                })
            });
            
            const data = await response.json();
            this.agregarMensajeAsistente(data.respuesta);
            
        } catch (error) {
            console.error('Error:', error);
            this.agregarMensajeAsistente('❌ Error de conexión. Intenta de nuevo.');
        } finally {
            this.enviando = false;
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }
    
    agregarMensajeUsuario(mensaje) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `<div class="message-content">${this.escapeHTML(mensaje)}</div>`;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    agregarMensajeAsistente(mensaje) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        messageDiv.innerHTML = `<div class="message-content">${this.escapeHTML(mensaje)}</div>`;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

// Iniciar chat cuando cargue la página
document.addEventListener('DOMContentLoaded', () => {
    new ChatClient();
});
