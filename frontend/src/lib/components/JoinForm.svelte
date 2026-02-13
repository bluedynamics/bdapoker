<script lang="ts">
	import { sendMessage } from '$lib/stores/websocket';
	import { joined } from '$lib/stores/room';
	import { t, type TranslationKey } from '$lib/i18n';

	let name = $state(localStorage.getItem('participant_name') ?? '');
	let role = $state<'voter' | 'spectator'>('voter');

	let tr = $state((_key: TranslationKey) => '' as string);

	$effect(() => {
		const unsub = t.subscribe((v) => (tr = v));
		return () => unsub();
	});

	function handleJoin() {
		const trimmed = name.trim();
		if (!trimmed) return;
		sendMessage('join', { name: trimmed, role });
		localStorage.setItem('participant_name', trimmed);
		joined.set(true);
	}
</script>

<form class="join-form" onsubmit={(e) => { e.preventDefault(); handleJoin(); }}>
	<label>
		{tr('join.yourName')}
		<input type="text" bind:value={name} placeholder={tr('join.placeholder')} autofocus />
	</label>

	<fieldset>
		<legend>{tr('join.role')}</legend>
		<label>
			<input type="radio" bind:group={role} value="voter" />
			{tr('join.voter')}
		</label>
		<label>
			<input type="radio" bind:group={role} value="spectator" />
			{tr('join.spectator')}
		</label>
	</fieldset>

	<button type="submit" disabled={!name.trim()}>{tr('join.button')}</button>
</form>

<style>
	.join-form {
		max-width: 320px;
		margin: 2rem auto;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		font-family: system-ui, -apple-system, sans-serif;
	}
	label {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		font-size: 0.875rem;
		font-weight: 600;
	}
	fieldset {
		border: 1px solid #ccc;
		padding: 0.5rem;
	}
	fieldset label {
		flex-direction: row;
		align-items: center;
		gap: 0.5rem;
		font-weight: normal;
	}
	legend {
		font-size: 0.875rem;
		font-weight: 600;
	}
	input[type='text'] {
		padding: 0.5rem;
		font-size: 0.875rem;
		border: 1px solid #999;
	}
	button {
		padding: 0.625rem;
		font-size: 0.875rem;
		cursor: pointer;
		background: #222;
		color: #fff;
		border: none;
	}
	button:disabled {
		opacity: 0.5;
		cursor: default;
	}
</style>
