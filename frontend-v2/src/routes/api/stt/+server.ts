import { proxyPost } from '$lib/server/proxy';

export const POST = proxyPost('/api/stt', { body: 'form' });
