import { BACKEND } from '$lib/server/backend';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async () => {
	const resp = await fetch(`${BACKEND}/api/news/refresh`, {
		method: 'POST'
	});

	return new Response(resp.body, {
		status: resp.status,
		headers: { 'content-type': 'application/json' }
	});
};
