<script lang="ts">
	import { onMount } from 'svelte';
	import type { Artikel } from '$lib/types/artikel';

	let artikelen = $state<Artikel[]>([]);
	let selected = $state<Artikel | null>(null);
	let loading = $state(true);
	let copied = $state(false);

	onMount(async () => {
		try {
			const res = await fetch('/api/artikelen');
			if (res.ok) artikelen = await res.json();
		} finally {
			loading = false;
		}
	});

	async function selectArtikel(id: string) {
		const res = await fetch(`/api/artikelen/${id}`);
		if (res.ok) selected = await res.json();
	}

	function terug() {
		selected = null;
		copied = false;
	}

	async function kopieer() {
		if (!selected?.content) return;
		await navigator.clipboard.writeText(selected.content);
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}

	function formatDatum(iso: string): string {
		const d = new Date(iso);
		return d.toLocaleDateString('nl-NL', { day: 'numeric', month: 'short', year: 'numeric' });
	}
</script>

{#if selected}
	<div class="detail">
		<div class="detail-header">
			<button class="terug-btn" onclick={terug}>
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M19 12H5M12 19l-7-7 7-7"/>
				</svg>
				Terug
			</button>
			<button class="kopieer-btn" onclick={kopieer}>
				{#if copied}
					Gekopieerd!
				{:else}
					<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
						<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
					</svg>
					Kopieer
				{/if}
			</button>
		</div>
		<h2 class="detail-titel">{selected.title}</h2>
		<span class="detail-datum">{formatDatum(selected.created_at)}</span>
		<div class="detail-content">{selected.content}</div>
	</div>
{:else}
	<div class="lijst-container">
		{#if loading}
			<div class="leeg"><p>Laden...</p></div>
		{:else if artikelen.length === 0}
			<div class="leeg">
				<p>Nog geen artikelen.</p>
				<p class="hint">Zeg "artikel over ..." om er een te genereren.</p>
			</div>
		{:else}
			<div class="lijst">
				{#each artikelen as artikel}
					<button class="artikel-item" onclick={() => selectArtikel(artikel.id)}>
						<div class="artikel-info">
							<span class="artikel-titel">{artikel.title}</span>
							<span class="artikel-datum">{formatDatum(artikel.created_at)}</span>
						</div>
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="chevron">
							<path d="M9 18l6-6-6-6"/>
						</svg>
					</button>
				{/each}
			</div>
		{/if}
	</div>
{/if}

<style>
	.lijst-container {
		padding: 1rem;
	}

	.lijst {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.artikel-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 0.75rem;
		padding: 0.75rem 1rem;
		cursor: pointer;
		text-align: left;
		color: #eaeaea;
		transition: border-color 0.15s;
		width: 100%;
	}

	.artikel-item:hover {
		border-color: #e94560;
	}

	.artikel-info {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		min-width: 0;
	}

	.artikel-titel {
		font-size: 0.9rem;
		font-weight: 500;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.artikel-datum {
		font-size: 0.75rem;
		color: #888;
	}

	.chevron {
		flex-shrink: 0;
		color: #555;
	}

	.leeg {
		text-align: center;
		padding: 3rem 1rem;
		color: #888;
	}

	.leeg p {
		margin: 0.25rem 0;
	}

	.hint {
		font-size: 0.8rem;
	}

	/* Detail view */
	.detail {
		padding: 1rem;
	}

	.detail-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
	}

	.terug-btn {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		background: none;
		border: none;
		color: #e94560;
		font-size: 0.85rem;
		cursor: pointer;
		padding: 0.375rem 0;
	}

	.kopieer-btn {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 0.5rem;
		color: #eaeaea;
		font-size: 0.8rem;
		padding: 0.5rem 0.75rem;
		cursor: pointer;
		transition: border-color 0.15s;
	}

	.kopieer-btn:hover {
		border-color: #e94560;
	}

	.detail-titel {
		font-size: 1.15rem;
		font-weight: 600;
		color: #e5e5e5;
		margin-bottom: 0.25rem;
	}

	.detail-datum {
		font-size: 0.75rem;
		color: #888;
		display: block;
		margin-bottom: 1rem;
	}

	.detail-content {
		font-size: 0.9rem;
		line-height: 1.65;
		color: #ccc;
		white-space: pre-wrap;
	}
</style>
