import { writable, derived } from 'svelte/store';
import type { RoomState, Stats } from '$lib/types';

export const roomState = writable<RoomState | null>(null);
export const stats = writable<Stats | null>(null);
export const timerSeconds = writable<number | null>(null);
export const timerRunning = writable(false);
export const joined = writable(false);
export const selectedCard = writable<string | null>(null);

export const participants = derived(roomState, ($room) =>
	$room ? Object.values($room.participants) : []
);

export const currentRound = derived(roomState, ($room) => $room?.current_round ?? null);

export const deckCards = derived(roomState, ($room) => $room?.deck_cards ?? []);
