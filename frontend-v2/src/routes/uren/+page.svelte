<script lang="ts">
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Download from '@lucide/svelte/icons/download';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Clock from '@lucide/svelte/icons/clock';

	type UrenEntry = { start: string; eind: string; omschrijving: string; duur_minuten: number };
	type UrenSummary = { id: string; datum: string; totaal_uren: string; entries_count: number; created_at: string };
	type UrenDetail = UrenSummary & { entries: UrenEntry[]; source_text: string };

	let sheets = $state<UrenSummary[]>([]);
	let selected = $state<UrenDetail | null>(null);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await fetch('/api/uren');
			if (res.ok) sheets = await res.json();
		} finally {
			loading = false;
		}
	});

	async function selectSheet(id: string) {
		const res = await fetch(`/api/uren/${id}`);
		if (res.ok) selected = await res.json();
	}

	function terug() {
		selected = null;
	}

	function downloadExcel() {
		if (!selected) return;
		window.open(`/api/uren/${selected.id}/excel`, '_blank');
	}

	function formatDatum(iso: string): string {
		const d = new Date(iso);
		const dagen = ['zo', 'ma', 'di', 'wo', 'do', 'vr', 'za'];
		const maanden = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
		return `${dagen[d.getDay()]} ${d.getDate()} ${maanden[d.getMonth()]}`;
	}

	function formatDuur(min: number): string {
		return `${Math.floor(min / 60)}:${(min % 60).toString().padStart(2, '0')}`;
	}
</script>

<div class="flex flex-col gap-4 px-4 pb-8">
	{#if selected}
		<!-- Detail view -->
		<div class="flex items-center justify-between pt-4">
			<Button variant="ghost" size="sm" class="gap-1 px-0" onclick={terug}>
				<ArrowLeft class="size-4" /> Terug
			</Button>
			<Button variant="outline" size="sm" class="gap-1.5" onclick={downloadExcel}>
				<Download class="size-3.5" /> Excel
			</Button>
		</div>

		<div>
			<h2 class="text-lg font-semibold">{formatDatum(selected.datum)}</h2>
			<span class="text-xs text-muted-foreground">Totaal: {selected.totaal_uren}</span>
		</div>

		<!-- Time entries table -->
		<div class="overflow-hidden rounded-lg border border-muted">
			<div class="grid grid-cols-[3.5rem_3.5rem_1fr_3rem] bg-muted/30 px-3 py-1.5 text-[0.6875rem] font-medium text-muted-foreground/50">
				<span>Start</span>
				<span>Eind</span>
				<span>Omschrijving</span>
				<span class="text-right">Duur</span>
			</div>
			{#each selected.entries as entry}
				<div class="grid grid-cols-[3.5rem_3.5rem_1fr_3rem] border-t border-muted/50 px-3 py-2 text-sm">
					<span class="font-mono text-xs">{entry.start}</span>
					<span class="font-mono text-xs">{entry.eind}</span>
					<span>{entry.omschrijving}</span>
					<span class="text-right font-mono text-xs text-muted-foreground">
						{formatDuur(entry.duur_minuten)}
					</span>
				</div>
			{/each}
			<div class="grid grid-cols-[3.5rem_3.5rem_1fr_3rem] border-t border-muted px-3 py-2 text-sm font-semibold">
				<span></span>
				<span></span>
				<span>Totaal</span>
				<span class="text-right font-mono text-xs">{selected.totaal_uren}</span>
			</div>
		</div>
	{:else}
		<!-- List view -->
		<h2 class="pl-0.5 pt-4 text-[0.6875rem] font-semibold uppercase tracking-widest text-muted-foreground/30">
			Uren
		</h2>

		{#if loading}
			<p class="py-12 text-center text-sm text-muted-foreground">Laden...</p>
		{:else if sheets.length === 0}
			<div class="flex flex-col items-center gap-2 py-16 text-center">
				<Clock class="size-10 text-muted-foreground/20" />
				<p class="text-sm text-muted-foreground">Nog geen uren geregistreerd.</p>
				<p class="text-xs text-muted-foreground/50">Zeg "uren van 8 tot 12 ..." om te starten.</p>
			</div>
		{:else}
			<div class="flex flex-col gap-0.5">
				{#each sheets as sheet}
					<Card.Root
						class="cursor-pointer bg-muted/30 transition-colors hover:bg-muted/50"
						onclick={() => selectSheet(sheet.id)}
					>
						<Card.Content class="flex items-center gap-3 p-3">
							<div class="min-w-0 flex-1">
								<p class="text-sm font-medium">{formatDatum(sheet.datum)}</p>
								<span class="text-xs text-muted-foreground/50">
									{sheet.entries_count} {sheet.entries_count === 1 ? 'regel' : 'regels'}
								</span>
							</div>
							<span class="font-mono text-sm text-orange-400">{sheet.totaal_uren}</span>
							<ChevronRight class="size-4 shrink-0 text-muted-foreground/25" />
						</Card.Content>
					</Card.Root>
				{/each}
			</div>
		{/if}
	{/if}
</div>
