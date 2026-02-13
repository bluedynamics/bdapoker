<script lang="ts">
	import { sendMessage } from '$lib/stores/websocket';
	import { currentRound } from '$lib/stores/room';
	import type { RoundState } from '$lib/types';

	let round: RoundState | null = $state(null);
	let newStory = $state('');
	let newStoryLink = $state('');
	let showNewStoryForm = $state(false);

	$effect(() => {
		const unsub = currentRound.subscribe((v) => (round = v));
		return () => unsub();
	});

	function reveal() {
		sendMessage('reveal');
	}

	function resetRound() {
		sendMessage('reset_round');
	}

	function startNewRound() {
		sendMessage('new_round', {
			story: newStory.trim(),
			story_link: newStoryLink.trim() || null
		});
		newStory = '';
		newStoryLink = '';
		showNewStoryForm = false;
	}

	function startTimer(seconds: number) {
		sendMessage('start_timer', { seconds });
	}

	function stopTimer() {
		sendMessage('stop_timer');
	}
</script>

<div class="controls">
	<div class="buttons">
		{#if round && !round.revealed}
			<button onclick={reveal}>Reveal</button>
		{/if}
		{#if round}
			<button onclick={resetRound}>Re-vote</button>
		{/if}
		<button onclick={() => (showNewStoryForm = !showNewStoryForm)}>
			{showNewStoryForm ? 'Cancel' : 'New Story'}
		</button>
		{#if round && !round.revealed}
			<button onclick={() => startTimer(60)}>Timer 60s</button>
			<button onclick={() => startTimer(120)}>Timer 120s</button>
			<button onclick={stopTimer}>Stop Timer</button>
		{/if}
	</div>

	{#if showNewStoryForm}
		<form class="new-story" onsubmit={(e) => { e.preventDefault(); startNewRound(); }}>
			<input type="text" bind:value={newStory} placeholder="Story description" />
			<input type="text" bind:value={newStoryLink} placeholder="Link (optional)" />
			<button type="submit">Start Round</button>
		</form>
	{/if}
</div>

<style>
	.controls {
		font-family: system-ui, -apple-system, sans-serif;
		font-size: 0.8125rem;
	}
	.buttons {
		display: flex;
		flex-wrap: wrap;
		gap: 0.375rem;
	}
	button {
		padding: 0.375rem 0.75rem;
		font-size: 0.8125rem;
		cursor: pointer;
		background: #222;
		color: #fff;
		border: none;
	}
	.new-story {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
		margin-top: 0.5rem;
	}
	.new-story input {
		padding: 0.375rem;
		font-size: 0.8125rem;
		border: 1px solid #999;
	}
	.new-story button {
		align-self: flex-start;
	}
</style>
