<script lang="ts">
	import { locale, type Locale } from '$lib/i18n';

	let current: Locale = $state('en');

	$effect(() => {
		const unsub = locale.subscribe((v) => (current = v));
		return () => unsub();
	});

	function set(lang: Locale) {
		locale.set(lang);
	}
</script>

<div class="lang">
	<button class:active={current === 'en'} onclick={() => set('en')}>EN</button>
	<span>|</span>
	<button class:active={current === 'de'} onclick={() => set('de')}>DE</button>
</div>

<style>
	.lang {
		display: flex;
		align-items: center;
		gap: 0.125rem;
		font-size: 0.75rem;
	}
	button {
		background: none;
		border: none;
		padding: 0.125rem 0.375rem;
		cursor: pointer;
		color: #999;
	}
	button:hover { color: #333; }
	button.active { color: #000; font-weight: 700; }
	span { color: #ccc; }
</style>
