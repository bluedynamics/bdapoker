<script lang="ts">
	import { stats } from '$lib/stores/room';
	import type { Stats } from '$lib/types';

	let statsValue: Stats | null = $state(null);

	$effect(() => {
		const unsub = stats.subscribe((v) => (statsValue = v));
		return () => unsub();
	});
</script>

{#if statsValue}
	<div class="results">
		<h3>Results</h3>
		<dl>
			<dt>Average</dt>
			<dd>{statsValue.average}</dd>
			<dt>Median</dt>
			<dd>{statsValue.median}</dd>
			<dt>Range</dt>
			<dd>{statsValue.min} – {statsValue.max}</dd>
			{#if statsValue.consensus !== undefined}
				<dt>Consensus</dt>
				<dd>{statsValue.consensus ? 'Yes' : 'No'}</dd>
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
