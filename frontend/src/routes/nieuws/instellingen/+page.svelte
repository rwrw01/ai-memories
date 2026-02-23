<script lang="ts">
	import { onMount } from 'svelte';
	import type { NewsPreferences } from '$lib/types/news';

	let feeds = $state<string[]>([]);
	let maxArtikelen = $state(20);
	let categoriesExclude = $state<string[]>([]);
	let nieuweFeed = $state('');
	let status = $state<'idle' | 'laden' | 'opgeslagen' | 'fout'>('idle');

	const categorieen = ['sport', 'entertainment', 'cultuur', 'economie', 'tech'];

	onMount(async () => {
		try {
			const res = await fetch('/api/news/preferences');
			if (res.ok) {
				const data: NewsPreferences = await res.json();
				feeds = data.feeds;
				maxArtikelen = data.max_articles;
				categoriesExclude = data.categories_exclude;
			}
		} catch {
			// Use defaults
		}
	});

	function feedToevoegen() {
		const url = nieuweFeed.trim();
		if (url && !feeds.includes(url)) {
			feeds = [...feeds, url];
			nieuweFeed = '';
		}
	}

	function feedVerwijderen(url: string) {
		feeds = feeds.filter((f) => f !== url);
	}

	function toggleCategorie(cat: string) {
		if (categoriesExclude.includes(cat)) {
			categoriesExclude = categoriesExclude.filter((c) => c !== cat);
		} else {
			categoriesExclude = [...categoriesExclude, cat];
		}
	}

	async function opslaan() {
		status = 'laden';
		try {
			const res = await fetch('/api/news/preferences', {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					feeds,
					max_articles: maxArtikelen,
					categories_exclude: categoriesExclude
				})
			});
			if (!res.ok) throw new Error();
			status = 'opgeslagen';
			setTimeout(() => (status = 'idle'), 2000);
		} catch {
			status = 'fout';
			setTimeout(() => (status = 'idle'), 3000);
		}
	}
</script>

<div class="instellingen">
	<div class="header-rij">
		<a href="/nieuws" class="terug-link">← Terug</a>
		<h1 class="pagina-titel">Nieuws instellingen</h1>
	</div>

	<section class="sectie">
		<h2 class="sectie-titel">RSS Feeds</h2>
		<div class="feeds-lijst">
			{#each feeds as feed}
				<div class="feed-item">
					<span class="feed-url">{feed}</span>
					<button class="verwijder-knop" onclick={() => feedVerwijderen(feed)} aria-label="Verwijderen">
						✕
					</button>
				</div>
			{/each}
		</div>
		<div class="feed-toevoegen">
			<input
				class="feed-invoer"
				type="url"
				placeholder="https://example.com/rss"
				bind:value={nieuweFeed}
				onkeydown={(e) => e.key === 'Enter' && feedToevoegen()}
			/>
			<button class="toevoeg-knop" onclick={feedToevoegen} disabled={!nieuweFeed.trim()}>
				Toevoegen
			</button>
		</div>
	</section>

	<section class="sectie">
		<h2 class="sectie-titel">Maximum artikelen</h2>
		<div class="slider-rij">
			<input
				type="range"
				min="5"
				max="30"
				bind:value={maxArtikelen}
				class="slider"
			/>
			<span class="slider-waarde">{maxArtikelen}</span>
		</div>
	</section>

	<section class="sectie">
		<h2 class="sectie-titel">Categorieën uitsluiten</h2>
		<div class="categorie-lijst">
			{#each categorieen as cat}
				<label class="categorie-optie">
					<input
						type="checkbox"
						checked={categoriesExclude.includes(cat)}
						onchange={() => toggleCategorie(cat)}
					/>
					<span>{cat}</span>
				</label>
			{/each}
		</div>
	</section>

	<button class="opslaan-knop" onclick={opslaan} disabled={status === 'laden'}>
		{#if status === 'laden'}
			Opslaan...
		{:else if status === 'opgeslagen'}
			Opgeslagen!
		{:else if status === 'fout'}
			Fout bij opslaan
		{:else}
			Opslaan
		{/if}
	</button>
</div>

<style>
	.instellingen {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
		padding: 1.5rem 1.25rem;
	}

	.header-rij {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.terug-link {
		font-size: 0.8rem;
		color: #e94560;
	}

	.pagina-titel {
		font-size: 1.2rem;
		font-weight: 700;
		color: #eaeaea;
		margin: 0;
	}

	.sectie {
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 1rem;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.sectie-titel {
		font-size: 0.9rem;
		font-weight: 600;
		color: #eaeaea;
		margin: 0;
	}

	.feeds-lijst {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.feed-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		background: #0f3460;
		border-radius: 0.5rem;
		padding: 0.5rem 0.75rem;
	}

	.feed-url {
		flex: 1;
		font-size: 0.75rem;
		color: #bbb;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.verwijder-knop {
		background: none;
		border: none;
		color: #e94560;
		cursor: pointer;
		font-size: 0.85rem;
		padding: 0.125rem 0.25rem;
	}

	.feed-toevoegen {
		display: flex;
		gap: 0.5rem;
	}

	.feed-invoer {
		flex: 1;
		background: #0f3460;
		border: 1px solid #1a4080;
		border-radius: 0.375rem;
		padding: 0.5rem;
		color: #eaeaea;
		font-size: 0.8rem;
	}

	.feed-invoer:focus {
		outline: none;
		border-color: #e94560;
	}

	.toevoeg-knop {
		background: #0f3460;
		border: 1px solid #1a4080;
		border-radius: 0.375rem;
		color: #eaeaea;
		font-size: 0.8rem;
		padding: 0.5rem 0.75rem;
		cursor: pointer;
		white-space: nowrap;
	}

	.toevoeg-knop:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.slider-rij {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.slider {
		flex: 1;
		accent-color: #e94560;
	}

	.slider-waarde {
		font-size: 0.9rem;
		color: #eaeaea;
		font-weight: 600;
		min-width: 2rem;
		text-align: center;
	}

	.categorie-lijst {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.categorie-optie {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		background: #0f3460;
		border-radius: 0.375rem;
		padding: 0.375rem 0.625rem;
		font-size: 0.8rem;
		color: #bbb;
		cursor: pointer;
	}

	.categorie-optie input {
		accent-color: #e94560;
	}

	.opslaan-knop {
		background: linear-gradient(135deg, #e94560, #c23152);
		border: none;
		border-radius: 0.5rem;
		padding: 0.75rem;
		color: white;
		font-size: 0.95rem;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.15s;
	}

	.opslaan-knop:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
