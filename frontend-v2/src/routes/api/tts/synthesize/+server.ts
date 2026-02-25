import { proxyPost } from '$lib/server/proxy';

export const POST = proxyPost('/api/tts/synthesize', { forwardXHeaders: true });
