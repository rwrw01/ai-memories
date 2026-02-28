import { proxyPost } from '$lib/server/proxy';

export const POST = proxyPost('/api/whatsapp/pair', { body: 'json' });
