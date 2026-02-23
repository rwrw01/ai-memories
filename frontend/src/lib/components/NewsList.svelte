<script lang="ts">
	import type { NewsArticle } from '$lib/types/news';

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

	function bronKleur(source: string): string {
		return sourceKleuren[source] ?? '#888';
	}
</script>

<div class="lijst">
	{#each articles as article, i}
		<button
			class="artikel-item"
			class:actief={i === currentIndex}
			onclick={() => onselect(i)}
		>
			<span class="status-dot" class:gereed={article.audio_ready} class:wachtend={!article.audio_ready}></span>
			<span class="bron-badge" style="background: {bronKleur(article.source)}">{article.source}</span>
			<span class="titel">{article.title}</span>
			{#if article.audio_quality}
				<span class="kwaliteit-tag">{article.audio_quality}</span>
			{/if}
		</button>
	{/each}

	{#if articles.length === 0}
		<div class="leeg">
			<p>Nog geen nieuwsartikelen vandaag.</p>
			<p class="hint">De briefing wordt om 04:30 gegenereerd.</p>
		</div>
	{/if}
</div>

<style>
	.lijst {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		max-height: 60vh;
		overflow-y: auto;
	}

	.artikel-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 0.75rem;
		padding: 0.75rem;
		cursor: pointer;
		text-align: left;
		color: #eaeaea;
		font-size: 0.85rem;
		transition: border-color 0.15s;
	}

	.artikel-item:hover {
		border-color: #e94560;
	}

	.artikel-item.actief {
		border-color: #e94560;
		background: #1a2742;
	}

	.status-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.status-dot.gereed {
		background: #22c55e;
	}

	.status-dot.wachtend {
		background: #888;
	}

	.bron-badge {
		font-size: 0.65rem;
		font-weight: 700;
		text-transform: uppercase;
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		color: white;
		flex-shrink: 0;
		letter-spacing: 0.03em;
	}

	.titel {
		flex: 1;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.kwaliteit-tag {
		font-size: 0.6rem;
		color: #888;
		background: #0f3460;
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		flex-shrink: 0;
	}

	.leeg {
		text-align: center;
		padding: 2rem 1rem;
		color: #888;
	}

	.leeg p {
		margin: 0.25rem 0;
	}

	.hint {
		font-size: 0.8rem;
	}
</style>
