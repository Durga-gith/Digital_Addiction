class SimpleChatbot {
    constructor() {
        this.apiBase = 'http://localhost:8000'; 
        this.currentLanguage = 'en';
        this.isVoiceActive = false;
        this.speechRecognition = null;
        this.chatHistory = [];
        this.isChatbotOpen = false;
        
        this.init();
    }
    
    init() {
        this.createChatbotUI();
        this.initSpeechRecognition();
        this.setupEventListeners();
        this.loadChatHistory();
    }
    
    createChatbotUI() {

        const chatbotHTML = `
        <div id="chatbot-container" class="chatbot-container" style="display: none;">
            <!-- Header -->
            <div class="chatbot-header">
                <div class="d-flex align-items-center">
                    <div class="chatbot-avatar me-2">
                        <i class="fas fa-robot text-white"></i>
                    </div>
                    <div>
                        <h6 class="mb-0 text-white">Wellness Assistant</h6>
                        <small class="text-white-50">Always here to help</small>
                    </div>
                </div>
                <div>
                    <button id="chatbot-minimize" class="btn btn-sm btn-light me-2">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button id="chatbot-close" class="btn btn-sm btn-light">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            
            <!-- Messages -->
            <div class="chatbot-messages" id="chatbot-messages">
                <div class="welcome-message">
                    <div class="message bot">
                        <div class="message-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-content">
                            <p class="mb-1"><strong>👋 Hello! I'm your Digital Wellness Assistant</strong></p>
                            <p class="mb-2">I can help you understand your assessment results, manage screen time, reduce digital stress, and improve your digital wellbeing.</p>
                            <div class="d-flex flex-wrap gap-1 mb-2">
                                <span class="badge bg-primary topic-badge" data-topic="assessment">📊 Results</span>
                                <span class="badge bg-info topic-badge" data-topic="screentime">⏰ Screen Time</span>
                                <span class="badge bg-warning topic-badge" data-topic="stress">🧘 Stress</span>
                                <span class="badge bg-success topic-badge" data-topic="detox">🌱 Detox</span>
                            </div>
                            <small class="text-muted">Try typing or using voice input!</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Input Area -->
            <div class="chatbot-input">
                <!-- Quick Actions -->
                <div class="quick-actions mb-2">
                    <button class="btn btn-sm btn-outline-primary quick-action" data-query="Explain my assessment">
                        Results
                    </button>
                    <button class="btn btn-sm btn-outline-primary quick-action" data-query="Screen time tips">
                        Screen Time
                    </button>
                    <button class="btn btn-sm btn-outline-primary quick-action" data-query="Reduce digital stress">
                        Stress Help
                    </button>
                </div>
                
                <!-- Input Group -->
                <div class="input-group">
                    <button id="voice-toggle" class="btn btn-outline-secondary" type="button">
                        <i class="fas fa-microphone"></i>
                    </button>
                    <input type="text" id="chatbot-input" class="form-control" 
                           placeholder="Ask about digital wellness..." autocomplete="off">
                    <button id="send-message" class="btn btn-primary" type="button">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
                
                <!-- Voice Status -->
                <div id="voice-status" class="mt-2 text-center" style="display: none;">
                    <div class="spinner-border spinner-border-sm text-danger me-2" role="status"></div>
                    <span class="text-danger">Listening... Speak now</span>
                </div>
                
                <!-- Footer -->
                <div class="chatbot-footer mt-2 d-flex justify-content-between align-items-center">
                    <button id="toggle-language" class="btn btn-sm btn-outline-secondary">
                        <i class="fas fa-language"></i> <span>EN</span>
                    </button>
                    <div>
                        <button id="clear-chat" class="btn btn-sm btn-link text-muted" title="Clear chat">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button id="help-btn" class="btn btn-sm btn-link text-muted" title="Help">
                            <i class="fas fa-question-circle"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Toggle Button -->
        <button id="chatbot-toggle" class="chatbot-toggle-btn">
            <i class="fas fa-robot"></i>
        </button>
        `;
        

        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
        
        this.addChatbotCSS();
    }
    
    addChatbotCSS() {
        const css = `
        <style>
        /* Chatbot Container */
        .chatbot-container {
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 380px;
            height: 550px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            z-index: 9999;
            overflow: hidden;
        }
        
        /* Toggle Button */
        .chatbot-toggle-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2196f3, #1976d2);
            color: white;
            border: none;
            font-size: 24px;
            cursor: pointer;
            z-index: 10000;
            box-shadow: 0 5px 20px rgba(33, 150, 243, 0.4);
            transition: all 0.3s;
        }
        
        .chatbot-toggle-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 8px 25px rgba(33, 150, 243, 0.6);
        }
        
        /* Header */
        .chatbot-header {
            background: linear-gradient(90deg, #2196f3, #1976d2);
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chatbot-avatar {
            width: 40px;
            height: 40px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Messages Area */
        .chatbot-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            display: flex;
            margin-bottom: 15px;
        }
        
        .message.bot {
            margin-right: auto;
        }
        
        .message.user {
            margin-left: auto;
            flex-direction: row-reverse;
        }
        
        .message-avatar {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 10px;
            flex-shrink: 0;
        }
        
        .message.bot .message-avatar {
            background: #e3f2fd;
            color: #2196f3;
        }
        
        .message.user .message-avatar {
            background: #2196f3;
            color: white;
        }
        
        .message-content {
            max-width: 75%;
            padding: 10px 15px;
            border-radius: 18px;
            position: relative;
        }
        
        .message.bot .message-content {
            background: white;
            border: 1px solid #e0e0e0;
            border-top-left-radius: 4px;
        }
        
        .message.user .message-content {
            background: #2196f3;
            color: white;
            border-top-right-radius: 4px;
        }
        
        /* Input Area */
        .chatbot-input {
            padding: 15px;
            border-top: 1px solid #e0e0e0;
            background: white;
        }
        
        .quick-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .topic-badge {
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .topic-badge:hover {
            transform: translateY(-2px);
        }
        
        /* Typing Indicator */
        .typing-indicator {
            display: flex;
            align-items: center;
            padding: 10px 15px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 18px;
            width: fit-content;
            margin-bottom: 15px;
        }
        
        .typing-dots {
            display: flex;
            gap: 4px;
            margin-right: 10px;
        }
        
        .typing-dots span {
            width: 8px;
            height: 8px;
            background: #2196f3;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: 0s; }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-5px); }
        }
        
        /* Suggestions */
        .suggestions {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px dashed #dee2e6;
        }
        
        .suggestion-btn {
            display: inline-block;
            margin: 2px;
            padding: 4px 10px;
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 15px;
            font-size: 0.85rem;
            color: #1976d2;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .suggestion-btn:hover {
            background: #bbdefb;
            transform: translateY(-1px);
        }
        
        /* Responsive */
        @media (max-width: 576px) {
            .chatbot-container {
                width: calc(100% - 40px);
                height: 70vh;
                right: 20px;
                left: 20px;
                bottom: 20px;
            }
        }
        </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', css);
    }
    
    setupEventListeners() {

        document.getElementById('chatbot-toggle').addEventListener('click', () => this.toggleChatbot());
        
        document.getElementById('chatbot-close').addEventListener('click', () => this.hideChatbot());
        document.getElementById('chatbot-minimize').addEventListener('click', () => this.toggleMinimize());
        
        document.getElementById('send-message').addEventListener('click', () => this.sendMessage());
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        

        document.getElementById('voice-toggle').addEventListener('click', () => this.toggleVoice());
        

        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const query = e.target.dataset.query;
                document.getElementById('chatbot-input').value = query;
                this.sendMessage();
            });
        });
        

        document.querySelectorAll('.topic-badge').forEach(badge => {
            badge.addEventListener('click', (e) => {
                const topic = e.target.dataset.topic;
                this.handleTopic(topic);
            });
        });
        

        document.getElementById('toggle-language').addEventListener('click', () => this.toggleLanguage());
        

        document.getElementById('clear-chat').addEventListener('click', () => this.clearChat());
        

        document.getElementById('help-btn').addEventListener('click', () => this.showHelp());
    }
    
    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.speechRecognition = new SpeechRecognition();
            this.speechRecognition.continuous = false;
            this.speechRecognition.interimResults = false;
            this.speechRecognition.lang = this.currentLanguage === 'fr' ? 'fr-FR' : 'en-US';
            
            this.speechRecognition.onstart = () => {
                this.isVoiceActive = true;
                this.showVoiceStatus(true);
            };
            
            this.speechRecognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('chatbot-input').value = transcript;
                this.sendMessage();
            };
            
            this.speechRecognition.onerror = (event) => {
                console.log('Speech recognition error:', event.error);
                this.isVoiceActive = false;
                this.showVoiceStatus(false);
                this.showNotification('Voice recognition failed. Please try again.', 'error');
            };
            
            this.speechRecognition.onend = () => {
                this.isVoiceActive = false;
                this.showVoiceStatus(false);
            };
        } else {
            document.getElementById('voice-toggle').style.display = 'none';
            console.log('Speech recognition not supported');
        }
    }
    
    toggleVoice() {
        if (!this.speechRecognition) {
            this.showNotification('Voice recognition not supported', 'warning');
            return;
        }
        
        if (this.isVoiceActive) {
            this.speechRecognition.stop();
        } else {
            this.speechRecognition.start();
        }
    }
    
    showVoiceStatus(show) {
        const statusEl = document.getElementById('voice-status');
        const voiceBtn = document.getElementById('voice-toggle');
        
        if (show) {
            statusEl.style.display = 'block';
            voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
            voiceBtn.classList.remove('btn-outline-secondary');
            voiceBtn.classList.add('btn-danger');
        } else {
            statusEl.style.display = 'none';
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceBtn.classList.remove('btn-danger');
            voiceBtn.classList.add('btn-outline-secondary');
        }
    }
    
    toggleLanguage() {
        this.currentLanguage = this.currentLanguage === 'en' ? 'fr' : 'en';
        const btn = document.getElementById('toggle-language');
        btn.querySelector('span').textContent = this.currentLanguage.toUpperCase();
        
        if (this.speechRecognition) {
            this.speechRecognition.lang = this.currentLanguage === 'fr' ? 'fr-FR' : 'en-US';
        }
        
        const placeholder = this.currentLanguage === 'en' 
            ? 'Ask about digital wellness...' 
            : 'Demandez sur le bien-être numérique...';
        document.getElementById('chatbot-input').placeholder = placeholder;
        
        this.showNotification(`Language: ${this.currentLanguage.toUpperCase()}`, 'info');
    }
    
    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message) return;
        

        this.addMessage(message, 'user');
        input.value = '';
        

        this.showTyping();
        
        try {

            const context = this.getUserContext();
            

            const response = await this.callChatbotAPI(message, context);
            

            this.hideTyping();
            
            this.addMessage(response.response, 'bot');
            
            if (response.suggestions && response.suggestions.length > 0) {
                this.addSuggestions(response.suggestions);
            }
            
            this.saveMessage(message, response.response);
            
        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTyping();
            this.addMessage("Sorry, I'm having trouble connecting. Please try again later.", 'bot');
        }
    }
    
    async callChatbotAPI(message, context) {
        const payload = {
            message: message,
            language: this.currentLanguage,
            user_id: window.currentUser ? window.currentUser.username : null,
            context: context,
            chat_history: this.chatHistory.slice(-3)
        };
        
        const response = await fetch(`${this.apiBase}/api/chatbot/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    getUserContext() {
        const context = {};
        
        if (window.assessmentHistory && window.assessmentHistory.length > 0) {
            const latest = window.assessmentHistory[0];
            context.assessment = {
                risk_score: latest.risk_score,
                addiction_level: latest.addiction_level
            };
        }
        
        if (window.predictionData) {
            context.prediction = {
                trend: window.predictionData.trend
            };
        }
        
        context.language = this.currentLanguage;
        
        return context;
    }
    
    addMessage(text, sender) {
        const messagesContainer = document.getElementById('chatbot-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-content">
                <p class="mb-1">${this.formatMessage(text)}</p>
                <small class="text-muted">${time}</small>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    addSuggestions(suggestions) {
        const messagesContainer = document.getElementById('chatbot-messages');
        
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'suggestions';
        
        let html = '<p class="mb-1"><small><strong>💡 You might also ask:</strong></small></p>';
        suggestions.forEach(suggestion => {
            html += `<button class="suggestion-btn" onclick="window.chatbot.quickQuery('${suggestion}')">${suggestion}</button>`;
        });
        
        suggestionsDiv.innerHTML = html;
        messagesContainer.appendChild(suggestionsDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    quickQuery(query) {
        document.getElementById('chatbot-input').value = query;
        this.sendMessage();
    }
    
    handleTopic(topic) {
        const queries = {
            'assessment': 'Can you explain my assessment results?',
            'screentime': 'How can I reduce my screen time effectively?',
            'stress': 'What are good digital stress management techniques?',
            'detox': 'Tell me about digital detox strategies'
        };
        
        this.quickQuery(queries[topic] || queries.assessment);
    }
    
    showTyping() {
        const messagesContainer = document.getElementById('chatbot-messages');
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span>Assistant is typing...</span>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    hideTyping() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }
    
    formatMessage(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>')
            .replace(/🌲/g, '🌲 ')
            .replace(/📊/g, '📊 ')
            .replace(/🧘/g, '🧘 ')
            .replace(/⚠️/g, '⚠️ ')
            .replace(/✅/g, '✅ ');
    }
    
    saveMessage(userMsg, botMsg) {
        this.chatHistory.push({
            user: userMsg,
            bot: botMsg,
            time: new Date().toISOString(),
            lang: this.currentLanguage
        });
        

        if (this.chatHistory.length > 20) {
            this.chatHistory = this.chatHistory.slice(-20);
        }
        
        localStorage.setItem('chatbot_history', JSON.stringify(this.chatHistory));
    }
    
    loadChatHistory() {
        const saved = localStorage.getItem('chatbot_history');
        if (saved) {
            try {
                this.chatHistory = JSON.parse(saved);
            } catch (e) {
                this.chatHistory = [];
            }
        }
    }
    
    clearChat() {
        if (confirm('Clear all chat history?')) {
            this.chatHistory = [];
            localStorage.removeItem('chatbot_history');
            const messages = document.getElementById('chatbot-messages');
            messages.innerHTML = `
                <div class="welcome-message">
                    <div class="message bot">
                        <div class="message-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-content">
                            <p class="mb-1"><strong>Chat cleared!</strong></p>
                            <p class="mb-2">How can I help you with your digital wellness today?</p>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    showHelp() {
        this.addMessage("**Help Guide:**\n• Type your questions about digital wellness\n• Use voice button for speech input\n• Click topic badges for quick questions\n• Switch languages with EN/FR button\n• Chat history saves automatically", 'bot');
    }
    
    toggleChatbot() {
        const container = document.getElementById('chatbot-container');
        if (container.style.display === 'none') {
            container.style.display = 'flex';
            this.isChatbotOpen = true;
            document.getElementById('chatbot-input').focus();
        } else {
            container.style.display = 'none';
            this.isChatbotOpen = false;
        }
    }
    
    hideChatbot() {
        document.getElementById('chatbot-container').style.display = 'none';
        this.isChatbotOpen = false;
    }
    
    toggleMinimize() {
        const container = document.getElementById('chatbot-container');
        const messages = document.getElementById('chatbot-messages');
        const input = document.querySelector('.chatbot-input');
        
        if (messages.style.display !== 'none') {
            messages.style.display = 'none';
            input.style.display = 'none';
            container.style.height = 'auto';
        } else {
            messages.style.display = 'block';
            input.style.display = 'block';
            container.style.height = '550px';
        }
    }
    
    showNotification(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.style.cssText = 'position:fixed; top:20px; right:20px; z-index:10001; min-width:300px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(alert);
        setTimeout(() => {
            if (alert.parentNode) alert.remove();
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    window.chatbot = new SimpleChatbot();
    
    const existingNav = document.querySelector('.navbar-nav');
    if (existingNav) {
        const chatNavItem = document.createElement('li');
        chatNavItem.className = 'nav-item';
        chatNavItem.innerHTML = `
            <button class="btn btn-outline-primary" onclick="window.chatbot.toggleChatbot()">
                <i class="fas fa-robot me-1"></i>Chat Assistant
            </button>
        `;
        existingNav.appendChild(chatNavItem);
    }
});