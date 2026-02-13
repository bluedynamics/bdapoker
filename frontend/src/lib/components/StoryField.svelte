<script lang="ts">
	import { currentRound } from '$lib/stores/room';
	import type { RoundState } from '$lib/types';

	let round: RoundState | null = $state(null);

	$effect(() => {
		const unsub = currentRound.subscribe((v) => (round = v));
		return () => unsub();
	});
</script>

<div class="story">
	{#if round}
		<span class="label">Story:</span>
		<span class="text">{round.story || '(no story set)'}</span>
		{#if round.story_link}
			<a href={round.story_link} target="_blank" rel="noopener">[link]</a>
		{/if}
		<span class="round">Round {round.round_number}</span>
	{:else}
		<span class="text">Waiting for moderator to start a round...</span>
	{/if}
</div>

<style>
	.story {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		font-family: system-ui, -apple-system, sans-serif;
		font-size: 0.875rem;
		padding: 0.5rem 0;
		border-bottom: 1px solid #eee;
	}
	.label {
		font-weight: 600;
	}
	.text {
		color: #333;
	}
	.round {
		margin-left: auto;
		color: #666;
		font-size: 0.75rem;
	}
	a {
		color: #333;
		font-size: 0.75rem;
	}
</style>
