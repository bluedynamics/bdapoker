<script lang="ts">
	import { participants, currentRound } from '$lib/stores/room';
	import type { Participant, RoundState } from '$lib/types';

	let participantList: Participant[] = $state([]);
	let round: RoundState | null = $state(null);

	$effect(() => {
		const unsub1 = participants.subscribe((v) => (participantList = v));
		const unsub2 = currentRound.subscribe((v) => (round = v));
		return () => { unsub1(); unsub2(); };
	});

	function voteStatus(pid: string): string {
		if (!round) return '';
		const vote = round.votes[pid];
		if (!vote) return '';
		if (round.revealed && vote.value) return vote.value;
		if (vote.has_voted || vote.value) return '\u2713';
		return '';
	}
</script>

<div class="participants">
	<h3>Participants</h3>
	<table>
		<thead>
			<tr>
				<th>Name</th>
				<th>Role</th>
				<th>Vote</th>
			</tr>
		</thead>
		<tbody>
			{#each participantList as p}
				<tr class:disconnected={!p.connected}>
					<td>{p.name}</td>
					<td class="role">{p.role}</td>
					<td class="vote">{voteStatus(p.id)}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.participants {
		font-family: system-ui, -apple-system, sans-serif;
	}
	h3 {
		font-size: 0.875rem;
		margin: 0 0 0.5rem;
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.8125rem;
	}
	th, td {
		text-align: left;
		padding: 0.25rem 0.5rem;
		border-bottom: 1px solid #eee;
	}
	th {
		font-weight: 600;
		border-bottom: 2px solid #ccc;
	}
	.role {
		color: #666;
	}
	.vote {
		text-align: center;
		font-weight: 700;
	}
	.disconnected {
		opacity: 0.4;
	}
</style>
