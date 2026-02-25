import { proxyGet, proxyPut } from '$lib/server/proxy';

export const GET = proxyGet('/api/news/preferences');
export const PUT = proxyPut('/api/news/preferences');
