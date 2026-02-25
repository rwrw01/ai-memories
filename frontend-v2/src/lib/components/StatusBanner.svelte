<script lang="ts">
	import { onMount } from 'svelte';
	import {
		POLL_INTERVAL,
		SERVICE_LABELS,
		type HealthResponse,
		type ServiceStatus
	} from '$lib/data/health-config';

	let health = $state<HealthResponse | null>(null);
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
	}

	const problems = $derived.by(() => {
		if (!health) return [];
		return Object.entries(health.services)
			.filter(([, v]) => v.status !== 'ok')
			.map(([k, v]) => ({
				name: SERVICE_LABELS[k] ?? k,
				status: v.status as ServiceStatus
			}));
	});

	const visible = $derived(fetchError || problems.length > 0);

	onMount(() => {
		checkHealth();
		const timer = setInterval(checkHealth, POLL_INTERVAL);
		return () => clearInterval(timer);
	});
</script>

{#if visible}
	<div
		class="shrink-0 px-4 py-1.5 text-center text-xs font-medium {fetchError
			? 'bg-red-900 text-red-200'
			: 'bg-amber-900 text-amber-100'}"
	>
		{#if fetchError}
			<span>Backend niet bereikbaar</span>
		{:else}
			<span>
				{problems.map((p) => `${p.name} ${p.status === 'down' ? 'offline' : 'traag'}`).join(' · ')}
			</span>
		{/if}
	</div>
{/if}
