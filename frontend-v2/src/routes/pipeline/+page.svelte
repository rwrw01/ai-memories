<script lang="ts">
	import { onMount } from 'svelte';
	import { Badge } from '$lib/components/ui/badge';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';

	type Execution = {
		id: string;
		intent: string;
		status: string;
		error: string | null;
		source_text: string;
		created_at: string | null;
	};

	let executions = $state<Execution[]>([]);
	let loading = $state(true);
	let autoRefresh = $state(true);
	let refreshTimer: ReturnType<typeof setInterval> | undefined;

	async function fetchRecent() {
		try {
			const resp = await fetch('/api/flow/recent');
			if (resp.ok) {
				executions = await resp.json();
			}
		} catch {
			// silently ignore
		} finally {
			loading = false;
		}
	}

	function startAutoRefresh() {
		refreshTimer = setInterval(fetchRecent, 5000);
	}

	function stopAutoRefresh() {
		if (refreshTimer) {
			clearInterval(refreshTimer);
			refreshTimer = undefined;
		}
	}

	$effect(() => {
		if (autoRefresh) {
			startAutoRefresh();
		} else {
			stopAutoRefresh();
		}
		return () => stopAutoRefresh();
	});

	onMount(() => {
		fetchRecent();
	});

	const statusColors: Record<string, string> = {
		pending: 'bg-yellow-600/15 text-yellow-400 border-yellow-600/30',
		running: 'bg-blue-600/15 text-blue-400 border-blue-600/30',
		success: 'bg-green-600/15 text-green-400 border-green-600/30',
		error: 'bg-red-600/15 text-red-400 border-red-600/30'
	};

	const intentColors: Record<string, string> = {
		artikel: 'bg-blue-600/15 text-blue-400 border-blue-600/30',
		whatsapp: 'bg-green-600/15 text-green-400 border-green-600/30',
		uren: 'bg-orange-600/15 text-orange-400 border-orange-600/30',
		aantekening: 'bg-muted text-muted-foreground border-muted'
	};

	function formatTime(iso: string | null): string {
		if (!iso) return '';
		const d = new Date(iso);
		return d.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
	}

	function formatDate(iso: string | null): string {
		if (!iso) return '';
		const d = new Date(iso);
		const today = new Date();
		if (d.toDateString() === today.toDateString()) return 'Vandaag';
		return d.toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' });
	}
</script>

<div class="flex flex-col gap-3 p-4">
	<div class="flex items-center justify-between">
		<h2 class="text-base font-semibold">Pipeline Monitor</h2>
		<div class="flex items-center gap-2">
			<label class="flex items-center gap-1.5 text-xs text-muted-foreground">
				<input type="checkbox" bind:checked={autoRefresh} class="accent-primary" />
				Auto
			</label>
			<Button
				variant="ghost"
				size="sm"
				class="h-7 w-7 p-0"
				onclick={fetchRecent}
			>
				<RefreshCw class="size-3.5" />
			</Button>
		</div>
	</div>

	{#if loading}
		<p class="text-sm text-muted-foreground">Laden...</p>
	{:else if executions.length === 0}
		<Card.Root class="border-muted/30">
			<Card.Content class="p-6 text-center">
				<p class="text-sm text-muted-foreground">Nog geen flow-uitvoeringen.</p>
				<p class="mt-1 text-xs text-muted-foreground/60">
					Zeg een commando zoals "artikel over..." om een flow te starten.
				</p>
			</Card.Content>
		</Card.Root>
	{:else}
		<div class="flex flex-col gap-2">
			{#each executions as ex (ex.id)}
				<Card.Root class="border-primary/10 bg-primary/5">
					<Card.Content class="p-3">
						<div class="flex items-center justify-between gap-2">
							<div class="flex items-center gap-1.5">
								<Badge class="{intentColors[ex.intent] ?? intentColors.aantekening} text-[0.625rem]">
									{ex.intent}
								</Badge>
								<Badge class="{statusColors[ex.status] ?? statusColors.pending} text-[0.625rem]">
									{ex.status}
								</Badge>
							</div>
							<span class="text-[0.6rem] text-muted-foreground/50">
								{formatDate(ex.created_at)} {formatTime(ex.created_at)}
							</span>
						</div>

						{#if ex.source_text}
							<p class="mt-1.5 truncate text-xs text-muted-foreground">
								{ex.source_text}
							</p>
						{/if}

						{#if ex.error}
							<p class="mt-1 text-xs text-red-400/80">
								{ex.error}
							</p>
						{/if}

						<p class="mt-1 text-[0.55rem] text-muted-foreground/30 font-mono">
							{ex.id}
						</p>
					</Card.Content>
				</Card.Root>
			{/each}
		</div>
	{/if}
</div>
