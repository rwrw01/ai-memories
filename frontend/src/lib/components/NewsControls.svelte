<script lang="ts">
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

<div class="controls">
	<button class="ctrl-btn" disabled={!canPrev} onclick={onprev} aria-label="Vorige">
		<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
			<path d="M6 6h2v12H6zm3.5 6 8.5 6V6z" />
		</svg>
	</button>

	<button class="ctrl-btn play-btn" onclick={ontoggleplay} aria-label={isPlaying ? 'Pauzeren' : 'Afspelen'}>
		{#if isPlaying}
			<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="currentColor">
				<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
			</svg>
		{:else}
			<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="currentColor">
				<path d="M8 5v14l11-7z" />
			</svg>
		{/if}
	</button>

	<button class="ctrl-btn" disabled={!canNext} onclick={onnext} aria-label="Volgende">
		<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
			<path d="m6 18 8.5-6L6 6v12zM16 6v12h2V6h-2z" />
		</svg>
	</button>

	<span class="counter">{currentIndex + 1} / {total}</span>

	<select
		class="rate-select"
		value={playbackRate}
		onchange={(e) => onratechange(Number(e.currentTarget.value))}
	>
		{#each rates as r}
			<option value={r}>{r}x</option>
		{/each}
	</select>
</div>

<style>
	.controls {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
		padding: 0.75rem 0;
	}

	.ctrl-btn {
		background: none;
		border: 1px solid #0f3460;
		border-radius: 50%;
		color: #eaeaea;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 48px;
		height: 48px;
		transition: background 0.15s, opacity 0.15s;
	}

	.ctrl-btn:hover:not(:disabled) {
		background: #0f3460;
	}

	.ctrl-btn:disabled {
		opacity: 0.3;
		cursor: not-allowed;
	}

	.play-btn {
		width: 60px;
		height: 60px;
		background: linear-gradient(135deg, #e94560, #c23152);
		border: none;
	}

	.play-btn:hover {
		opacity: 0.9;
	}

	.counter {
		font-size: 0.8rem;
		color: #888;
		min-width: 3.5rem;
		text-align: center;
	}

	.rate-select {
		background: #0f3460;
		border: 1px solid #1a4080;
		border-radius: 0.375rem;
		color: #eaeaea;
		font-size: 0.75rem;
		padding: 0.25rem 0.5rem;
		cursor: pointer;
	}
</style>
