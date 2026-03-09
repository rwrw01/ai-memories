<script lang="ts">
	import { onMount } from 'svelte';
	import {
		POLL_INTERVAL,
		SERVICE_LABELS,
		STATUS_LABELS,
		STATUS_COLORS,
		type HealthResponse
	} from '$lib/data/health-config';

	let health = $state<HealthResponse | null>(null);
	let loading = $state(true);

	async function checkHealth() {
		try {
			const resp = await fetch('/api/health');
			if (resp.ok) health = await resp.json();
		} catch {
			// handled by null check
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		checkHealth();
		const timer = setInterval(checkHealth, POLL_INTERVAL);
		return () => clearInterval(timer);
	});
</script>

<div class="space-y-6 p-4">
	<h2 class="text-lg font-semibold">Instellingen</h2>

	<section class="space-y-3">
		<h3 class="text-sm font-medium text-muted-foreground">Systeemstatus</h3>

		{#if loading}
			<p class="text-sm text-muted-foreground">Laden...</p>
		{:else if !health}
			<p class="text-sm text-red-400">Backend niet bereikbaar</p>
		{:else}
			<div class="rounded-lg border border-white/8 divide-y divide-white/8">
				{#each Object.entries(health.services) as [key, svc]}
					{@const label = SERVICE_LABELS[key] ?? key}
					{@const colors = STATUS_COLORS[svc.status]}
					<div class="flex items-center justify-between px-4 py-3">
						<span class="text-sm">{label}</span>
						<span class="flex items-center gap-2 text-xs {colors.text}">
							<span class="inline-block size-2 rounded-full {colors.dot}"></span>
							{STATUS_LABELS[svc.status]}
						</span>
					</div>
				{/each}
			</div>
		{/if}
	</section>
</div>
