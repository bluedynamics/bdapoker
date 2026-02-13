<script lang="ts">
	import { page } from '$app/state';
	import { onMount, onDestroy } from 'svelte';
	import { connectWs, disconnectWs, onMessage, participantId, isModerator } from '$lib/stores/websocket';
	import { roomState, stats, joined, selectedCard, timerSeconds, timerRunning } from '$lib/stores/room';
	import type { RoomState, WsMessage } from '$lib/types';
	import { t, translateError, type TranslationKey } from '$lib/i18n';
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

	let tr = $state((_key: TranslationKey) => '' as string);

	$effect(() => {
		const unsub = t.subscribe((v) => (tr = v));
		return () => unsub();
	});

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
				error = tr('room.notFound');
				return;
			}
			roomExists = true;
		} catch {
			roomExists = false;
			error = tr('room.networkError');
			return;
		}

		// Connect WebSocket
		const id = roomId;
		if (!id) return;
		const token = localStorage.getItem(`mod_token_${id}`);
		const reconId = localStorage.getItem(`reconnect_id_${id}`);
		const reconToken = localStorage.getItem(`reconnect_token_${id}`);
		connectWs(id, token, reconId, reconToken);

		cleanups.push(onMessage((msg: WsMessage) => {
			if (msg.type === 'room_state') {
				roomState.set(msg.payload as unknown as RoomState);
				if ('stats' in msg.payload) {
					stats.set(msg.payload.stats as any);
				} else {
					stats.set(null);
				}
			} else if (msg.type === 'welcome') {
				if ((msg.payload as any).reconnected) {
					joined.set(true);
				}
				// Store reconnect_token from welcome (for reconnected users)
				if ((msg.payload as any).reconnect_token) {
					localStorage.setItem(`reconnect_id_${id}`, (msg.payload as any).participant_id);
					localStorage.setItem(`reconnect_token_${id}`, (msg.payload as any).reconnect_token);
				}
			} else if (msg.type === 'reconnect_token') {
				// Store reconnect credentials for future reconnection
				const rToken = (msg.payload as any).reconnect_token;
				if (rToken) {
					localStorage.setItem(`reconnect_token_${id}`, rToken);
				}
				// Store participant_id (set by welcome message earlier)
				let currentPid: string | null = null;
				const unsub = participantId.subscribe((v) => (currentPid = v));
				unsub();
				if (currentPid) {
					localStorage.setItem(`reconnect_id_${id}`, currentPid);
				}
			} else if (msg.type === 'timer_start') {
				timerSeconds.set((msg.payload as any).seconds);
				timerRunning.set(true);
			} else if (msg.type === 'timer_stop') {
				timerRunning.set(false);
			} else if (msg.type === 'error') {
				error = translateError((msg.payload as any).message);
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
		<p>{tr('room.loading')}</p>
	{:else if !roomExists}
		<p class="error">{error || tr('room.notFound')}</p>
	{:else if !isJoined}
		<h2>{tr('join.title')} <code>{roomId}</code></h2>
		<JoinForm />
	{:else}
		<header>
			<div class="room-info">
				{tr('room.label')} <code>{roomId}</code>
				<button class="copy-btn" onclick={() => navigator.clipboard.writeText(shareUrl)}>
					{tr('room.copyLink')}
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
