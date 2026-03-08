import { env } from '$env/dynamic/private';

// Internal backend URL — only reachable from the SvelteKit server, never from the browser.
export const BACKEND = env.BACKEND_URL ?? 'http://localhost:8000';

// API key for authenticating server-side requests to the backend.
export const API_KEY = env.API_KEY ?? '';
