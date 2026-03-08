<script lang="ts">
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Copy from '@lucide/svelte/icons/copy';
	import Check from '@lucide/svelte/icons/check';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import FileText from '@lucide/svelte/icons/file-text';

	type ArtikelSummary = { id: string; title: string; created_at: string };
	type ArtikelDetail = ArtikelSummary & { content: string; source_text: string };

	let artikelen = $state<ArtikelSummary[]>([]);
	let selected = $state<ArtikelDetail | null>(null);
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
		const maanden = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
		return `${d.getDate()} ${maanden[d.getMonth()]} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
	}
</script>

<div class="flex flex-col gap-4 px-4 pb-8">
	{#if selected}
		<!-- Detail view -->
		<div class="flex items-center justify-between pt-4">
			<Button variant="ghost" size="sm" class="gap-1 px-0" onclick={terug}>
				<ArrowLeft class="size-4" />
				Terug
			</Button>
			<Button variant="outline" size="sm" class="gap-1.5" onclick={kopieer}>
				{#if copied}
					<Check class="size-3.5" />
					Gekopieerd
				{:else}
					<Copy class="size-3.5" />
					Kopieer
				{/if}
			</Button>
		</div>

		<div>
			<h2 class="text-lg font-semibold leading-tight">{selected.title}</h2>
			<span class="text-xs text-muted-foreground">{formatDatum(selected.created_at)}</span>
		</div>

		<p class="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
			{selected.content}
		</p>
	{:else}
		<!-- List view -->
		<h2 class="pl-0.5 pt-4 text-[0.6875rem] font-semibold uppercase tracking-widest text-muted-foreground/30">
			Artikelen
		</h2>

		{#if loading}
			<p class="py-12 text-center text-sm text-muted-foreground">Laden...</p>
		{:else if artikelen.length === 0}
			<div class="flex flex-col items-center gap-2 py-16 text-center">
				<FileText class="size-10 text-muted-foreground/20" />
				<p class="text-sm text-muted-foreground">Nog geen artikelen.</p>
				<p class="text-xs text-muted-foreground/50">Zeg "artikel over ..." om er een te genereren.</p>
			</div>
		{:else}
			<div class="flex flex-col gap-0.5">
				{#each artikelen as artikel}
					<Card.Root class="cursor-pointer bg-muted/30 transition-colors hover:bg-muted/50" onclick={() => selectArtikel(artikel.id)}>
						<Card.Content class="flex items-center gap-3 p-3">
							<div class="min-w-0 flex-1">
								<p class="truncate text-sm font-medium">{artikel.title}</p>
								<span class="text-xs text-muted-foreground/50">{formatDatum(artikel.created_at)}</span>
							</div>
							<ChevronRight class="size-4 shrink-0 text-muted-foreground/25" />
						</Card.Content>
					</Card.Root>
				{/each}
			</div>
		{/if}
	{/if}
</div>
