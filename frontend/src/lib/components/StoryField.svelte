<script lang="ts">
	import { currentRound } from '$lib/stores/room';
	import type { RoundState } from '$lib/types';
	import { t, type TranslationKey } from '$lib/i18n';

	let round: RoundState | null = $state(null);

	let tr = $state((_key: TranslationKey) => '' as string);

	$effect(() => {
		const unsub = t.subscribe((v) => (tr = v));
		return () => unsub();
	});

	$effect(() => {
		const unsub = currentRound.subscribe((v) => (round = v));
		return () => unsub();
	});
</script>

<div class="story">
	{#if round}
		<span class="label">{tr('story.label')}</span>
		<span class="text">{round.story || tr('story.noStory')}</span>
		{#if round.story_link}
			<a href={round.story_link} target="_blank" rel="noopener">{tr('story.link')}</a>
		{/if}
		<span class="round">{tr('story.round')} {round.round_number}</span>
	{:else}
		<span class="text">{tr('story.waiting')}</span>
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
