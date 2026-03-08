import { BACKEND } from '$lib/server/backend';

export async function GET({ params }: { params: { id: string } }) {
	const resp = await fetch(`${BACKEND}/api/uren/${params.id}/excel`);
	return new Response(resp.body, {
		status: resp.status,
		headers: {
			'content-type':
				resp.headers.get('content-type') ?? 'application/octet-stream',
			'content-disposition': resp.headers.get('content-disposition') ?? 'attachment'
		}
	});
}
