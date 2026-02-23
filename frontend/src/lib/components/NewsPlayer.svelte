<script lang="ts">
	import type { NewsArticle } from '$lib/types/news';
	import NewsControls from './NewsControls.svelte';

	type Props = {
		articles: NewsArticle[];
	};

	let { articles }: Props = $props();
	let currentIndex = $state(0);
	let isPlaying = $state(false);
	let playbackRate = $state(1);
	let audioEl = $state<HTMLAudioElement | null>(null);

	// Touch swipe tracking
	let touchStartX = 0;

	let currentArticle = $derived(articles[currentIndex]);
	let audioSrc = $derived(
		currentArticle?.audio_ready ? `/api/news/${currentArticle.id}/audio` : ''
	);

	const sourceKleuren: Record<string, string> = {
		nos: '#0066cc',
		'nu.nl': '#e67e22',
		tweakers: '#27ae60'
	};

	function next() {
		if (currentIndex < articles.length - 1) {
			currentIndex++;
			isPlaying = false;
		}
	}

	function prev() {
		if (currentIndex > 0) {
			currentIndex--;
			isPlaying = false;
		}
	}

	function togglePlay() {
		if (!audioEl || !audioSrc) return;
		if (isPlaying) {
			audioEl.pause();
			isPlaying = false;
		} else {
			audioEl.play();
			isPlaying = true;
		}
	}

	function handleRateChange(rate: number) {
		playbackRate = rate;
		if (audioEl) audioEl.playbackRate = rate;
	}

	function handleEnded() {
		isPlaying = false;
		if (currentIndex < articles.length - 1) {
			currentIndex++;
			// Auto-play next after a short delay
			setTimeout(() => {
				if (audioEl && articles[currentIndex]?.audio_ready) {
					audioEl.play();
					isPlaying = true;
				}
			}, 500);
		}
	}

	function handleTouchStart(e: TouchEvent) {
		touchStartX = e.touches[0].clientX;
	}

	function handleTouchEnd(e: TouchEvent) {
		const dx = e.changedTouches[0].clientX - touchStartX;
		if (Math.abs(dx) > 60) {
			if (dx < 0) next();
			else prev();
		}
	}
</script>

<div
	class="player"
	ontouchstart={handleTouchStart}
	ontouchend={handleTouchEnd}
	role="region"
	aria-label="Nieuwsspeler"
>
	{#if currentArticle}
		<div class="artikel-kaart">
			<div class="kaart-header">
				<span
					class="bron-badge"
					style="background: {sourceKleuren[currentArticle.source] ?? '#888'}"
				>
					{currentArticle.source}
				</span>
				{#if currentArticle.audio_quality}
					<span class="kwaliteit">{currentArticle.audio_quality}</span>
				{/if}
			</div>

			<h2 class="artikel-titel">{currentArticle.title}</h2>

			{#if currentArticle.description}
				<p class="artikel-beschrijving">{currentArticle.description}</p>
			{/if}

			{#if audioSrc}
				<!-- svelte-ignore a11y_media_has_caption -->
				<audio
					bind:this={audioEl}
					src={audioSrc}
					{playbackRate}
					onended={handleEnded}
					onpause={() => (isPlaying = false)}
					onplay={() => (isPlaying = true)}
					controls
					class="audio-speler"
				></audio>
			{:else}
				<div class="geen-audio">
					<p>Audio niet beschikbaar</p>
				</div>
			{/if}
		</div>

		<NewsControls
			{isPlaying}
			{currentIndex}
			total={articles.length}
			{playbackRate}
			canPrev={currentIndex > 0}
			canNext={currentIndex < articles.length - 1}
			onprev={prev}
			onnext={next}
			ontoggleplay={togglePlay}
			onratechange={handleRateChange}
		/>

		<p class="swipe-hint">Swipe om te navigeren</p>
	{:else}
		<div class="leeg">
			<p>Geen nieuwsartikelen beschikbaar.</p>
		</div>
	{/if}
</div>

<style>
	.player {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		user-select: none;
		-webkit-user-select: none;
	}

	.artikel-kaart {
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 1rem;
		padding: 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.kaart-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.bron-badge {
		font-size: 0.7rem;
		font-weight: 700;
		text-transform: uppercase;
		padding: 0.2rem 0.5rem;
		border-radius: 0.25rem;
		color: white;
		letter-spacing: 0.03em;
	}

	.kwaliteit {
		font-size: 0.65rem;
		color: #888;
		background: #0f3460;
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
	}

	.artikel-titel {
		font-size: 1.05rem;
		font-weight: 600;
		color: #eaeaea;
		line-height: 1.4;
		margin: 0;
	}

	.artikel-beschrijving {
		font-size: 0.875rem;
		color: #bbb;
		line-height: 1.6;
		margin: 0;
	}

	.audio-speler {
		width: 100%;
		border-radius: 0.5rem;
		margin-top: 0.25rem;
	}

	.geen-audio {
		padding: 1rem;
		text-align: center;
		color: #888;
		font-size: 0.85rem;
		background: #0f3460;
		border-radius: 0.5rem;
	}

	.geen-audio p {
		margin: 0;
	}

	.swipe-hint {
		text-align: center;
		font-size: 0.7rem;
		color: #555;
		margin: 0;
	}

	.leeg {
		text-align: center;
		padding: 3rem 1rem;
		color: #888;
	}

	.leeg p {
		margin: 0;
	}
</style>
