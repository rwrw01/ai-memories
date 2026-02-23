import { env } from '$env/dynamic/private';

// Internal backend URL — only reachable from the SvelteKit server, never from the browser.
export const BACKEND = env.BACKEND_URL ?? 'http://localhost:8000';
