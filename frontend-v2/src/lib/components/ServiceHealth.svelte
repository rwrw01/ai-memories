<script lang="ts">
	import { onMount } from 'svelte';

	type ServiceStatus = 'ok' | 'slow' | 'down';
	type HealthResponse = {
		status: 'ok' | 'degraded';
		services: Record<string, { status: ServiceStatus }>;
		checked_at: string;
	};

	const POLL_INTERVAL = 30_000;
	const SERVICE_LABELS: Record<string, string> = {
		database: 'Database',
		stt: 'Spraak-naar-tekst',
		tts: 'Tekst-naar-spraak',
		ollama: 'LLM',
		n8n: 'Automatisering'
	};
	const STATUS_LABELS: Record<ServiceStatus, string> = {
		ok: 'Online',
		slow: 'Traag',
		down: 'Offline'
	};
	const STATUS_COLORS: Record<ServiceStatus, string> = {
		ok: 'bg-green-500 text-green-500',
		slow: 'bg-amber-500 text-amber-500',
		down: 'bg-red-500 text-red-500'
	};

	let health = $state<HealthResponse | null>(null);
	let loading = $state(true);
	let fetchError = $state(false);

	async function checkHealth() {
		try {
			const resp = await fetch('/api/health');
			if (resp.ok) {
				health = await resp.json();
				fetchError = false;
			} else {
				fetchError = true;
			}
		} catch {
			fetchError = true;
		}
		loading = false;
	}

	onMount(() => {
		checkHealth();
		const timer = setInterval(checkHealth, POLL_INTERVAL);
		return () => clearInterval(timer);
	});
</script>

<div class="flex flex-col gap-1.5">
	{#if loading}
		<div class="flex items-center gap-2 py-1.5">
			<span class="text-sm text-muted-foreground">Laden...</span>
		</div>
	{:else if fetchError}
		<div class="flex items-center gap-2 py-1.5">
			<span class="size-2 rounded-full bg-red-500"></span>
			<span class="text-sm text-muted-foreground">Backend niet bereikbaar</span>
		</div>
	{:else if health}
		{#each Object.entries(health.services) as [key, svc]}
			{@const colors = STATUS_COLORS[svc.status]}
			<div class="flex items-center gap-2 py-1.5">
				<span class="size-2 rounded-full {colors.split(' ')[0]}"></span>
				<span class="flex-1 text-sm text-muted-foreground">{SERVICE_LABELS[key] ?? key}</span>
				<span class="text-xs font-medium {colors.split(' ')[1]}">{STATUS_LABELS[svc.status]}</span>
			</div>
		{/each}
	{/if}
</div>
