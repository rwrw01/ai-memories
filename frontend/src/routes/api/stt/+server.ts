import { BACKEND } from '$lib/server/backend';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
	const resp = await fetch(`${BACKEND}/api/stt`, {
		method: 'POST',
		body: await request.formData()
	});

	return new Response(resp.body, {
		status: resp.status,
		headers: { 'content-type': resp.headers.get('content-type') ?? 'application/json' }
	});
};
