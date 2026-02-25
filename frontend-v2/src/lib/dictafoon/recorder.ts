// MediaRecorder wrapper with crash-resilient chunk saving to IndexedDB.
// Uses 10-second timeslices so at most 10s of audio is lost on crash.
// In-memory chunks are used for the normal stop flow (no race condition).
// IndexedDB chunks are only used for crash recovery.

import { set, get, del, keys } from 'idb-keyval';
import { requestWakeLock, releaseWakeLock } from './wake-lock';

const CHUNK_PREFIX = 'rec-chunk-';
const RECORDING_META = 'rec-meta';

export const MAX_RECORDING_SECS = 5400; // 1 hour 30 minutes
export const WARN_SECS = 10; // beep countdown in last 10 seconds

let audioCtx: AudioContext | null = null;

function playBeep(): void {
	if (!audioCtx) audioCtx = new AudioContext();
	const osc = audioCtx.createOscillator();
	const gain = audioCtx.createGain();
	osc.frequency.value = 880;
	gain.gain.value = 0.3;
	osc.connect(gain);
	gain.connect(audioCtx.destination);
	osc.start();
	osc.stop(audioCtx.currentTime + 0.1);
}

type RecordingMeta = {
	mimeType: string;
	startedAt: number;
	chunkCount: number;
};

function getSupportedMimeType(): string {
	const candidates = [
		'audio/webm;codecs=opus',
		'audio/webm',
		'audio/ogg;codecs=opus',
		'audio/mp4'
	];
	return candidates.find((t) => MediaRecorder.isTypeSupported(t)) ?? '';
}

let mediaRecorder: MediaRecorder | null = null;
let chunkIndex = 0;
let memoryChunks: Blob[] = [];
let timerInterval: ReturnType<typeof setInterval> | null = null;
let elapsedSeconds = 0;
let onTickCallback: ((seconds: number) => void) | null = null;
let onStopCallback: ((blob: Blob, mimeType: string, duration: number) => void) | null = null;
let currentMimeType = '';
let isStarting = false;

export function isRecording(): boolean {
	return mediaRecorder?.state === 'recording';
}

export function getElapsed(): number {
	return elapsedSeconds;
}

export async function startRecording(
	onTick: (seconds: number) => void,
	onStop: (blob: Blob, mimeType: string, duration: number) => void
): Promise<void> {
	if (isStarting) return;
	isStarting = true;

	try {
		// Stop any previous recording and timer to prevent stacking
		if (mediaRecorder && mediaRecorder.state !== 'inactive') {
			mediaRecorder.stop();
		}
		stopTimer();

		await clearChunks();

		const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
		currentMimeType = getSupportedMimeType();
		mediaRecorder = new MediaRecorder(stream, currentMimeType ? { mimeType: currentMimeType } : undefined);
		chunkIndex = 0;
		memoryChunks = [];
		elapsedSeconds = 0;
		onTickCallback = onTick;
		onStopCallback = onStop;

		await set(RECORDING_META, {
			mimeType: currentMimeType || 'audio/webm',
			startedAt: Date.now(),
			chunkCount: 0
		} satisfies RecordingMeta);

		mediaRecorder.ondataavailable = (e) => {
			if (e.data.size > 0) {
				// In-memory for immediate use on stop
				memoryChunks.push(e.data);

				// Async IndexedDB write for crash recovery (fire-and-forget)
				const idx = chunkIndex++;
				e.data.arrayBuffer().then((buffer) => {
					set(`${CHUNK_PREFIX}${idx}`, buffer).then(() => {
						get<RecordingMeta>(RECORDING_META).then((meta) => {
							if (meta) {
								meta.chunkCount = idx + 1;
								set(RECORDING_META, meta);
							}
						});
					});
				});
			}
		};

		mediaRecorder.onstop = async () => {
			stream.getTracks().forEach((t) => t.stop());
			stopTimer();
			await releaseWakeLock();

			// Use in-memory chunks — always complete, no race condition
			const blob = new Blob(memoryChunks, { type: currentMimeType || 'audio/webm' });
			const duration = elapsedSeconds;
			const mime = currentMimeType || 'audio/webm';

			memoryChunks = [];
			await clearChunks();

			onStopCallback?.(blob, mime, duration);
		};

		await requestWakeLock();
		mediaRecorder.start(10_000);
		startTimer();
	} finally {
		isStarting = false;
	}
}

export function stopRecording(): void {
	if (mediaRecorder && mediaRecorder.state !== 'inactive') {
		mediaRecorder.stop();
	}
}

export async function hasInterruptedRecording(): Promise<boolean> {
	const meta = await get<RecordingMeta>(RECORDING_META);
	return meta !== undefined && meta.chunkCount > 0;
}

export async function recoverInterruptedRecording(): Promise<{ blob: Blob; mimeType: string; duration: number } | null> {
	const meta = await get<RecordingMeta>(RECORDING_META);
	if (!meta || meta.chunkCount === 0) return null;

	const blob = await assembleFromIndexedDB(meta.mimeType);
	const estimatedDuration = Math.round((Date.now() - meta.startedAt) / 1000);

	await clearChunks();

	return { blob, mimeType: meta.mimeType, duration: estimatedDuration };
}

export async function discardInterruptedRecording(): Promise<void> {
	await clearChunks();
}

// --- Internal helpers ---

// Only used for crash recovery — reads chunks from IndexedDB
async function assembleFromIndexedDB(mimeType: string): Promise<Blob> {
	const allKeys = (await keys()).filter((k) => typeof k === 'string' && k.startsWith(CHUNK_PREFIX));
	allKeys.sort((a, b) => {
		const idxA = parseInt(String(a).replace(CHUNK_PREFIX, ''), 10);
		const idxB = parseInt(String(b).replace(CHUNK_PREFIX, ''), 10);
		return idxA - idxB;
	});

	const buffers: ArrayBuffer[] = [];
	for (const key of allKeys) {
		const buf = await get<ArrayBuffer>(key);
		if (buf) buffers.push(buf);
	}

	return new Blob(buffers, { type: mimeType });
}

async function clearChunks(): Promise<void> {
	const allKeys = (await keys()).filter(
		(k) => typeof k === 'string' && (k.startsWith(CHUNK_PREFIX) || k === RECORDING_META)
	);
	for (const key of allKeys) {
		await del(key);
	}
}

function startTimer(): void {
	if (timerInterval) clearInterval(timerInterval);
	timerInterval = setInterval(() => {
		elapsedSeconds++;
		onTickCallback?.(elapsedSeconds);

		const remaining = MAX_RECORDING_SECS - elapsedSeconds;
		if (remaining <= 0) {
			stopRecording();
		} else if (remaining < WARN_SECS) {
			playBeep();
		}
	}, 1000);
}

function stopTimer(): void {
	if (timerInterval) {
		clearInterval(timerInterval);
		timerInterval = null;
	}
}
