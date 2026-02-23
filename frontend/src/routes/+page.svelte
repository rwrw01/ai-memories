<script lang="ts">
	// --- STT state ---
	let status = $state<'idle' | 'luisteren' | 'verwerken' | 'fout'>('idle');
	let transcriptie = $state('');
	let foutmelding = $state('');

	const statusTekst: Record<typeof status, string> = {
		idle: 'Tik om te spreken',
		luisteren: 'Ik luister...',
		verwerken: 'Even geduld...',
		fout: 'Er ging iets mis'
	};

	let mediaRecorder: MediaRecorder | null = null;
	let audioChunks: Blob[] = [];

	function getSupportedMimeType(): string {
		const candidates = [
			'audio/webm;codecs=opus',
			'audio/webm',
			'audio/ogg;codecs=opus',
			'audio/mp4'
		];
		return candidates.find((t) => MediaRecorder.isTypeSupported(t)) ?? '';
	}

	async function startOpname() {
		foutmelding = '';
		transcriptie = '';

		let stream: MediaStream;
		try {
			stream = await navigator.mediaDevices.getUserMedia({ audio: true });
		} catch {
			foutmelding = 'Geen toegang tot microfoon';
			status = 'fout';
			return;
		}

		const mimeType = getSupportedMimeType();
		mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
		audioChunks = [];

		mediaRecorder.ondataavailable = (e) => {
			if (e.data.size > 0) audioChunks.push(e.data);
		};

		mediaRecorder.onstop = async () => {
			stream.getTracks().forEach((t) => t.stop());
			await verstuurAudio(mimeType);
		};

		mediaRecorder.start();
		status = 'luisteren';
	}

	function stopOpname() {
		if (mediaRecorder && mediaRecorder.state !== 'inactive') {
			status = 'verwerken';
			mediaRecorder.stop();
		}
	}

	async function verstuurAudio(mimeType: string) {
		const blob = new Blob(audioChunks, { type: mimeType || 'audio/webm' });
		const form = new FormData();
		form.append('audio', blob, 'opname.webm');

		try {
			const res = await fetch(`/api/stt`, {
				method: 'POST',
				body: form
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: res.statusText }));
				throw new Error(err.detail ?? 'Onbekende fout');
			}

			const data = await res.json();
			transcriptie = data.text ?? '';
			status = 'idle';
		} catch (err) {
			foutmelding = err instanceof Error ? err.message : 'Verbindingsfout';
			status = 'fout';
		}
	}

	function handleMicKlik() {
		if (status === 'luisteren') {
			stopOpname();
		} else if (status === 'idle' || status === 'fout') {
			startOpname();
		}
	}

	// --- Chat state ---
	type ChatBericht = { rol: 'gebruiker' | 'assistent'; tekst: string };
	let chatBerichten = $state<ChatBericht[]>([]);
	let chatInvoer = $state('');
	let chatStatus = $state<'idle' | 'denken' | 'fout'>('idle');
	let chatFout = $state('');

	async function stuurBericht() {
		const tekst = chatInvoer.trim();
		if (!tekst || chatStatus === 'denken') return;

		chatBerichten = [...chatBerichten, { rol: 'gebruiker', tekst }];
		chatInvoer = '';
		chatStatus = 'denken';
		chatFout = '';

		const messages = chatBerichten.map((b) => ({
			role: b.rol === 'gebruiker' ? 'user' : 'assistant',
			content: b.tekst
		}));

		try {
			const res = await fetch(`/api/chat`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ messages })
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: res.statusText }));
				throw new Error(err.detail ?? 'Onbekende fout');
			}

			const data = await res.json();
			chatBerichten = [...chatBerichten, { rol: 'assistent', tekst: data.reply ?? '' }];
			chatStatus = 'idle';
		} catch (err) {
			chatFout = err instanceof Error ? err.message : 'Verbindingsfout';
			chatStatus = 'fout';
		}
	}

	function handleChatToets(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			stuurBericht();
		}
	}

	// --- TTS state ---
	let ttsStatus = $state<'idle' | 'laden' | 'klaar' | 'fout'>('idle');
	let ttsTekst = $state('');
	let ttsFout = $state('');
	let ttsEngine = $state<'piper' | 'parkiet' | 'auto'>('piper');
	let audioElement: HTMLAudioElement | null = null;
	let audioUrl = $state('');

	async function spreekUit() {
		if (!ttsTekst.trim()) return;
		ttsStatus = 'laden';
		ttsFout = '';

		if (audioUrl) {
			URL.revokeObjectURL(audioUrl);
			audioUrl = '';
		}

		try {
			const res = await fetch(`/api/tts/synthesize`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ text: ttsTekst, engine: ttsEngine, voice: 'default' })
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: res.statusText }));
				throw new Error(err.detail ?? 'TTS mislukt');
			}

			const blob = await res.blob();
			audioUrl = URL.createObjectURL(blob);
			ttsStatus = 'klaar';

			// Auto-play
			await audioElement?.play();
		} catch (err) {
			ttsFout = err instanceof Error ? err.message : 'Verbindingsfout';
			ttsStatus = 'fout';
		}
	}
</script>

<div class="home">
	<section class="record-section">
		<button
			class="mic-button"
			class:active={status === 'luisteren'}
			disabled={status === 'verwerken'}
			aria-label="Spreek een herinnering in"
			onclick={handleMicKlik}
		>
			<svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 24 24" fill="currentColor">
				<path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15a.998.998 0 0 0-.98-.85c-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z"/>
			</svg>
		</button>

		<p class="status-tekst" class:actief={status !== 'idle'}>
			{statusTekst[status]}
		</p>
	</section>

	{#if transcriptie}
		<section class="transcriptie-section">
			<div class="transcriptie-kaart">
				<p class="transcriptie-tekst">{transcriptie}</p>
			</div>
		</section>
	{/if}

	{#if foutmelding}
		<section class="fout-section">
			<div class="fout-kaart">
				<p>{foutmelding}</p>
			</div>
		</section>
	{/if}

	<!-- TTS test panel -->
	<section class="tts-section">
		<div class="tts-kaart">
			<h2>Tekst uitspreken</h2>

			<textarea
				class="tts-invoer"
				placeholder="Typ tekst om voor te lezen…"
				rows="3"
				bind:value={ttsTekst}
			></textarea>

			<div class="tts-controls">
				<select class="engine-keuze" bind:value={ttsEngine}>
					<option value="piper">Piper (snel)</option>
					<option value="parkiet">Parkiet (hoge kwaliteit)</option>
					<option value="auto">Automatisch</option>
				</select>

				<button
					class="spreek-knop"
					disabled={ttsStatus === 'laden' || !ttsTekst.trim()}
					onclick={spreekUit}
				>
					{ttsStatus === 'laden' ? 'Bezig…' : 'Spreek uit'}
				</button>
			</div>

			{#if audioUrl}
				<!-- svelte-ignore a11y_media_has_caption -->
				<audio bind:this={audioElement} src={audioUrl} controls class="audio-speler"></audio>
			{/if}

			{#if ttsFout}
				<p class="tts-fout">{ttsFout}</p>
			{/if}
		</div>
	</section>

	<!-- Chat panel -->
	<section class="chat-section">
		<div class="chat-kaart">
			<h2>Gesprek</h2>

			{#if chatBerichten.length > 0}
				<div class="chat-berichten">
					{#each chatBerichten as bericht}
						<div class="bericht {bericht.rol}">
							<p>{bericht.tekst}</p>
						</div>
					{/each}
					{#if chatStatus === 'denken'}
						<div class="bericht assistent denken">
							<p>Even denken…</p>
						</div>
					{/if}
				</div>
			{/if}

			<div class="chat-invoer-rij">
				<textarea
					class="chat-invoer"
					placeholder="Stel een vraag…"
					rows="2"
					bind:value={chatInvoer}
					onkeydown={handleChatToets}
					disabled={chatStatus === 'denken'}
				></textarea>
				<button
					class="stuur-knop"
					disabled={chatStatus === 'denken' || !chatInvoer.trim()}
					onclick={stuurBericht}
				>
					{chatStatus === 'denken' ? '…' : 'Stuur'}
				</button>
			</div>

			{#if chatFout}
				<p class="chat-fout">{chatFout}</p>
			{/if}
		</div>
	</section>

	<section class="info-section">
		<div class="info-kaart">
			<h2>Welkom bij Herinneringen</h2>
			<p>
				Spreek je gedachten, taken of herinneringen in en de assistent
helpt je ze te bewaren en terug te vinden.
			</p>
		</div>

		<div class="status-banner">
			<span class="status-dot online"></span>
			<span>Spraakherkenning actief via Parakeet TDT v3 (NL)</span>
		</div>
		<div class="status-banner">
			<span class="status-dot online"></span>
			<span>Tekst-naar-spraak actief via Piper + Parkiet (NL)</span>
		</div>
		<div class="status-banner">
			<span class="status-dot online"></span>
			<span>Taalmodel actief via Ollama Llama 3 8B (NL)</span>
		</div>
	</section>
</div>

<style>
	.home {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2rem;
		padding: 2rem 1.25rem;
		min-height: 100%;
	}

	.record-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1.25rem;
		margin-top: 1rem;
	}

	.mic-button {
		width: 120px;
		height: 120px;
		border-radius: 50%;
		border: none;
		background: linear-gradient(135deg, #e94560, #c23152);
		color: white;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 4px 24px rgba(233, 69, 96, 0.4);
		transition: transform 0.15s, box-shadow 0.15s;
	}

	.mic-button:hover:not(:disabled) {
		transform: scale(1.05);
		box-shadow: 0 6px 32px rgba(233, 69, 96, 0.55);
	}

	.mic-button:active:not(:disabled) {
		transform: scale(0.97);
	}

	.mic-button.active {
		animation: pulse 1.5s ease-in-out infinite;
	}

	.mic-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	@keyframes pulse {
		0%, 100% { box-shadow: 0 4px 24px rgba(233, 69, 96, 0.4); }
		50% { box-shadow: 0 4px 48px rgba(233, 69, 96, 0.8); }
	}

	.status-tekst {
		font-size: 1rem;
		color: #888;
		transition: color 0.2s;
	}

	.status-tekst.actief {
		color: #e94560;
	}

	.transcriptie-section,
	.fout-section,
	.tts-section,
	.info-section {
		width: 100%;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.transcriptie-kaart {
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 1rem;
		padding: 1.25rem;
	}

	.transcriptie-tekst {
		font-size: 1rem;
		color: #eaeaea;
		line-height: 1.6;
		margin: 0;
	}

	.fout-kaart {
		background: #2a1020;
		border: 1px solid #e94560;
		border-radius: 1rem;
		padding: 1rem 1.25rem;
		font-size: 0.875rem;
		color: #e94560;
	}

	.fout-kaart p {
		margin: 0;
	}

	/* TTS panel */
	.tts-kaart {
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 1rem;
		padding: 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.875rem;
	}

	.tts-kaart h2 {
		font-size: 1rem;
		font-weight: 600;
		color: #eaeaea;
		margin: 0;
	}

	.tts-invoer {
		width: 100%;
		background: #0f3460;
		border: 1px solid #1a4080;
		border-radius: 0.5rem;
		padding: 0.75rem;
		color: #eaeaea;
		font-size: 0.95rem;
		font-family: inherit;
		resize: vertical;
		box-sizing: border-box;
	}

	.tts-invoer:focus {
		outline: none;
		border-color: #e94560;
	}

	.tts-controls {
		display: flex;
		gap: 0.75rem;
		align-items: center;
	}

	.engine-keuze {
		flex: 1;
		background: #0f3460;
		border: 1px solid #1a4080;
		border-radius: 0.5rem;
		padding: 0.5rem 0.75rem;
		color: #eaeaea;
		font-size: 0.875rem;
		cursor: pointer;
	}

	.spreek-knop {
		background: linear-gradient(135deg, #e94560, #c23152);
		border: none;
		border-radius: 0.5rem;
		padding: 0.5rem 1.25rem;
		color: white;
		font-size: 0.9rem;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.15s;
		white-space: nowrap;
	}

	.spreek-knop:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.audio-speler {
		width: 100%;
		border-radius: 0.5rem;
	}

	.tts-fout {
		font-size: 0.875rem;
		color: #e94560;
		margin: 0;
	}

	.info-kaart {
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 1rem;
		padding: 1.25rem;
	}

	.info-kaart h2 {
		font-size: 1rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: #eaeaea;
	}

	.info-kaart p {
		font-size: 0.875rem;
		color: #aaa;
		line-height: 1.5;
	}

	.status-banner {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 0.75rem;
		padding: 0.75rem 1rem;
		font-size: 0.8rem;
		color: #888;
	}

	.status-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.status-dot.online {
		background: #22c55e;
	}

	/* Chat panel */
	.chat-section {
		width: 100%;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.chat-kaart {
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 1rem;
		padding: 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.875rem;
	}

	.chat-kaart h2 {
		font-size: 1rem;
		font-weight: 600;
		color: #eaeaea;
		margin: 0;
	}

	.chat-berichten {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		max-height: 300px;
		overflow-y: auto;
	}

	.bericht {
		border-radius: 0.75rem;
		padding: 0.625rem 0.875rem;
		max-width: 85%;
	}

	.bericht p {
		margin: 0;
		font-size: 0.9rem;
		line-height: 1.5;
		white-space: pre-wrap;
	}

	.bericht.gebruiker {
		background: #e94560;
		color: white;
		align-self: flex-end;
	}

	.bericht.assistent {
		background: #0f3460;
		color: #eaeaea;
		align-self: flex-start;
	}

	.bericht.denken p {
		color: #888;
		font-style: italic;
	}

	.chat-invoer-rij {
		display: flex;
		gap: 0.75rem;
		align-items: flex-end;
	}

	.chat-invoer {
		flex: 1;
		background: #0f3460;
		border: 1px solid #1a4080;
		border-radius: 0.5rem;
		padding: 0.625rem 0.75rem;
		color: #eaeaea;
		font-size: 0.9rem;
		font-family: inherit;
		resize: none;
		box-sizing: border-box;
	}

	.chat-invoer:focus {
		outline: none;
		border-color: #e94560;
	}

	.chat-invoer:disabled {
		opacity: 0.6;
	}

	.stuur-knop {
		background: linear-gradient(135deg, #e94560, #c23152);
		border: none;
		border-radius: 0.5rem;
		padding: 0.5rem 1.25rem;
		color: white;
		font-size: 0.9rem;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.15s;
		white-space: nowrap;
		align-self: flex-end;
	}

	.stuur-knop:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.chat-fout {
		font-size: 0.875rem;
		color: #e94560;
		margin: 0;
	}
</style>
