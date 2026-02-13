<script lang="ts">
	import { stats } from '$lib/stores/room';
	import type { Stats } from '$lib/types';
	import { t, type TranslationKey } from '$lib/i18n';

	let statsValue: Stats | null = $state(null);

	let tr = $state((_key: TranslationKey) => '' as string);

	$effect(() => {
		const unsub = t.subscribe((v) => (tr = v));
		return () => unsub();
	});

	$effect(() => {
		const unsub = stats.subscribe((v) => (statsValue = v));
		return () => unsub();
	});
</script>

{#if statsValue}
	<div class="results">
		<h3>{tr('results.title')}</h3>
		<dl>
			<dt>{tr('results.average')}</dt>
			<dd>{statsValue.average}</dd>
			<dt>{tr('results.median')}</dt>
			<dd>{statsValue.median}</dd>
			<dt>{tr('results.range')}</dt>
			<dd>{statsValue.min} – {statsValue.max}</dd>
			{#if statsValue.consensus !== undefined}
				<dt>{tr('results.consensus')}</dt>
				<dd>{statsValue.consensus ? tr('results.yes') : tr('results.no')}</dd>
			{/if}
		</dl>
	</div>
{/if}

<style>
	.results {
		font-family: system-ui, -apple-system, sans-serif;
	}
	h3 {
		font-size: 0.875rem;
		margin: 0 0 0.5rem;
	}
	dl {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 0.125rem 0.75rem;
		font-size: 0.8125rem;
		margin: 0;
	}
	dt {
		font-weight: 600;
	}
	dd {
		margin: 0;
	}
</style>
