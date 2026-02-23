import { BACKEND } from '$lib/server/backend';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
	const resp = await fetch(`${BACKEND}/api/tts/synthesize`, {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: await request.text()
	});

	const headers: Record<string, string> = {
		'content-type': resp.headers.get('content-type') ?? 'audio/wav'
	};
	// Forward x-* headers from the TTS service (engine-used, duration, etc.)
	resp.headers.forEach((v, k) => {
		if (k.startsWith('x-')) headers[k] = v;
	});

	return new Response(resp.body, { status: resp.status, headers });
};
