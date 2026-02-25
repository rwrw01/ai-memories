import { BACKEND } from '$lib/server/backend';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
	const resp = await fetch(`${BACKEND}/api/summarize`, {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: await request.text()
	});

	return new Response(resp.body, {
		status: resp.status,
		headers: { 'content-type': 'application/json' }
	});
};
