import { BACKEND } from '$lib/server/backend';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
	const resp = await fetch(`${BACKEND}/api/news/preferences`);

	return new Response(resp.body, {
		status: resp.status,
		headers: { 'content-type': 'application/json' }
	});
};

export const PUT: RequestHandler = async ({ request }) => {
	const resp = await fetch(`${BACKEND}/api/news/preferences`, {
		method: 'PUT',
		headers: { 'content-type': 'application/json' },
		body: await request.text()
	});

	return new Response(resp.body, {
		status: resp.status,
		headers: { 'content-type': 'application/json' }
	});
};
