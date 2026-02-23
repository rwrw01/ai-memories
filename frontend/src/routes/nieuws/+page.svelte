<script lang="ts">
	import NewsPlayer from '$lib/components/NewsPlayer.svelte';
	import NewsList from '$lib/components/NewsList.svelte';

	let { data } = $props();
	let weergave = $state<'speler' | 'lijst'>('speler');
	let geselecteerdeIndex = $state(0);

	function selecteerArtikel(index: number) {
		geselecteerdeIndex = index;
		weergave = 'speler';
	}

	let verversStatus = $state<'idle' | 'laden' | 'klaar' | 'fout'>('idle');

	async function ververs() {
		verversStatus = 'laden';
		try {
			const res = await fetch('/api/news/refresh', { method: 'POST' });
			if (!res.ok) throw new Error();
			verversStatus = 'klaar';
			setTimeout(() => (verversStatus = 'idle'), 3000);
		} catch {
			verversStatus = 'fout';
			setTimeout(() => (verversStatus = 'idle'), 3000);
		}
	}
</script>

<div class="nieuws">
	<div class="header-rij">
		<h1 class="pagina-titel">Nieuws</h1>
		{#if data.date}
			<span class="datum">{data.date}</span>
		{/if}
	</div>

	<div class="stats-rij">
		<span class="stat">{data.total} artikelen</span>
		<span class="stat-scheiding">·</span>
		<span class="stat">{data.audioReadyCount} audio gereed</span>
		<button
			class="ververs-knop"
			disabled={verversStatus === 'laden'}
			onclick={ververs}
		>
			{#if verversStatus === 'laden'}
				Bezig...
			{:else if verversStatus === 'klaar'}
				Vernieuwd!
			{:else if verversStatus === 'fout'}
				Mislukt
			{:else}
				Vernieuwen
			{/if}
		</button>
	</div>

	<div class="tabs">
		<button
			class="tab"
			class:actief={weergave === 'speler'}
			onclick={() => (weergave = 'speler')}
		>
			Speler
		</button>
		<button
			class="tab"
			class:actief={weergave === 'lijst'}
			onclick={() => (weergave = 'lijst')}
		>
			Lijst
		</button>
	</div>

	{#if weergave === 'speler'}
		<NewsPlayer articles={data.articles} />
	{:else}
		<NewsList
			articles={data.articles}
			currentIndex={geselecteerdeIndex}
			onselect={selecteerArtikel}
		/>
	{/if}
</div>

<style>
	.nieuws {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 1.5rem 1.25rem;
		min-height: 100%;
	}

	.header-rij {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
	}

	.pagina-titel {
		font-size: 1.3rem;
		font-weight: 700;
		color: #eaeaea;
		margin: 0;
	}

	.datum {
		font-size: 0.8rem;
		color: #888;
	}

	.stats-rij {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.8rem;
		color: #888;
	}

	.stat-scheiding {
		color: #555;
	}

	.ververs-knop {
		margin-left: auto;
		background: #0f3460;
		border: 1px solid #1a4080;
		border-radius: 0.375rem;
		color: #eaeaea;
		font-size: 0.75rem;
		padding: 0.25rem 0.75rem;
		cursor: pointer;
		transition: opacity 0.15s;
	}

	.ververs-knop:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.tabs {
		display: flex;
		gap: 0;
		border-radius: 0.5rem;
		overflow: hidden;
		border: 1px solid #0f3460;
	}

	.tab {
		flex: 1;
		background: #16213e;
		border: none;
		color: #888;
		font-size: 0.85rem;
		font-weight: 600;
		padding: 0.625rem;
		cursor: pointer;
		transition: background 0.15s, color 0.15s;
	}

	.tab.actief {
		background: #0f3460;
		color: #e94560;
	}
</style>
