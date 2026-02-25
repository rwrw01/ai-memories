<script lang="ts">
	import type { NewsArticle } from '$lib/types/news';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import NewsControls from './NewsControls.svelte';

	type Props = {
		articles: NewsArticle[];
	};

	let { articles }: Props = $props();
	let currentIndex = $state(0);
	let isPlaying = $state(false);
	let playbackRate = $state(1);
	let audioEl = $state<HTMLAudioElement | null>(null);

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
	class="flex select-none flex-col gap-3"
	ontouchstart={handleTouchStart}
	ontouchend={handleTouchEnd}
	role="region"
	aria-label="Nieuwsspeler"
>
	{#if currentArticle}
		<Card.Root>
			<Card.Content class="flex flex-col gap-3 p-5">
				<div class="flex items-center justify-between">
					<Badge
						class="text-[0.7rem] font-bold uppercase tracking-wide text-white"
						style="background: {sourceKleuren[currentArticle.source] ?? '#888'}"
					>
						{currentArticle.source}
					</Badge>
					{#if currentArticle.audio_quality}
						<Badge variant="outline" class="text-[0.65rem]">{currentArticle.audio_quality}</Badge>
					{/if}
				</div>

				<h2 class="text-[1.05rem] font-semibold leading-snug">{currentArticle.title}</h2>

				{#if currentArticle.description}
					<p class="text-sm leading-relaxed text-muted-foreground">{currentArticle.description}</p>
				{/if}

				{#if audioSrc}
					<!-- svelte-ignore a11y_media_has_caption -->
					<audio
						bind:this={audioEl}
						src={audioSrc}
						onended={handleEnded}
						onpause={() => (isPlaying = false)}
						onplay={() => { isPlaying = true; if (audioEl) audioEl.playbackRate = playbackRate; }}
						controls
						class="mt-1 w-full rounded-lg"
					></audio>
				{:else}
					<div class="rounded-lg bg-muted p-4 text-center text-sm text-muted-foreground">
						Audio niet beschikbaar
					</div>
				{/if}
			</Card.Content>
		</Card.Root>

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

		<p class="text-center text-[0.7rem] text-muted-foreground/40">Swipe om te navigeren</p>
	{:else}
		<div class="py-12 text-center text-muted-foreground">
			<p>Geen nieuwsartikelen beschikbaar.</p>
		</div>
	{/if}
</div>
