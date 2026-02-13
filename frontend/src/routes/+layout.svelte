<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="app">
	<div class="lang-pos">
		<LanguageSwitcher />
	</div>
	{@render children()}
</div>

<style>
	.app { position: relative; }
	.lang-pos {
		position: absolute;
		top: 0.75rem;
		right: 1rem;
		z-index: 100;
	}
</style>
