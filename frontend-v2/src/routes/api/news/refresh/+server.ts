import { proxyPost } from '$lib/server/proxy';

export const POST = proxyPost('/api/news/refresh', { body: 'none' });
