<script lang="ts">
	import type { NewsArticle } from '$lib/types/news';
	import { Badge } from '$lib/components/ui/badge';
	import { ScrollArea } from '$lib/components/ui/scroll-area';

	type Props = {
		articles: NewsArticle[];
		currentIndex: number;
		onselect: (index: number) => void;
	};

	let { articles, currentIndex, onselect }: Props = $props();

	const sourceKleuren: Record<string, string> = {
		nos: '#0066cc',
		'nu.nl': '#e67e22',
		tweakers: '#27ae60'
	};
</script>

<ScrollArea class="h-[60vh]">
	<div class="flex flex-col gap-2">
		{#each articles as article, i}
			<button
				class="flex w-full items-center gap-2 rounded-xl border border-border bg-card p-3 text-left text-sm transition-colors hover:border-red-500
					{i === currentIndex ? 'border-red-500 bg-accent' : ''}"
				onclick={() => onselect(i)}
			>
				<span class="size-2 shrink-0 rounded-full {article.audio_ready ? 'bg-green-500' : 'bg-muted-foreground'}"></span>
				<Badge
					class="shrink-0 text-[0.65rem] font-bold uppercase text-white"
					style="background: {sourceKleuren[article.source] ?? '#888'}"
				>
					{article.source}
				</Badge>
				<span class="flex-1 truncate">{article.title}</span>
				{#if article.audio_quality}
					<Badge variant="outline" class="shrink-0 text-[0.6rem]">{article.audio_quality}</Badge>
				{/if}
			</button>
		{/each}

		{#if articles.length === 0}
			<div class="py-8 text-center text-muted-foreground">
				<p>Nog geen nieuwsartikelen vandaag.</p>
				<p class="mt-1 text-sm">De briefing wordt om 04:30 gegenereerd.</p>
			</div>
		{/if}
	</div>
</ScrollArea>
