<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { Input } from '$lib/components/ui/input';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import Smartphone from '@lucide/svelte/icons/smartphone';

	type Contact = { name: string; number: string };

	let status = $state<{ ready: boolean; hasQr: boolean; error?: string } | null>(null);
	let qrDataUrl = $state<string | null>(null);
	let contacts = $state<Contact[]>([]);
	let zoekterm = $state('');
	let loading = $state(true);
	let phoneNumber = $state('');
	let pairingCode = $state<string | null>(null);
	let pairingLoading = $state(false);
	let pairingError = $state<string | null>(null);

	let gefilterdeContacten = $derived(
		zoekterm
			? contacts.filter((c) => c.name.toLowerCase().includes(zoekterm.toLowerCase()))
			: contacts
	);

	async function fetchStatus() {
		try {
			const res = await fetch('/api/whatsapp/status');
			status = await res.json();
		} catch {
			status = { ready: false, hasQr: false, error: 'Kan status niet ophalen' };
		}
	}

	async function fetchQr() {
		try {
			const res = await fetch('/api/whatsapp/qr');
			const data = await res.json();
			qrDataUrl = data.qr ?? null;
			if (data.ready) {
				status = { ready: true, hasQr: false };
			}
		} catch {
			qrDataUrl = null;
		}
	}

	async function fetchContacts() {
		try {
			const res = await fetch('/api/whatsapp/contacts');
			if (res.ok) {
				const data = await res.json();
				if (Array.isArray(data)) contacts = data;
			}
		} catch {
			// Contacts not available yet
		}
	}

	async function refresh() {
		loading = true;
		await fetchStatus();
		if (status?.ready) {
			await fetchContacts();
		} else if (status?.hasQr) {
			await fetchQr();
		}
		loading = false;
	}

	async function requestPair() {
		const cleaned = phoneNumber.replace(/[\s\-\+\(\)]/g, '');
		if (!cleaned || cleaned.length < 10) {
			pairingError = 'Voer een geldig telefoonnummer in (bijv. 31612345678)';
			return;
		}
		pairingLoading = true;
		pairingError = null;
		pairingCode = null;
		try {
			const res = await fetch('/api/whatsapp/pair', {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ phoneNumber: cleaned })
			});
			const data = await res.json();
			if (data.ready) {
				status = { ready: true, hasQr: false };
				await fetchContacts();
			} else if (data.code) {
				pairingCode = data.code;
			} else if (data.error) {
				pairingError = data.error;
			}
		} catch {
			pairingError = 'Koppeling mislukt, probeer opnieuw';
		}
		pairingLoading = false;
	}

	let pollInterval: ReturnType<typeof setInterval> | null = null;

	onMount(() => {
		refresh();

		// Auto-refresh every 3 seconds while waiting for QR scan
		pollInterval = setInterval(async () => {
			if (!status?.ready) {
				await fetchStatus();
				if (status?.hasQr && !status?.ready) {
					await fetchQr();
				}
				if (status?.ready) {
					await fetchContacts();
				}
			}
		}, 3000);
	});

	onDestroy(() => {
		if (pollInterval) clearInterval(pollInterval);
	});
</script>

<div class="flex flex-col gap-4 px-4 pb-8">
	<div class="flex items-center justify-between pt-2">
		<h2 class="text-sm font-semibold text-muted-foreground">WhatsApp</h2>
		<Button variant="ghost" size="sm" class="h-7 gap-1 text-xs" onclick={refresh} disabled={loading}>
			<RefreshCw class="size-3 {loading ? 'animate-spin' : ''}" />
			Vernieuwen
		</Button>
	</div>

	<!-- Status -->
	<Card.Root>
		<Card.Content class="p-3">
			<div class="flex items-center gap-2">
				<span class="text-sm text-muted-foreground">Status:</span>
				{#if status?.ready}
					<Badge class="bg-green-600/15 text-green-400 border-green-600/30">Verbonden</Badge>
				{:else if status?.error}
					<Badge variant="destructive">{status.error}</Badge>
				{:else}
					<Badge variant="secondary">Niet verbonden</Badge>
				{/if}
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Phone number pairing (primary on mobile) -->
	{#if !status?.ready}
		<Card.Root>
			<Card.Content class="flex flex-col gap-3 p-4">
				<div class="flex items-center gap-2">
					<Smartphone class="size-4 text-green-400" />
					<p class="text-sm font-medium">Koppel via telefoonnummer</p>
				</div>

				<div class="flex gap-2">
					<Input
						bind:value={phoneNumber}
						placeholder="31612345678"
						class="h-9 text-sm"
						type="tel"
					/>
					<Button
						size="sm"
						class="h-9 shrink-0"
						onclick={requestPair}
						disabled={pairingLoading || !phoneNumber}
					>
						{pairingLoading ? 'Bezig...' : 'Koppelen'}
					</Button>
				</div>

				{#if pairingCode}
					<div class="flex flex-col items-center gap-2 rounded-lg bg-green-600/10 p-4">
						<p class="text-xs text-muted-foreground">Voer deze code in op je telefoon:</p>
						<span class="text-3xl font-bold tracking-widest text-green-400">{pairingCode}</span>
					</div>
				{/if}

				{#if pairingError}
					<p class="text-xs text-red-400">{pairingError}</p>
				{/if}

				<p class="text-xs text-muted-foreground/40">
					Open WhatsApp → Gekoppelde apparaten → Koppel een apparaat → Koppel via telefoonnummer
				</p>
			</Card.Content>
		</Card.Root>

		<!-- QR Code (alternative, e.g. from desktop) -->
		<Card.Root>
			<Card.Content class="flex flex-col items-center gap-3 p-4">
				<p class="text-sm text-muted-foreground">Of scan de QR code (vanaf een ander scherm)</p>
				{#if qrDataUrl}
					<img
						src={qrDataUrl}
						alt="WhatsApp QR code"
						class="size-56 rounded-lg bg-white p-2"
					/>
				{:else}
					<div class="flex size-56 items-center justify-center rounded-lg bg-muted/30">
						<span class="text-sm text-muted-foreground/50">Wachten op QR code...</span>
					</div>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}

	<!-- Contacts -->
	{#if status?.ready && contacts.length > 0}
		<div class="flex flex-col gap-2">
			<Input
				bind:value={zoekterm}
				placeholder="Zoek contact..."
				class="h-8 text-sm"
			/>

			<Card.Root>
				<Card.Content class="max-h-80 overflow-y-auto p-0">
					{#each gefilterdeContacten as contact}
						<div class="flex items-center justify-between border-b border-muted/20 px-3 py-2 last:border-0">
							<span class="text-sm">{contact.name}</span>
							<span class="text-xs text-muted-foreground/40">{contact.number}</span>
						</div>
					{/each}
					{#if gefilterdeContacten.length === 0}
						<div class="p-3 text-center text-sm text-muted-foreground/50">
							Geen contacten gevonden
						</div>
					{/if}
				</Card.Content>
			</Card.Root>

			<p class="text-center text-xs text-muted-foreground/30">
				{contacts.length} contacten beschikbaar
			</p>
		</div>
	{/if}
</div>
