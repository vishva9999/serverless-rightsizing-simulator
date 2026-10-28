type MessageListener = (data: any) => void;
type StatusListener = (status: 'CONNECTED' | 'CONNECTING' | 'DISCONNECTED') => void;

class WebSocketClient {
  private socket: WebSocket | null = null;
  private messageListeners: Set<MessageListener> = new Set();
  private statusListeners: Set<StatusListener> = new Set();
  private reconnectTimer: any = null;
  private isExplicitlyClosed = false;

  public connect(url: string = 'ws://localhost:8000/ws') {
    this.isExplicitlyClosed = false;
    this.notifyStatus('CONNECTING');

    try {
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        this.notifyStatus('CONNECTED');
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.messageListeners.forEach((listener) => listener(parsed));
        } catch (e) {
          this.messageListeners.forEach((listener) => listener(event.data));
        }
      };

      this.socket.onclose = () => {
        this.notifyStatus('DISCONNECTED');
        if (!this.isExplicitlyClosed) {
          this.reconnectTimer = setTimeout(() => this.connect(url), 4000);
        }
      };

      this.socket.onerror = () => {
        this.notifyStatus('DISCONNECTED');
      };
    } catch {
      this.notifyStatus('DISCONNECTED');
    }
  }

  public disconnect() {
    this.isExplicitlyClosed = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.notifyStatus('DISCONNECTED');
  }

  public send(data: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(typeof data === 'string' ? data : JSON.stringify(data));
    }
  }

  public onMessage(listener: MessageListener): () => void {
    this.messageListeners.add(listener);
    return () => {
      this.messageListeners.delete(listener);
    };
  }

  public onStatus(listener: StatusListener): () => void {
    this.statusListeners.add(listener);
    return () => {
      this.statusListeners.delete(listener);
    };
  }

  private notifyStatus(status: 'CONNECTED' | 'CONNECTING' | 'DISCONNECTED') {
    this.statusListeners.forEach((listener) => listener(status));
  }
}

export const wsClient = new WebSocketClient();
