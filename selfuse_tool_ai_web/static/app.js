// WebSocket 客戶端邏輯
class AIBrowserClient {
    constructor() {
        this.ws = null;
        this.currentConfirmId = null;
        this.connected = false;

        this.elements = {
            taskInput: document.getElementById('task-input'),
            submitBtn: document.getElementById('submit-btn'),
            logs: document.getElementById('logs'),
            connectionStatus: document.getElementById('connection-status'),
            confirmModal: document.getElementById('confirm-modal'),
            confirmMessage: document.getElementById('confirm-message'),
            confirmStep: document.getElementById('confirm-step'),
            confirmYes: document.getElementById('confirm-yes'),
            confirmNo: document.getElementById('confirm-no')
        };

        this.init();
    }

    init() {
        this.connectWebSocket();
        this.bindEvents();
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.connected = true;
            this.updateConnectionStatus(true);
            this.log('已連接到伺服器', 'success');
        };

        this.ws.onclose = () => {
            this.connected = false;
            this.updateConnectionStatus(false);
            this.log('連接已斷開，嘗試重新連接...', 'warning');
            setTimeout(() => this.connectWebSocket(), 3000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.log('連接錯誤', 'error');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
    }

    updateConnectionStatus(connected) {
        if (connected) {
            this.elements.connectionStatus.textContent = '🟢 已連接';
            this.elements.connectionStatus.className = 'status-connected';
            this.elements.submitBtn.disabled = false;
        } else {
            this.elements.connectionStatus.textContent = '⚫ 未連接';
            this.elements.connectionStatus.className = 'status-disconnected';
            this.elements.submitBtn.disabled = true;
        }
    }

    handleMessage(data) {
        switch (data.type) {
            case 'connected':
                this.log(data.message, 'info');
                break;

            case 'log':
                this.log(data.message, data.level);
                break;

            case 'confirm_request':
                this.showConfirmDialog(data);
                break;

            default:
                console.log('Unknown message type:', data);
        }
    }

    log(message, level = 'info') {
        const entry = document.createElement('div');
        entry.className = `log-entry ${level}`;

        const timestamp = new Date().toLocaleTimeString('zh-TW');
        entry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="message">${this.escapeHtml(message)}</span>
        `;

        this.elements.logs.appendChild(entry);
        this.elements.logs.scrollTop = this.elements.logs.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showConfirmDialog(data) {
        this.currentConfirmId = data.confirm_id;

        const step = data.step;
        const actionText = this.getActionText(step.action, step);

        this.elements.confirmMessage.textContent =
            `步驟 ${data.step_index}: ${actionText}`;

        this.elements.confirmStep.textContent =
            JSON.stringify(step, null, 2);

        this.elements.confirmModal.classList.remove('hidden');
    }

    getActionText(action, step) {
        switch (action) {
            case 'navigate':
                return `導航到 ${step.url}`;
            case 'click':
                return `點擊元素 ${step.selector}`;
            case 'type':
                return `在 ${step.selector} 輸入文字`;
            default:
                return action;
        }
    }

    hideConfirmDialog() {
        this.elements.confirmModal.classList.add('hidden');
        this.currentConfirmId = null;
    }

    sendConfirmResponse(approved) {
        if (this.currentConfirmId && this.ws && this.connected) {
            this.ws.send(JSON.stringify({
                type: 'confirm_response',
                confirm_id: this.currentConfirmId,
                approved: approved
            }));

            this.log(
                approved ? '✅ 用戶已批准操作' : '🛑 用戶已拒絕操作',
                approved ? 'success' : 'warning'
            );
        }
        this.hideConfirmDialog();
    }

    bindEvents() {
        // Submit task
        this.elements.submitBtn.addEventListener('click', () => {
            this.submitTask();
        });

        // Submit on Ctrl+Enter
        this.elements.taskInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.submitTask();
            }
        });

        // Confirm dialog buttons
        this.elements.confirmYes.addEventListener('click', () => {
            this.sendConfirmResponse(true);
        });

        this.elements.confirmNo.addEventListener('click', () => {
            this.sendConfirmResponse(false);
        });

        // Close modal on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.elements.confirmModal.classList.contains('hidden')) {
                this.sendConfirmResponse(false);
            }
        });
    }

    async submitTask() {
        const goal = this.elements.taskInput.value.trim();

        if (!goal) {
            this.log('請輸入任務內容', 'warning');
            return;
        }

        if (!this.connected) {
            this.log('未連接到伺服器', 'error');
            return;
        }

        // Disable button while submitting
        this.elements.submitBtn.disabled = true;
        this.elements.submitBtn.querySelector('.btn-text').textContent = '⏳ 提交中...';

        try {
            const response = await fetch('/api/task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ goal })
            });

            if (response.ok) {
                this.log(`任務已提交: ${goal}`, 'success');
                // Clear input after successful submission
                // this.elements.taskInput.value = '';
            } else {
                const error = await response.json();
                this.log(`提交失敗: ${error.error || '未知錯誤'}`, 'error');
            }
        } catch (error) {
            this.log(`提交失敗: ${error.message}`, 'error');
        } finally {
            this.elements.submitBtn.disabled = false;
            this.elements.submitBtn.querySelector('.btn-text').textContent = '▶️ 執行任務';
        }
    }
}

// Initialize client when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.client = new AIBrowserClient();
});
