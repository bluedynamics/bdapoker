import { writable } from 'svelte/store';
import type { WsMessage } from '$lib/types';

export const connected = writable(false);
export const participantId = writable<string | null>(null);
export const isModerator = writable(false);

let ws: WebSocket | null = null;
let messageHandlers: Array<(msg: WsMessage) => void> = [];

export function onMessage(handler: (msg: WsMessage) => void): () => void {
	messageHandlers.push(handler);
	return () => {
		messageHandlers = messageHandlers.filter((h) => h !== handler);
	};
}

export function connectWs(
	roomId: string,
	token?: string | null,
	reconnectId?: string | null,
	reconnectToken?: string | null
): void {
	if (ws) {
		ws.close();
	}

	const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
	const params = new URLSearchParams();
	if (token) params.set('token', token);
	if (reconnectId) params.set('reconnect_id', reconnectId);
	if (reconnectToken) params.set('reconnect_token', reconnectToken);
	const qs = params.toString();
	const url = `${protocol}//${window.location.host}/api/rooms/${roomId}/ws${qs ? '?' + qs : ''}`;

	ws = new WebSocket(url);

	ws.onopen = () => {
		connected.set(true);
	};

	ws.onclose = () => {
		connected.set(false);
	};

	ws.onmessage = (event) => {
		try {
			const msg: WsMessage = JSON.parse(event.data);
			if (msg.type === 'welcome') {
				participantId.set(msg.payload.participant_id as string);
				isModerator.set(msg.payload.is_moderator as boolean);
			}
			for (const handler of messageHandlers) {
				handler(msg);
			}
		} catch {
			// ignore malformed messages
		}
	};
}

export function sendMessage(type: string, payload: Record<string, unknown> = {}): void {
	if (ws && ws.readyState === WebSocket.OPEN) {
		ws.send(JSON.stringify({ type, payload }));
	}
}

export function disconnectWs(): void {
	if (ws) {
		ws.close();
		ws = null;
	}
}
