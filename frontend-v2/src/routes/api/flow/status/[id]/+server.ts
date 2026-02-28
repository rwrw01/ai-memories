import { proxyGet } from '$lib/server/proxy';

export const GET = proxyGet('/api/flow/status/[id]');
