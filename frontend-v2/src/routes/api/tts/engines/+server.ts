import { BACKEND } from '$lib/server/backend';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
	const resp = await fetch(`${BACKEND}/api/tts/engines`);

	return new Response(resp.body, {
		status: resp.status,
		headers: { 'content-type': 'application/json' }
	});
};
