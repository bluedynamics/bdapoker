<script lang="ts">
	import type { CardDef } from '$lib/types';
	import { locale, type Locale } from '$lib/i18n';

	interface Props {
		card: CardDef;
		selected: boolean;
		disabled: boolean;
		onclick: () => void;
	}

	let { card, selected, disabled, onclick }: Props = $props();

	let lang: Locale = $state('en');

	$effect(() => {
		const unsub = locale.subscribe((v) => (lang = v));
		return () => unsub();
	});

	let desc = $derived(card.description[lang]);
</script>

<button
	class="card"
	class:selected
	{disabled}
	{onclick}
	title={desc}
>
	<span class="label">{card.label}</span>
	<span class="info" title={desc}>i</span>
</button>

<style>
	.card {
		display: inline-flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		width: 3.5rem;
		height: 5rem;
		border: 2px solid #999;
		background: #fff;
		cursor: pointer;
		position: relative;
		font-family: system-ui, -apple-system, sans-serif;
		gap: 0.25rem;
	}
	.card:hover:not(:disabled) {
		border-color: #333;
	}
	.card.selected {
		background: #222;
		color: #fff;
		border-color: #222;
	}
	.card:disabled {
		opacity: 0.4;
		cursor: default;
	}
	.label {
		font-size: 1.125rem;
		font-weight: 700;
	}
	.info {
		font-size: 0.625rem;
		width: 1rem;
		height: 1rem;
		border-radius: 50%;
		border: 1px solid currentColor;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		opacity: 0.5;
	}
</style>
