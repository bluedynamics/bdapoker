<script lang="ts">
	import Card from './Card.svelte';
	import { deckCards, currentRound, selectedCard } from '$lib/stores/room';
	import { sendMessage } from '$lib/stores/websocket';
	import type { Participant, CardDef, RoundState } from '$lib/types';

	interface Props {
		participant: Participant | null;
	}

	let { participant }: Props = $props();

	function handleSelect(value: string) {
		selectedCard.set(value);
		sendMessage('vote', { value });
	}

	let cardsValue: CardDef[] = $state([]);
	let roundValue: RoundState | null = $state(null);
	let selectedValue: string | null = $state(null);

	$effect(() => {
		const unsub1 = deckCards.subscribe((v) => (cardsValue = v));
		const unsub2 = currentRound.subscribe((v) => (roundValue = v));
		const unsub3 = selectedCard.subscribe((v) => (selectedValue = v));
		return () => { unsub1(); unsub2(); unsub3(); };
	});

	function checkCanVote(p: Participant | null, r: RoundState | null): boolean {
		return p !== null && p.role !== 'spectator' && r !== null && !r.revealed;
	}

	let canVote = $derived(checkCanVote(participant, roundValue));
</script>

<div class="deck">
	{#each cardsValue as card}
		<Card
			{card}
			selected={selectedValue === card.value}
			disabled={!canVote}
			onclick={() => handleSelect(card.value)}
		/>
	{/each}
</div>

<style>
	.deck {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		justify-content: center;
		padding: 0.5rem 0;
	}
</style>
