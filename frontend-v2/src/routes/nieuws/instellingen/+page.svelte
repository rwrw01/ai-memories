<script lang="ts">
	import { onMount } from 'svelte';
	import type { NewsPreferences } from '$lib/types/news';
	import { FEED_CATALOG, type Provider } from '$lib/data/feed-catalog';
	import ServiceHealth from '$lib/components/ServiceHealth.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Switch } from '$lib/components/ui/switch';
	import { Slider } from '$lib/components/ui/slider';
	import { Badge } from '$lib/components/ui/badge';
	import { Separator } from '$lib/components/ui/separator';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';

	let feeds = $state<string[]>([]);
	let maxArtikelen = $state(20);
	let categoriesExclude = $state<string[]>([]);
	let nieuweFeed = $state('');
	let status = $state<'idle' | 'laden' | 'opgeslagen' | 'fout'>('idle');
	let openProviders = $state<Set<string>>(new Set());

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

	function toggleProvider(id: string) {
		const next = new Set(openProviders);
		if (next.has(id)) next.delete(id);
		else next.add(id);
		openProviders = next;
	}

	function toggleFeed(url: string) {
		if (feeds.includes(url)) feeds = feeds.filter((f) => f !== url);
		else feeds = [...feeds, url];
	}

	function actieveFeeds(provider: Provider): number {
		return provider.feeds.filter((f) => feeds.includes(f.url)).length;
	}

	function eigenFeeds(): string[] {
		const catalogUrls = new Set(FEED_CATALOG.flatMap((p) => p.feeds.map((f) => f.url)));
		return feeds.filter((f) => !catalogUrls.has(f));
	}

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
		if (categoriesExclude.includes(cat)) categoriesExclude = categoriesExclude.filter((c) => c !== cat);
		else categoriesExclude = [...categoriesExclude, cat];
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

<div class="flex flex-col gap-5 p-5">
	<div class="flex flex-col gap-1">
		<a href="/nieuws" class="flex items-center gap-1 text-sm text-primary">
			<ArrowLeft class="size-3.5" />Terug
		</a>
		<h1 class="text-lg font-bold">Nieuws instellingen</h1>
	</div>

	<!-- Systeemstatus -->
	<Card.Root>
		<Card.Header class="pb-3">
			<Card.Title class="text-sm">Systeemstatus</Card.Title>
		</Card.Header>
		<Card.Content>
			<ServiceHealth />
		</Card.Content>
	</Card.Root>

	<!-- Nieuwsbronnen -->
	<Card.Root>
		<Card.Header class="pb-3">
			<Card.Title class="text-sm">Nieuwsbronnen</Card.Title>
		</Card.Header>
		<Card.Content class="flex flex-col gap-2">
			{#each FEED_CATALOG as provider}
				{@const isEN = provider.lang === 'en'}
				{@const isOpen = openProviders.has(provider.id)}
				{@const actief = actieveFeeds(provider)}

				<button
					class="flex w-full items-center gap-2 rounded-lg bg-muted px-3 py-2.5 text-left text-sm transition-colors
						{isEN ? 'opacity-50' : 'hover:bg-accent'}"
					onclick={() => !isEN && toggleProvider(provider.id)}
					disabled={isEN}
				>
					{#if isEN}
						<ChevronRight class="size-3.5 text-muted-foreground" />
					{:else if isOpen}
						<ChevronDown class="size-3.5 text-muted-foreground" />
					{:else}
						<ChevronRight class="size-3.5 text-muted-foreground" />
					{/if}
					<span class="flex-1 font-semibold">{provider.name}</span>
					{#if isEN}
						<Badge variant="secondary" class="text-[0.65rem]">binnenkort</Badge>
					{:else}
						<span class="text-xs text-muted-foreground">{actief}/{provider.feeds.length}</span>
					{/if}
				</button>

				{#if isOpen && !isEN}
					<div class="flex flex-col gap-1 pl-5">
						{#each provider.feeds as feed}
							<label class="flex cursor-pointer items-center gap-3 rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:bg-muted">
								<Switch
									checked={feeds.includes(feed.url)}
									onCheckedChange={() => toggleFeed(feed.url)}
								/>
								<span class="flex-1">{feed.label}</span>
								<span class="text-[0.65rem] text-muted-foreground/50">{feed.category}</span>
							</label>
						{/each}
					</div>
				{/if}
			{/each}
		</Card.Content>
	</Card.Root>

	<!-- Eigen feeds -->
	{#if eigenFeeds().length > 0}
		<Card.Root>
			<Card.Header class="pb-3">
				<Card.Title class="text-sm">Eigen feeds</Card.Title>
			</Card.Header>
			<Card.Content class="flex flex-col gap-1.5">
				{#each eigenFeeds() as feed}
					<div class="flex items-center gap-2 rounded-lg bg-muted px-3 py-2">
						<span class="flex-1 truncate text-xs text-muted-foreground">{feed}</span>
						<Button variant="ghost" size="sm" class="h-auto p-1 text-destructive" onclick={() => feedVerwijderen(feed)} aria-label="Verwijderen">
							<X class="size-3.5" />
						</Button>
					</div>
				{/each}
			</Card.Content>
		</Card.Root>
	{/if}

	<!-- Feed toevoegen -->
	<Card.Root>
		<Card.Header class="pb-3">
			<Card.Title class="text-sm">Eigen feed toevoegen</Card.Title>
		</Card.Header>
		<Card.Content>
			<div class="flex gap-2">
				<Input
					type="url"
					placeholder="https://example.com/rss"
					bind:value={nieuweFeed}
					onkeydown={(e) => e.key === 'Enter' && feedToevoegen()}
				/>
				<Button variant="outline" size="icon" onclick={feedToevoegen} disabled={!nieuweFeed.trim()}>
					<Plus class="size-4" />
				</Button>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Maximum artikelen -->
	<Card.Root>
		<Card.Header class="pb-3">
			<Card.Title class="text-sm">Maximum artikelen</Card.Title>
		</Card.Header>
		<Card.Content>
			<div class="flex items-center gap-3">
				<Slider type="single" bind:value={maxArtikelen} min={5} max={30} step={1} class="flex-1" />
				<span class="min-w-8 text-center text-sm font-semibold">{maxArtikelen}</span>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Categorieën uitsluiten -->
	<Card.Root>
		<Card.Header class="pb-3">
			<Card.Title class="text-sm">Categorieën uitsluiten</Card.Title>
		</Card.Header>
		<Card.Content>
			<div class="flex flex-wrap gap-2">
				{#each categorieen as cat}
					<label class="flex cursor-pointer items-center gap-2 rounded-md bg-muted px-3 py-1.5 text-sm text-muted-foreground">
						<Switch
							checked={categoriesExclude.includes(cat)}
							onCheckedChange={() => toggleCategorie(cat)}
						/>
						<span>{cat}</span>
					</label>
				{/each}
			</div>
		</Card.Content>
	</Card.Root>

	<Button class="w-full" onclick={opslaan} disabled={status === 'laden'}>
		{#if status === 'laden'}
			Opslaan...
		{:else if status === 'opgeslagen'}
			Opgeslagen!
		{:else if status === 'fout'}
			Fout bij opslaan
		{:else}
			Opslaan
		{/if}
	</Button>

	<p class="mt-4 text-center text-xs text-muted-foreground/30">Herinneringen v2.0</p>
</div>
