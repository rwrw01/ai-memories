<script lang="ts">
	import { onMount } from 'svelte';
	import {
		startRecording,
		stopRecording,
		hasInterruptedRecording,
		recoverInterruptedRecording,
		discardInterruptedRecording,
		MAX_RECORDING_SECS,
		WARN_SECS
	} from '$lib/dictafoon/recorder';
	import {
		getDictaten,
		getIsLoaded,
		loadDictaten,
		saveDictaat,
		deleteDictaat,
		transcribeDictaat,
		classifyDictaat,
		executeDictaatFlow,
		type Dictaat
	} from '$lib/dictafoon/store.svelte';
	import FlowConfirm from '$lib/components/FlowConfirm.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import Square from '@lucide/svelte/icons/square';
	import Circle from '@lucide/svelte/icons/circle';
	import Copy from '@lucide/svelte/icons/copy';
	import Check from '@lucide/svelte/icons/check';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import Trash2 from '@lucide/svelte/icons/trash-2';

	let recording = $state(false);
	let elapsed = $state(0);
	let foutmelding = $state('');
	let hasInterrupted = $state(false);
	let copiedId = $state<string | null>(null);
	let laadFout = $state('');
	let executingId = $state<string | null>(null);

	let dictaten = $derived(getDictaten());
	let isLoaded = $derived(getIsLoaded());

	function formatTijd(seconds: number): string {
		const h = Math.floor(seconds / 3600);
		const m = Math.floor((seconds % 3600) / 60);
		const s = seconds % 60;
		const mm = String(m).padStart(2, '0');
		const ss = String(s).padStart(2, '0');
		return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
	}

	function formatDatum(ts: number): string {
		const d = new Date(ts);
		const maanden = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
		return `${d.getDate()} ${maanden[d.getMonth()]} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
	}

	function formatDuur(s: number): string {
		if (s >= 3600) return `${Math.floor(s / 3600)}u${Math.floor((s % 3600) / 60)}m`;
		if (s >= 60) return `${Math.floor(s / 60)}m`;
		return `${s}s`;
	}

	function statusLabel(d: Dictaat): string {
		switch (d.status) {
			case 'gereed': return '';
			case 'bezig': return 'Transcriberen...';
			case 'wacht': return 'Wacht op verwerking';
			case 'fout': return d.foutReden ?? 'Mislukt';
		}
	}

	async function toggleRecording() {
		foutmelding = '';
		if (recording) {
			stopRecording();
			recording = false;
			return;
		}
		try {
			await startRecording(
				(secs) => { elapsed = secs; },
				async (blob, mimeType, duration) => {
					recording = false;
					elapsed = 0;
					const dictaat = await saveDictaat(blob, mimeType, duration);
					await transcribeDictaat(dictaat);
					await classifyDictaat(dictaat);
				},
				(message) => {
					recording = false;
					elapsed = 0;
					foutmelding = message;
				}
			);
			recording = true;
			elapsed = 0;
		} catch {
			foutmelding = 'Geen toegang tot microfoon';
		}
	}

	async function handleRecover() {
		const recovered = await recoverInterruptedRecording();
		if (recovered) {
			const dictaat = await saveDictaat(recovered.blob, recovered.mimeType, recovered.duration);
			await transcribeDictaat(dictaat);
			await classifyDictaat(dictaat);
		}
		hasInterrupted = false;
	}

	async function handleDiscard() {
		await discardInterruptedRecording();
		hasInterrupted = false;
	}

	async function copyText(tekst: string, id: string) {
		await navigator.clipboard.writeText(tekst);
		copiedId = id;
		setTimeout(() => { copiedId = null; }, 1500);
	}

	async function handleExecuteFlow(d: Dictaat, _intent: string, params: Record<string, string>) {
		executingId = d.id;
		await executeDictaatFlow(d, params);
		executingId = null;
	}

	onMount(async () => {
		try {
			await loadDictaten();
			hasInterrupted = await hasInterruptedRecording();
		} catch (e) {
			console.error('Laden mislukt:', e);
			laadFout = 'Kan gegevens niet laden. Probeer de pagina te herladen.';
		}
	});
</script>

<div class="flex flex-col gap-6 px-4 pb-8">
	{#if laadFout}
		<Card.Root class="mt-3 border-destructive/50 bg-destructive/10">
			<Card.Content class="p-3 text-sm text-destructive">{laadFout}</Card.Content>
		</Card.Root>
	{/if}

	{#if hasInterrupted}
		<Card.Root class="mt-3 bg-muted/50">
			<Card.Content class="flex items-center justify-between p-3">
				<span class="text-sm text-muted-foreground">Onafgeronde opname gevonden</span>
				<div class="flex gap-3">
					<Button variant="link" size="sm" class="h-auto p-0 text-xs" onclick={handleRecover}>Herstellen</Button>
					<Button variant="link" size="sm" class="h-auto p-0 text-xs text-muted-foreground" onclick={handleDiscard}>Verwijderen</Button>
				</div>
			</Card.Content>
		</Card.Root>
	{/if}

	<!-- Recorder -->
	<section class="flex flex-col items-center gap-3.5 pb-6 pt-10">
		<span
			class="text-[3.25rem] font-extralight tracking-wide tabular-nums transition-colors duration-200
				{recording ? (elapsed >= MAX_RECORDING_SECS - WARN_SECS ? 'animate-pulse text-red-500' : 'text-foreground') : 'text-muted-foreground/20'}"
		>
			{formatTijd(elapsed)}
		</span>

		<button
			class="grid size-[72px] cursor-pointer place-items-center rounded-full border-none bg-red-600 text-white shadow-lg transition-transform active:scale-[0.93]
				{recording ? 'animate-pulse' : ''}"
			onclick={toggleRecording}
			aria-label={recording ? 'Stop opname' : 'Start opname'}
		>
			{#if recording}
				<Square class="size-6" />
			{:else}
				<Circle class="size-7 fill-current" />
			{/if}
		</button>

		<span class="text-xs font-medium tracking-wide text-muted-foreground/30">
			{#if recording}Tik om te stoppen{:else}Opnemen{/if}
		</span>

		{#if foutmelding}
			<span class="text-sm text-destructive">{foutmelding}</span>
		{/if}
	</section>

	<!-- History -->
	{#if isLoaded && dictaten.length > 0}
		<section class="flex flex-col gap-2">
			<h2 class="pl-0.5 text-[0.6875rem] font-semibold uppercase tracking-widest text-muted-foreground/30">Opnames</h2>

			<div class="flex flex-col gap-0.5">
				{#each dictaten as d (d.id)}
					<Card.Root class="bg-muted/30">
						<Card.Content class="p-3">
							<div class="flex items-baseline gap-1.5">
								<span class="text-sm font-medium text-muted-foreground">{formatDatum(d.datum)}</span>
								<span class="text-muted-foreground/15">&middot;</span>
								<span class="text-xs text-muted-foreground/25">{formatDuur(d.duur)}</span>
								{#if d.status !== 'gereed'}
									<Badge variant={d.status === 'fout' ? 'destructive' : 'secondary'} class="ml-auto text-[0.6875rem]">
										{statusLabel(d)}
									</Badge>
								{/if}
							</div>

							{#if d.transcriptie}
								<p class="mt-1 line-clamp-3 text-sm leading-relaxed text-muted-foreground/55">{d.transcriptie}</p>
							{/if}

							{#if d.classificatie}
								<FlowConfirm
									dictaat={d}
									onExecute={(intent, params) => handleExecuteFlow(d, intent, params)}
									executing={executingId === d.id}
								/>
							{/if}

							<div class="mt-2 flex gap-4">
								{#if d.transcriptie}
									<Button variant="ghost" size="sm" class="h-auto gap-1 p-0 text-xs text-muted-foreground" onclick={() => copyText(d.transcriptie!, d.id)}>
										{#if copiedId === d.id}
											<Check class="size-3" />Gekopieerd
										{:else}
											<Copy class="size-3" />Kopieer
										{/if}
									</Button>
								{/if}
								{#if d.status === 'fout'}
									<Button variant="ghost" size="sm" class="h-auto gap-1 p-0 text-xs text-muted-foreground" onclick={() => transcribeDictaat(d)}>
										<RotateCcw class="size-3" />Opnieuw
									</Button>
								{/if}
								<Button variant="ghost" size="sm" class="h-auto gap-1 p-0 text-xs text-muted-foreground/25" onclick={() => deleteDictaat(d.id)}>
									<Trash2 class="size-3" />Verwijder
								</Button>
							</div>
						</Card.Content>
					</Card.Root>
				{/each}
			</div>
		</section>
	{/if}
</div>
