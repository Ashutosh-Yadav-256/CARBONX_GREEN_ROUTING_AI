/* ═══════════════════════════════════════════════════════════════════════════
   AI Chatbot — Frontend Application Logic
   Handles messaging, API calls, and UI interactions
   ═══════════════════════════════════════════════════════════════════════════ */

(() => {
    'use strict';

    // ─── Configuration ───────────────────────────────────────────────────────
    const API_BASE = window.location.origin;
    const MAX_CHAR = 2000;

    // ─── DOM Elements ────────────────────────────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const messagesContainer = $('#messages-container');
    const messagesEl = $('#messages');
    const messageInput = $('#message-input');
    const sendBtn = $('#send-btn');
    const clearChatBtn = $('#clear-chat-btn');
    const welcomeScreen = $('#welcome-screen');
    const charCount = $('#char-count');
    const statusDot = $('.status-dot');
    const statusText = $('.status-text');
    const mobileMenuBtn = $('#mobile-menu-btn');
    const sidebar = $('#sidebar');
    const activeBadge = $('#active-tool-badge');
    const activeToolIcon = $('#active-tool-icon');
    const activeToolName = $('#active-tool-name');
    const badgeClose = $('#badge-close');
    const chatTitle = $('#chat-title');
    const chatSubtitle = $('#chat-subtitle');

    // ─── State ───────────────────────────────────────────────────────────────
    let isProcessing = false;
    let currentTool = 'chat';
    let conversationHistory = [];

    // ─── Tool Definitions ────────────────────────────────────────────────────
    const TOOLS = {
        chat:   { icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>', name: 'Chat',       title: 'AI Assistant',     subtitle: '' },
        search: { icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>', name: 'Web Search', title: 'Web Search',       subtitle: 'Real-time information via DuckDuckGo' },
        image:  { icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5"></circle><circle cx="17.5" cy="10.5" r=".5"></circle><circle cx="8.5" cy="7.5" r=".5"></circle><circle cx="6.5" cy="12.5" r=".5"></circle><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"></path></svg>', name: 'Image Gen',  title: 'Image Generator',  subtitle: 'Create images with Stable Diffusion' },
        rag:    { icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path></svg>', name: 'Knowledge',   title: 'Knowledge Base',   subtitle: 'Query your documents with RAG' },
    };

    // ─── Initialization ─────────────────────────────────────────────────────
    function init() {
        bindEvents();
        autoResizeInput();
        messageInput.focus();
        checkApiHealth();
    }

    // ─── Event Bindings ──────────────────────────────────────────────────────
    function bindEvents() {
        // Send message
        sendBtn.addEventListener('click', handleSend);
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });

        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            autoResizeInput();
            updateCharCount();
        });

        // Clear chat
        clearChatBtn.addEventListener('click', clearChat);

        // Tool navigation
        $$('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tool = btn.dataset.tool;
                setActiveTool(tool);
            });
        });

        // Capability cards
        $$('.capability-card').forEach(card => {
            card.addEventListener('click', () => {
                const action = card.dataset.action;
                setActiveTool(action);
                messageInput.focus();
            });
        });

        // Command chips
        $$('.chip').forEach(chip => {
            chip.addEventListener('click', () => {
                messageInput.value = chip.dataset.query;
                autoResizeInput();
                updateCharCount();
                messageInput.focus();
            });
        });

        // Badge close
        badgeClose.addEventListener('click', () => {
            setActiveTool('chat');
        });

        // Mobile menu
        mobileMenuBtn.addEventListener('click', toggleSidebar);

        // Close sidebar on overlay click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('sidebar-overlay')) {
                toggleSidebar();
            }
        });
    }

    // ─── API Health Check ────────────────────────────────────────────────────
    async function checkApiHealth() {
        try {
            const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
            if (res.ok) {
                setStatus('ready', 'Connected');
            } else {
                setStatus('error', 'API Error');
            }
        } catch {
            setStatus('error', 'API Offline');
        }
    }

    // ─── Send Message ────────────────────────────────────────────────────────
    async function handleSend() {
        const query = messageInput.value.trim();
        if (!query || isProcessing) return;

        // Detect tool from command prefix or current active tool
        let effectiveTool = currentTool;
        let effectiveQuery = query;

        if (query.startsWith('/search ') || query.startsWith('/s ')) {
            effectiveTool = 'search';
        } else if (query.startsWith('/image ') || query.startsWith('/img ')) {
            effectiveTool = 'image';
        } else if (query.startsWith('/rag ') || query.startsWith('/doc ')) {
            effectiveTool = 'rag';
        }

        // Hide welcome screen
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }

        // Add user message
        addMessage('user', query);
        messageInput.value = '';
        autoResizeInput();
        updateCharCount();

        // Show typing indicator
        isProcessing = true;
        sendBtn.disabled = true;
        setStatus('busy', 'Processing...');
        const typingEl = showTypingIndicator();

        try {
            const response = await callApi(effectiveQuery);
            removeTypingIndicator(typingEl);
            addAssistantMessage(response);
            setStatus('ready', 'Ready');
        } catch (err) {
            removeTypingIndicator(typingEl);
            addMessage('assistant', `⚠️ Error: ${err.message}`, 'error');
            setStatus('error', 'Error');
            showErrorToast(err.message);
        } finally {
            isProcessing = false;
            sendBtn.disabled = false;
            messageInput.focus();
        }
    }

    // ─── API Call ────────────────────────────────────────────────────────────
    async function callApi(query) {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                session_id: 'default',
            }),
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || `Server error (${res.status})`);
        }

        return await res.json();
    }

    // ─── Message Rendering ───────────────────────────────────────────────────
    function addMessage(role, content, type = 'chat') {
        const msg = document.createElement('div');
        msg.className = `message ${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>' : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="14" x="3" y="7" rx="2"></rect><path d="M12 7V3"></path><path d="M9 3h6"></path><path d="M8 12h.01"></path><path d="M16 12h.01"></path><path d="M10 16h4"></path></svg>';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = formatMarkdown(content);

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = formatTime(new Date());

        bubble.appendChild(contentDiv);
        bubble.appendChild(time);
        msg.appendChild(avatar);
        msg.appendChild(bubble);

        messagesEl.appendChild(msg);
        scrollToBottom();

        // Track conversation
        conversationHistory.push({ role, content });
    }

    function addAssistantMessage(response) {
        const type = response.type || 'chat';
        const content = response.content || 'No response.';
        const imageUrl = response.image_url;

        const msg = document.createElement('div');
        msg.className = 'message assistant';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="14" x="3" y="7" rx="2"></rect><path d="M12 7V3"></path><path d="M9 3h6"></path><path d="M8 12h.01"></path><path d="M16 12h.01"></path><path d="M10 16h4"></path></svg>';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        // Type badge
        const badge = document.createElement('div');
        badge.className = `message-type-badge badge-${type}`;
        const badgeIcons = {
            chat: '<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>',
            search: '<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>',
            image: '<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5"></circle><circle cx="17.5" cy="10.5" r=".5"></circle><circle cx="8.5" cy="7.5" r=".5"></circle><circle cx="6.5" cy="12.5" r=".5"></circle><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"></path></svg>',
            rag: '<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path></svg>',
            error: '<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
        };
        badge.innerHTML = `<span style="display:flex;align-items:center;margin-right:6px;">${badgeIcons[type] || badgeIcons.chat}</span> ${type}`;
        bubble.appendChild(badge);

        // Content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = formatMarkdown(content);
        bubble.appendChild(contentDiv);

        // Image (if present)
        if (imageUrl) {
            const imageContainer = document.createElement('div');
            imageContainer.className = 'message-image';

            const img = document.createElement('img');
            img.src = `${API_BASE}${imageUrl}`;
            img.alt = 'Generated image';
            img.loading = 'lazy';
            img.onerror = () => {
                img.style.display = 'none';
                const fallback = document.createElement('div');
                fallback.className = 'shimmer';
                fallback.style.cssText = 'width:100%;height:200px;display:flex;align-items:center;justify-content:center;';
                fallback.innerHTML = '<span style="color:var(--text-tertiary)">Image failed to load</span>';
                imageContainer.appendChild(fallback);
            };

            imageContainer.appendChild(img);
            bubble.appendChild(imageContainer);
        }

        // Timestamp
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = formatTime(new Date());
        bubble.appendChild(time);

        msg.appendChild(avatar);
        msg.appendChild(bubble);
        messagesEl.appendChild(msg);
        scrollToBottom();

        conversationHistory.push({ role: 'assistant', content, type, imageUrl });
    }

    // ─── Typing Indicator ────────────────────────────────────────────────────
    function showTypingIndicator() {
        const el = document.createElement('div');
        el.className = 'typing-indicator';
        el.id = 'typing-indicator';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="14" x="3" y="7" rx="2"></rect><path d="M12 7V3"></path><path d="M9 3h6"></path><path d="M8 12h.01"></path><path d="M16 12h.01"></path><path d="M10 16h4"></path></svg>';
        avatar.style.background = 'linear-gradient(135deg, #a855f7, #6366f1)';
        avatar.style.boxShadow = '0 0 12px rgba(168, 85, 247, 0.2)';

        const bubble = document.createElement('div');
        bubble.className = 'typing-bubble';
        bubble.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;

        el.appendChild(avatar);
        el.appendChild(bubble);
        messagesEl.appendChild(el);
        scrollToBottom();
        return el;
    }

    function removeTypingIndicator(el) {
        if (el && el.parentNode) {
            el.parentNode.removeChild(el);
        }
    }

    // ─── Markdown Formatting ─────────────────────────────────────────────────
    function formatMarkdown(text) {
        if (!text) return '';

        let html = escapeHtml(text);

        // Code blocks (```...```)
        html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
            return `<pre><code>${code.trim()}</code></pre>`;
        });

        // Inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Bold
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Italic
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Links [text](url)
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

        // Unordered lists
        html = html.replace(/^[-*] (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

        // Ordered lists
        html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

        // Headings
        html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>');
        html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>');

        // Horizontal rules
        html = html.replace(/^---$/gm, '<hr>');

        // Line breaks → paragraphs
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');

        // Wrap in paragraph if not already wrapped
        if (!html.startsWith('<')) {
            html = `<p>${html}</p>`;
        }

        return html;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ─── Tool Management ─────────────────────────────────────────────────────
    function setActiveTool(tool) {
        currentTool = tool;

        // Update nav buttons
        $$('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tool === tool);
        });

        // Update header
        const toolInfo = TOOLS[tool];
        if (toolInfo) {
            chatTitle.textContent = toolInfo.title;
            chatSubtitle.textContent = toolInfo.subtitle;
        }

        // Update input badge
        if (tool !== 'chat') {
            activeBadge.style.display = 'flex';
            activeToolIcon.innerHTML = toolInfo.icon;
            activeToolName.textContent = toolInfo.name;
        } else {
            activeBadge.style.display = 'none';
        }

        // Update placeholder
        const placeholders = {
            chat:   'Type your message...',
            search: 'What would you like to search for?',
            image:  'Describe the image you want to generate...',
            rag:    'Ask a question about your documents...',
        };
        messageInput.placeholder = placeholders[tool] || 'Type your message...';

        // Close mobile sidebar
        if (window.innerWidth <= 768) {
            closeSidebar();
        }
    }

    // ─── UI Helpers ──────────────────────────────────────────────────────────
    function autoResizeInput() {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
    }

    function updateCharCount() {
        const len = messageInput.value.length;
        if (len > 0) {
            charCount.textContent = `${len}/${MAX_CHAR}`;
            charCount.style.color = len > MAX_CHAR ? '#ef4444' : '';
        } else {
            charCount.textContent = '';
        }
    }

    function scrollToBottom() {
        requestAnimationFrame(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        });
    }

    function formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function clearChat() {
        // Keep welcome screen, remove messages
        const messages = messagesEl.querySelectorAll('.message, .typing-indicator');
        messages.forEach(msg => msg.remove());
        conversationHistory = [];

        if (welcomeScreen) {
            welcomeScreen.style.display = 'flex';
        }
    }

    function setStatus(state, text) {
        statusDot.className = 'status-dot';
        if (state === 'busy') statusDot.classList.add('busy');
        if (state === 'error') statusDot.classList.add('error');
        statusText.textContent = text;
    }

    function toggleSidebar() {
        const isOpen = sidebar.classList.contains('open');
        if (isOpen) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    function openSidebar() {
        sidebar.classList.add('open');
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
        }
        overlay.classList.add('show');
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) overlay.classList.remove('show');
    }

    function showErrorToast(message) {
        const toast = document.createElement('div');
        toast.className = 'error-toast';
        toast.textContent = `⚠️ ${message}`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    // ─── Start ───────────────────────────────────────────────────────────────
    init();
})();
