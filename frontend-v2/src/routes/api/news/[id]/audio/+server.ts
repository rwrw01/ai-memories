import { BACKEND } from '$lib/server/backend';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params }) => {
	const resp = await fetch(`${BACKEND}/api/news/${params.id}/audio`);

	return new Response(resp.body, {
		status: resp.status,
		headers: {
			'content-type': resp.headers.get('content-type') ?? 'audio/mpeg',
			'cache-control': 'public, max-age=86400'
		}
	});
};
