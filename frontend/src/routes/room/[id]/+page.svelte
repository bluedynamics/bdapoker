<script lang="ts">
	import { page } from '$app/state';
	import { onMount, onDestroy } from 'svelte';
	import { connectWs, disconnectWs, onMessage, participantId, isModerator } from '$lib/stores/websocket';
	import { roomState, stats, joined, selectedCard, timerSeconds, timerRunning } from '$lib/stores/room';
	import type { RoomState, WsMessage } from '$lib/types';
	import JoinForm from '$lib/components/JoinForm.svelte';
	import CardDeck from '$lib/components/CardDeck.svelte';
	import ParticipantList from '$lib/components/ParticipantList.svelte';
	import VoteResults from '$lib/components/VoteResults.svelte';
	import StoryField from '$lib/components/StoryField.svelte';
	import ModeratorControls from '$lib/components/ModeratorControls.svelte';
	import Timer from '$lib/components/Timer.svelte';

	let roomId = $derived(page.params.id);
	let roomExists = $state<boolean | null>(null);
	let error = $state('');

	let isJoined = $state(false);
	let isMod = $state(false);
	let myId = $state<string | null>(null);
	let room = $state<RoomState | null>(null);

	$effect(() => {
		const unsub1 = joined.subscribe((v) => (isJoined = v));
		const unsub2 = isModerator.subscribe((v) => (isMod = v));
		const unsub3 = participantId.subscribe((v) => (myId = v));
		const unsub4 = roomState.subscribe((v) => (room = v));
		return () => { unsub1(); unsub2(); unsub3(); unsub4(); };
	});

	let myParticipant = $derived(
		room && myId ? room.participants[myId] ?? null : null
	);

	let cleanups: Array<() => void> = [];

	onMount(async () => {
		// Check if room exists
		try {
			const res = await fetch(`/api/rooms/${roomId}`);
			if (!res.ok) {
				roomExists = false;
				error = 'Room not found';
				return;
			}
			roomExists = true;
		} catch {
			roomExists = false;
			error = 'Network error';
			return;
		}

		// Connect WebSocket
		const id = roomId;
		if (!id) return;
		const token = sessionStorage.getItem(`mod_token_${id}`);
		connectWs(id, token);

		cleanups.push(onMessage((msg: WsMessage) => {
			if (msg.type === 'room_state') {
				roomState.set(msg.payload as unknown as RoomState);
				if ('stats' in msg.payload) {
					stats.set(msg.payload.stats as any);
				} else {
					stats.set(null);
				}
			} else if (msg.type === 'timer_start') {
				timerSeconds.set((msg.payload as any).seconds);
				timerRunning.set(true);
			} else if (msg.type === 'timer_stop') {
				timerRunning.set(false);
			} else if (msg.type === 'error') {
				error = (msg.payload as any).message;
				setTimeout(() => (error = ''), 3000);
			}
		}));

		// Reset selected card when round changes
		cleanups.push(roomState.subscribe((r) => {
			if (r?.current_round && !r.current_round.revealed) {
				if (myId && !r.current_round.votes[myId]) {
					selectedCard.set(null);
				}
			}
		}));
	});

	onDestroy(() => {
		cleanups.forEach((fn) => fn());
		disconnectWs();
	});

	// Share link
	let shareUrl = $derived(typeof window !== 'undefined' ? window.location.href : '');
</script>

<main>
	{#if roomExists === null}
		<p>Loading...</p>
	{:else if !roomExists}
		<p class="error">{error || 'Room not found'}</p>
	{:else if !isJoined}
		<h2>Join Room <code>{roomId}</code></h2>
		<JoinForm />
	{:else}
		<header>
			<div class="room-info">
				Room: <code>{roomId}</code>
				<button class="copy-btn" onclick={() => navigator.clipboard.writeText(shareUrl)}>
					Copy link
				</button>
			</div>
			<Timer />
			{#if isMod}
				<ModeratorControls />
			{/if}
		</header>

		<StoryField />

		<div class="game-area">
			<div class="left">
				<ParticipantList />
				<VoteResults />
			</div>
			<div class="right">
				<CardDeck participant={myParticipant} />
			</div>
		</div>

		{#if error}
			<p class="error">{error}</p>
		{/if}
	{/if}
</main>

<style>
	main {
		max-width: 960px;
		margin: 1rem auto;
		padding: 0 1rem;
		font-family: system-ui, -apple-system, sans-serif;
	}
	header {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.75rem;
		padding: 0.5rem 0;
		border-bottom: 1px solid #eee;
	}
	.room-info {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.8125rem;
	}
	.room-info code {
		background: #f0f0f0;
		padding: 0.125rem 0.375rem;
	}
	.copy-btn {
		font-size: 0.75rem;
		padding: 0.25rem 0.5rem;
		cursor: pointer;
		background: none;
		border: 1px solid #999;
		color: #333;
	}
	.game-area {
		display: grid;
		grid-template-columns: 1fr 2fr;
		gap: 1.5rem;
		margin-top: 1rem;
	}
	h2 {
		font-size: 1.25rem;
	}
	.error {
		color: #c00;
		font-size: 0.8125rem;
	}

	@media (max-width: 640px) {
		.game-area {
			grid-template-columns: 1fr;
		}
	}
</style>
