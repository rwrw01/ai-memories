<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import SkipBack from '@lucide/svelte/icons/skip-back';
	import SkipForward from '@lucide/svelte/icons/skip-forward';
	import Play from '@lucide/svelte/icons/play';
	import Pause from '@lucide/svelte/icons/pause';

	type Props = {
		isPlaying: boolean;
		currentIndex: number;
		total: number;
		playbackRate: number;
		canPrev: boolean;
		canNext: boolean;
		onprev: () => void;
		onnext: () => void;
		ontoggleplay: () => void;
		onratechange: (rate: number) => void;
	};

	let {
		isPlaying,
		currentIndex,
		total,
		playbackRate,
		canPrev,
		canNext,
		onprev,
		onnext,
		ontoggleplay,
		onratechange
	}: Props = $props();

	const rates = [0.75, 1, 1.25, 1.5, 2];
</script>

<div class="flex items-center justify-center gap-3 py-3">
	<Button variant="outline" size="icon" class="size-12 rounded-full" disabled={!canPrev} onclick={onprev} aria-label="Vorige">
		<SkipBack class="size-5" />
	</Button>

	<Button size="icon" class="size-14 rounded-full bg-red-600 hover:bg-red-700" onclick={ontoggleplay} aria-label={isPlaying ? 'Pauzeren' : 'Afspelen'}>
		{#if isPlaying}
			<Pause class="size-7" />
		{:else}
			<Play class="size-7 ml-0.5" />
		{/if}
	</Button>

	<Button variant="outline" size="icon" class="size-12 rounded-full" disabled={!canNext} onclick={onnext} aria-label="Volgende">
		<SkipForward class="size-5" />
	</Button>

	<span class="min-w-14 text-center text-sm text-muted-foreground">{currentIndex + 1} / {total}</span>

	<select
		class="cursor-pointer rounded-md border border-border bg-muted px-2 py-1 text-xs text-foreground"
		value={playbackRate}
		onchange={(e) => onratechange(Number(e.currentTarget.value))}
	>
		{#each rates as r}
			<option value={r}>{r}x</option>
		{/each}
	</select>
</div>
