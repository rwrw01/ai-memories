<script lang="ts">
	import { onMount } from 'svelte';
	import { isWakeLockSupported } from '$lib/dictafoon/wake-lock';
	import {
		startRecording,
		stopRecording,
		isRecording,
		hasInterruptedRecording,
		recoverInterruptedRecording,
		discardInterruptedRecording
	} from '$lib/dictafoon/recorder';
	import {
		getDictaten,
		getIsLoaded,
		loadDictaten,
		saveDictaat,
		deleteDictaat,
		transcribeDictaat,
		type Dictaat
	} from '$lib/dictafoon/store.svelte';

	let recording = $state(false);
	let elapsed = $state(0);
	let foutmelding = $state('');
	let hasInterrupted = $state(false);
	let copiedId = $state<string | null>(null);
	let laadFout = $state('');

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

<div class="page">
	{#if laadFout}
		<div class="banner error-banner">
			<span>{laadFout}</span>
		</div>
	{/if}

	{#if hasInterrupted}
		<div class="banner">
			<span>Onafgeronde opname gevonden</span>
			<div class="banner-actions">
				<button class="link" onclick={handleRecover}>Herstellen</button>
				<button class="link dim" onclick={handleDiscard}>Verwijderen</button>
			</div>
		</div>
	{/if}

	<section class="recorder">
		<span class="timer" class:active={recording}>{formatTijd(elapsed)}</span>

		<button
			class="rec-btn"
			class:recording
			onclick={toggleRecording}
			aria-label={recording ? 'Stop opname' : 'Start opname'}
		>
			{#if recording}
				<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
			{:else}
				<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="8"/></svg>
			{/if}
		</button>

		<span class="label">
			{#if recording}Tik om te stoppen{:else}Opnemen{/if}
		</span>

		{#if foutmelding}
			<span class="error">{foutmelding}</span>
		{/if}
	</section>

	{#if isLoaded && dictaten.length > 0}
		<section class="history">
			<h2 class="section-label">Opnames</h2>

			<ul class="list">
				{#each dictaten as d (d.id)}
					<li class="item">
						<div class="item-meta">
							<span class="meta-date">{formatDatum(d.datum)}</span>
							<span class="meta-sep">&middot;</span>
							<span class="meta-dur">{formatDuur(d.duur)}</span>
							{#if d.status !== 'gereed'}
								<span class="meta-status" class:fout={d.status === 'fout'}>{statusLabel(d)}</span>
							{/if}
						</div>

						{#if d.transcriptie}
							<p class="item-text">{d.transcriptie}</p>
						{/if}

						<div class="item-actions">
							{#if d.transcriptie}
								<button class="link" onclick={() => copyText(d.transcriptie!, d.id)}>
									{copiedId === d.id ? 'Gekopieerd' : 'Kopieer'}
								</button>
							{/if}
							{#if d.status === 'fout'}
								<button class="link" onclick={() => transcribeDictaat(d)}>Opnieuw</button>
							{/if}
							<button class="link dim" onclick={() => deleteDictaat(d.id)}>Verwijder</button>
						</div>
					</li>
				{/each}
			</ul>
		</section>
	{/if}
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		padding: 0 1rem 2rem;
	}

	/* Recovery banner */
	.banner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.625rem 0.875rem;
		margin-top: 0.75rem;
		background: rgba(255, 255, 255, 0.04);
		border-radius: 10px;
		font-size: 0.8125rem;
		color: rgba(255, 255, 255, 0.7);
	}
	.error-banner {
		color: #d63031;
	}
	.banner-actions {
		display: flex;
		gap: 0.75rem;
	}

	/* Recorder */
	.recorder {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.875rem;
		padding: 2.5rem 0 1.5rem;
	}

	.timer {
		font-size: 3.25rem;
		font-weight: 200;
		font-variant-numeric: tabular-nums;
		color: rgba(255, 255, 255, 0.2);
		transition: color 0.2s;
		letter-spacing: 0.02em;
	}
	.timer.active {
		color: #fff;
	}

	.rec-btn {
		width: 72px;
		height: 72px;
		border-radius: 50%;
		border: none;
		background: #d63031;
		color: #fff;
		cursor: pointer;
		display: grid;
		place-items: center;
		transition: transform 0.1s, opacity 0.15s;
	}
	.rec-btn:active {
		transform: scale(0.93);
	}
	.rec-btn.recording {
		animation: pulse 2s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.6; }
	}

	.label {
		font-size: 0.75rem;
		font-weight: 500;
		color: rgba(255, 255, 255, 0.3);
		letter-spacing: 0.02em;
	}

	.error {
		font-size: 0.8125rem;
		color: #d63031;
	}

	/* History */
	.history {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.section-label {
		font-size: 0.6875rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.3);
		text-transform: uppercase;
		letter-spacing: 0.06em;
		padding-left: 0.125rem;
	}

	.list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.item {
		background: rgba(255, 255, 255, 0.04);
		border-radius: 10px;
		padding: 0.75rem 0.875rem;
	}

	.item-meta {
		display: flex;
		align-items: baseline;
		gap: 0.375rem;
		margin-bottom: 0.25rem;
	}

	.meta-date {
		font-size: 0.8125rem;
		font-weight: 500;
		color: rgba(255, 255, 255, 0.6);
	}

	.meta-sep {
		color: rgba(255, 255, 255, 0.15);
	}

	.meta-dur {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.25);
	}

	.meta-status {
		font-size: 0.6875rem;
		color: rgba(255, 255, 255, 0.3);
		margin-left: auto;
	}
	.meta-status.fout {
		color: #d63031;
	}

	.item-text {
		font-size: 0.875rem;
		line-height: 1.5;
		color: rgba(255, 255, 255, 0.55);
		margin-bottom: 0.5rem;
		display: -webkit-box;
		-webkit-line-clamp: 3;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.item-actions {
		display: flex;
		gap: 1rem;
	}

	/* Shared link-style buttons */
	.link {
		background: none;
		border: none;
		font-family: inherit;
		font-size: 0.75rem;
		font-weight: 500;
		color: rgba(255, 255, 255, 0.6);
		cursor: pointer;
		padding: 0;
		transition: color 0.1s;
	}
	.link:active {
		color: #fff;
	}
	.link.dim {
		color: rgba(255, 255, 255, 0.25);
	}
</style>
