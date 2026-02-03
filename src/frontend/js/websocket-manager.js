class WebSocketManager {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1s
        this.isConnected = false;

        // Bind methods
        this.connect = this.connect.bind(this);
        this.onOpen = this.onOpen.bind(this);
        this.onClose = this.onClose.bind(this);
        this.onError = this.onError.bind(this);
        this.onMessage = this.onMessage.bind(this);
    }

    connect() {
        if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host; // e.g., localhost:8000
        // Adjust port if running on different port for API (e.g. if frontend is served statically on 80 and api on 8000)
        // For Docker setup usually everything is behind Nginx on port 80/443, so window.location.host is correct.
        // But if running locally separately:
        // const wsUrl = `ws://localhost:8000/ws/dashboard`; 

        let wsUrl = `${protocol}//${host}/api/ws/dashboard`;

        // If we are in dev mode and frontend is just valid html file opened or served differently
        if (window.location.port !== '8000') {
            // Assuming API is on 8000 for local dev
            wsUrl = `ws://localhost:8000/ws/dashboard`;
        } else {
            // Production/Docker behind nginx usually proxies /api/ws/dashboard -> /ws/dashboard or similar
            // Based on Nginx config, usually passing through.
            // Let's assume the router is mounted at /api/v1/websocket or similar? 
            // In app.py: app.include_router(websocket.router, tags=["WebSocket"])
            // The route is @router.websocket("/ws/dashboard")
            // So exact path is /ws/dashboard relative to app root.
            wsUrl = `ws://localhost:8000/ws/dashboard`;
        }

        console.log(`🔌 Connecting to WebSocket at ${wsUrl}...`);

        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = this.onOpen;
        this.socket.onclose = this.onClose;
        this.socket.onerror = this.onError;
        this.socket.onmessage = this.onMessage;
    }

    onOpen(event) {
        console.log('✅ WebSocket Connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.updateStatus(true);

        // Dispatch connection event
        window.dispatchEvent(new CustomEvent('ws-connected'));
    }

    onClose(event) {
        console.log('❌ WebSocket Disconnected');
        this.isConnected = false;
        this.updateStatus(false);
        this.handleReconnect();
    }

    onError(event) {
        console.error('⚠️ WebSocket Error:', event);
    }

    onMessage(event) {
        try {
            const message = JSON.parse(event.data);
            console.log('📩 received:', message);

            // Dispatch event specific to the message type
            if (message.event) {
                window.dispatchEvent(new CustomEvent(message.event, { detail: message.data }));
            }
        } catch (e) {
            console.error('Error parsing WebSocket message:', e);
        }
    }

    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Reconnecting in ${this.reconnectDelay}ms... (Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.connect();
                this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000); // Exponential backoff max 30s
            }, this.reconnectDelay);
        } else {
            console.error('❌ Max reconnect attempts reached');
        }
    }

    updateStatus(connected) {
        const statusEl = document.getElementById('ws-status');
        if (statusEl) {
            statusEl.className = connected ? 'status-connected' : 'status-disconnected';
            statusEl.innerText = connected ? '🟢 LIVE' : '🔴 OFFLINE';
            statusEl.title = connected ? 'Real-time updates active' : 'Connection lost';
        }
    }
}

// Export singleton
const wsManager = new WebSocketManager();
window.wsManager = wsManager; // Make global
