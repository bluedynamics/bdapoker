<script lang="ts">
	import { goto } from '$app/navigation';

	let deckType = $state('fibonacci');
	let flavor = $state('technical');
	let creating = $state(false);
	let error = $state('');

	const deckTypes = [
		{ value: 'fibonacci', label: 'Fibonacci (0, ½, 1, 2, 3, 5, 8, 13, 20, 40, 100)' },
		{ value: 'tshirt', label: 'T-Shirt (XS, S, M, L, XL, XXL)' },
		{ value: 'powers2', label: 'Powers of 2 (1, 2, 4, 8, 16, 32, 64)' }
	];

	const flavors = [
		{ value: 'technical', label: 'Technical — straightforward complexity' },
		{ value: 'idioms', label: 'Idioms — sayings & metaphors' },
		{ value: 'animals', label: 'Animals — complexity by creature size' },
		{ value: 'software', label: 'Software — developer analogies' }
	];

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
				error = data.detail || 'Failed to create room';
				return;
			}
			const data = await res.json();
			sessionStorage.setItem(`mod_token_${data.room_id}`, data.moderator_token);
			goto(`/room/${data.room_id}`);
		} catch {
			error = 'Network error';
		} finally {
			creating = false;
		}
	}
</script>

<main>
	<h1>Planning Poker</h1>
	<form onsubmit={(e) => { e.preventDefault(); createRoom(); }}>
		<label>
			Deck
			<select bind:value={deckType}>
				{#each deckTypes as dt}
					<option value={dt.value}>{dt.label}</option>
				{/each}
			</select>
		</label>

		<label>
			Descriptions
			<select bind:value={flavor}>
				{#each flavors as f}
					<option value={f.value}>{f.label}</option>
				{/each}
			</select>
		</label>

		<button type="submit" disabled={creating}>
			{creating ? 'Creating...' : 'Create Room'}
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
