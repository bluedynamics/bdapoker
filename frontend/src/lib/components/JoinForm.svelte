<script lang="ts">
	import { sendMessage } from '$lib/stores/websocket';
	import { joined } from '$lib/stores/room';

	let name = $state('');
	let role = $state<'voter' | 'spectator'>('voter');

	function handleJoin() {
		const trimmed = name.trim();
		if (!trimmed) return;
		sendMessage('join', { name: trimmed, role });
		joined.set(true);
	}
</script>

<form class="join-form" onsubmit={(e) => { e.preventDefault(); handleJoin(); }}>
	<label>
		Your name
		<input type="text" bind:value={name} placeholder="Enter your name" autofocus />
	</label>

	<fieldset>
		<legend>Role</legend>
		<label>
			<input type="radio" bind:group={role} value="voter" />
			Voter
		</label>
		<label>
			<input type="radio" bind:group={role} value="spectator" />
			Spectator
		</label>
	</fieldset>

	<button type="submit" disabled={!name.trim()}>Join</button>
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
