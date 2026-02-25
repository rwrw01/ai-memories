// Dictafoon state store — manages dictations in IndexedDB (max 5).
// Uses Svelte 5 runes for reactive state.

import { get, set, del, keys } from 'idb-keyval';

const DICTAAT_PREFIX = 'dictaat-';
const MAX_DICTATEN = 5;

export type Dictaat = {
	id: string;
	datum: number;
	duur: number;
	audioBlob: ArrayBuffer | null;
	mimeType: string;
	transcriptie: string | null;
	status: 'gereed' | 'bezig' | 'wacht' | 'fout';
	foutReden: string | null;
};

// Reactive state
let dictaten = $state<Dictaat[]>([]);
let isLoaded = $state(false);

export function getDictaten(): Dictaat[] {
	return dictaten;
}

export function getIsLoaded(): boolean {
	return isLoaded;
}

export async function loadDictaten(): Promise<void> {
	const allKeys = (await keys()).filter((k) => typeof k === 'string' && k.startsWith(DICTAAT_PREFIX));

	const items: Dictaat[] = [];
	for (const key of allKeys) {
		const item = await get<Dictaat>(key);
		if (item) items.push(item);
	}

	// Sort newest first
	items.sort((a, b) => b.datum - a.datum);
	dictaten = items;
	isLoaded = true;
}

export async function saveDictaat(
	blob: Blob,
	mimeType: string,
	duur: number
): Promise<Dictaat> {
	const id = crypto.randomUUID();
	const dictaat: Dictaat = {
		id,
		datum: Date.now(),
		duur,
		audioBlob: await blob.arrayBuffer(),
		mimeType,
		transcriptie: null,
		status: 'wacht',
		foutReden: null
	};

	await set(`${DICTAAT_PREFIX}${id}`, dictaat);

	// Enforce max 5 — remove oldest
	dictaten = [dictaat, ...dictaten];
	if (dictaten.length > MAX_DICTATEN) {
		const toRemove = dictaten.splice(MAX_DICTATEN);
		for (const old of toRemove) {
			await del(`${DICTAAT_PREFIX}${old.id}`);
		}
	}

	return dictaat;
}

export async function updateDictaat(id: string, updates: Partial<Dictaat>): Promise<void> {
	const key = `${DICTAAT_PREFIX}${id}`;
	const existing = await get<Dictaat>(key);
	if (!existing) return;

	const updated = { ...existing, ...updates };
	await set(key, updated);

	// Update reactive state
	dictaten = dictaten.map((d) => (d.id === id ? updated : d));
}

export async function deleteDictaat(id: string): Promise<void> {
	await del(`${DICTAAT_PREFIX}${id}`);
	dictaten = dictaten.filter((d) => d.id !== id);
}

export async function transcribeDictaat(dictaat: Dictaat): Promise<void> {
	if (!dictaat.audioBlob) return;

	await updateDictaat(dictaat.id, { status: 'bezig' });

	const blob = new Blob([dictaat.audioBlob], { type: dictaat.mimeType });
	const form = new FormData();
	const ext = dictaat.mimeType.includes('mp4') ? 'mp4' : 'webm';
	form.append('audio', blob, `dictaat.${ext}`);

	try {
		const res = await fetch('/api/stt', { method: 'POST', body: form });

		if (!res.ok) {
			const err = await res.json().catch(() => ({ detail: res.statusText }));
			throw new Error(err.detail ?? 'Transcriptie mislukt');
		}

		const data = await res.json();
		await updateDictaat(dictaat.id, {
			transcriptie: data.text ?? '',
			status: 'gereed'
		});
	} catch (e) {
		const message = e instanceof Error ? e.message : 'Onbekende fout';
		console.error('Transcriptie mislukt:', message);
		await updateDictaat(dictaat.id, { status: 'fout', foutReden: message });
	}
}
