<script lang="ts">
	import { timerSeconds, timerRunning } from '$lib/stores/room';

	let seconds: number | null = $state(null);
	let running = $state(false);
	let intervalId: ReturnType<typeof setInterval> | null = null;

	$effect(() => {
		const unsub1 = timerSeconds.subscribe((v) => (seconds = v));
		const unsub2 = timerRunning.subscribe((v) => (running = v));
		return () => { unsub1(); unsub2(); };
	});

	$effect(() => {
		if (running && seconds !== null && seconds > 0) {
			intervalId = setInterval(() => {
				timerSeconds.update((v) => {
					if (v !== null && v > 0) return v - 1;
					timerRunning.set(false);
					return 0;
				});
			}, 1000);
		}
		return () => {
			if (intervalId) clearInterval(intervalId);
		};
	});

	function format(s: number): string {
		const m = Math.floor(s / 60);
		const sec = s % 60;
		return `${m}:${sec.toString().padStart(2, '0')}`;
	}
</script>

{#if running && seconds !== null}
	<span class="timer" class:urgent={seconds <= 10}>{format(seconds)}</span>
{/if}

<style>
	.timer {
		font-family: system-ui, -apple-system, sans-serif;
		font-size: 1.25rem;
		font-weight: 700;
		font-variant-numeric: tabular-nums;
	}
	.urgent {
		color: #c00;
	}
</style>
