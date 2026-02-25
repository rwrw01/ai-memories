import { proxyGet } from '$lib/server/proxy';

export const GET = proxyGet('/api/news/[id]/audio', {
	headers: { 'cache-control': 'public, max-age=86400' }
});
