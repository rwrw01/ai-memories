<script lang="ts">
	import NewsPlayer from '$lib/components/NewsPlayer.svelte';
	import NewsList from '$lib/components/NewsList.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Tabs from '$lib/components/ui/tabs';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';

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

<div class="flex min-h-full flex-col gap-4 p-5">
	<div class="flex items-baseline justify-between">
		<h1 class="text-xl font-bold">Nieuws</h1>
		{#if data.date}
			<span class="text-sm text-muted-foreground">{data.date}</span>
		{/if}
	</div>

	<div class="flex items-center gap-2 text-sm text-muted-foreground">
		<span>{data.total} artikelen</span>
		<span class="text-muted-foreground/40">·</span>
		<span>{data.audioReadyCount} audio gereed</span>
		<Button
			variant="outline"
			size="sm"
			class="ml-auto gap-1.5"
			disabled={verversStatus === 'laden'}
			onclick={ververs}
		>
			<RefreshCw class="size-3.5 {verversStatus === 'laden' ? 'animate-spin' : ''}" />
			{#if verversStatus === 'laden'}
				Bezig...
			{:else if verversStatus === 'klaar'}
				Vernieuwd!
			{:else if verversStatus === 'fout'}
				Mislukt
			{:else}
				Vernieuwen
			{/if}
		</Button>
	</div>

	<Tabs.Root bind:value={weergave}>
		<Tabs.List class="w-full">
			<Tabs.Trigger value="speler" class="flex-1">Speler</Tabs.Trigger>
			<Tabs.Trigger value="lijst" class="flex-1">Lijst</Tabs.Trigger>
		</Tabs.List>
		<Tabs.Content value="speler">
			<NewsPlayer articles={data.articles} />
		</Tabs.Content>
		<Tabs.Content value="lijst">
			<NewsList
				articles={data.articles}
				currentIndex={geselecteerdeIndex}
				onselect={selecteerArtikel}
			/>
		</Tabs.Content>
	</Tabs.Root>
</div>
