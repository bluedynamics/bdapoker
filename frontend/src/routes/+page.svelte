<script lang="ts">
	import { goto } from '$app/navigation';
	import { t, translateError, type TranslationKey } from '$lib/i18n';

	let deckType = $state('fibonacci');
	let flavor = $state('technical');
	let creating = $state(false);
	let error = $state('');

	let tr = $state((_key: TranslationKey) => '' as string);

	$effect(() => {
		const unsub = t.subscribe((v) => (tr = v));
		return () => unsub();
	});

	const deckTypes = ['fibonacci', 'tshirt', 'powers2'] as const;
	const flavors = ['technical', 'idioms', 'animals', 'software'] as const;

	async function createRoom() {
		creating = true;
		error = '';
		try {
			const res = await fetch('/api/rooms', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ deck_type: deckType, description_flavor: flavor })
			});
			if (!res.ok) {
				const data = await res.json();
				error = translateError(data.detail || 'Failed to create room');
				return;
			}
			const data = await res.json();
			sessionStorage.setItem(`mod_token_${data.room_id}`, data.moderator_token);
			goto(`/room/${data.room_id}`);
		} catch {
			error = tr('home.error.network');
		} finally {
			creating = false;
		}
	}
</script>

<main>
	<h1>{tr('app.title')}</h1>
	<form onsubmit={(e) => { e.preventDefault(); createRoom(); }}>
		<label>
			{tr('home.deck')}
			<select bind:value={deckType}>
				{#each deckTypes as dk}
					<option value={dk}>{tr(`deck.${dk}`)}</option>
				{/each}
			</select>
		</label>

		<label>
			{tr('home.descriptions')}
			<select bind:value={flavor}>
				{#each flavors as fl}
					<option value={fl}>{tr(`flavor.${fl}`)}</option>
				{/each}
			</select>
		</label>

		<button type="submit" disabled={creating}>
			{creating ? tr('home.creating') : tr('home.createRoom')}
		</button>
	</form>

	{#if error}
		<p class="error">{error}</p>
	{/if}
</main>

<style>
	main {
		max-width: 480px;
		margin: 2rem auto;
		padding: 0 1rem;
		font-family: system-ui, -apple-system, sans-serif;
	}
	h1 {
		font-size: 1.5rem;
		margin-bottom: 1.5rem;
	}
	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	label {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		font-size: 0.875rem;
		font-weight: 600;
	}
	select, button {
		padding: 0.5rem;
		font-size: 0.875rem;
		border: 1px solid #999;
	}
	button {
		cursor: pointer;
		background: #222;
		color: #fff;
		border: none;
		padding: 0.625rem;
	}
	button:disabled {
		opacity: 0.5;
		cursor: default;
	}
	.error {
		color: #c00;
		margin-top: 0.5rem;
	}
</style>
