// State
let mode = 'rag';
let loading = false;
let uploading = false;
const sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8);

const MODE_DESCRIPTIONS = {
    'rag': 'RAG mode: Search your uploaded PDF knowledge base using Pinecone vector store.',
    'api': 'API mode: Search the web using SerpAPI (Google Search and Google Images).',
    'mcp': 'MCP mode: Use tools from a remote MCP server over HTTP (streamable).',
    'mcp-stdio': 'MCP-stdio mode: Use tools from a local MCP server over stdio transport.',
};

// Elements
let chatArea, messageInput, sendBtn, loadingIndicator, modeDescription, uploadStatus, uploadBtn, fileInput;

document.addEventListener('DOMContentLoaded', () => {
    chatArea = document.getElementById('chatArea');
    messageInput = document.getElementById('messageInput');
    sendBtn = document.getElementById('sendBtn');
    loadingIndicator = document.getElementById('loadingIndicator');
    modeDescription = document.getElementById('modeDescription');
    uploadStatus = document.getElementById('uploadStatus');
    uploadBtn = document.getElementById('uploadBtn');
    fileInput = document.getElementById('fileInput');

    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
    });
});

function setMode(newMode) {
    mode = newMode;

    // Update active button
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === newMode);
    });

    // Update description
    modeDescription.textContent = MODE_DESCRIPTIONS[newMode] || '';
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || loading) return;

    // Add user message
    addMessage('user', text);
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Show loading
    loading = true;
    sendBtn.disabled = true;
    loadingIndicator.style.display = 'block';
    scrollToBottom();

    try {
        const resp = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                sessionId: sessionId,
                mode: mode,
            }),
        });

        const data = await resp.json();

        if (!resp.ok) {
            addMessage('assistant', 'Error: ' + (data.error || 'Something went wrong.'), mode);
        } else {
            addMessage('assistant', data.answer, data.mode);
        }
    } catch (err) {
        addMessage('assistant', 'Error: Could not connect to the server.', mode);
    } finally {
        loading = false;
        sendBtn.disabled = false;
        loadingIndicator.style.display = 'none';
        scrollToBottom();
    }
}

function addMessage(role, text, msgMode) {
    // Remove welcome message if present
    const welcome = chatArea.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const wrapper = document.createElement('div');
    wrapper.className = 'message ' + role;

    if (role === 'assistant' && msgMode) {
        const badge = document.createElement('span');
        badge.className = 'mode-badge ' + msgMode;
        badge.textContent = msgMode;
        wrapper.appendChild(badge);
    }

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    if (role === 'assistant') {
        bubble.innerHTML = renderMarkdown(text);
    } else {
        bubble.textContent = text;
    }

    wrapper.appendChild(bubble);
    chatArea.appendChild(wrapper);
    scrollToBottom();
}

function renderMarkdown(text) {
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true,
        });
        return marked.parse(text);
    }
    // Fallback: simple escape + line breaks
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
    });
}

async function uploadFile() {
    const file = fileInput.files[0];
    if (!file) {
        setUploadStatus('Please select a PDF file first.', 'error');
        return;
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
        setUploadStatus('Only PDF files are accepted.', 'error');
        return;
    }

    if (file.size > 25 * 1024 * 1024) {
        setUploadStatus('File exceeds 25MB limit.', 'error');
        return;
    }

    uploading = true;
    uploadBtn.disabled = true;
    setUploadStatus('Uploading and processing...', '');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const resp = await fetch('/api/ingest', {
            method: 'POST',
            body: formData,
        });

        const data = await resp.json();

        if (!resp.ok) {
            setUploadStatus('Error: ' + (data.error || 'Upload failed.'), 'error');
        } else {
            setUploadStatus('PDF uploaded and ingested successfully!', 'success');
            fileInput.value = '';
        }
    } catch (err) {
        setUploadStatus('Error: Could not connect to the server.', 'error');
    } finally {
        uploading = false;
        uploadBtn.disabled = false;
    }
}

function setUploadStatus(text, type) {
    uploadStatus.textContent = text;
    uploadStatus.className = 'upload-status' + (type ? ' ' + type : '');
}
