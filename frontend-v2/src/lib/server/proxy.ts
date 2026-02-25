import { BACKEND } from './backend';

// Shared proxy factory for SvelteKit API routes → FastAPI backend.
// Each route file becomes 1–3 lines instead of 10–25.

type Event = { request: Request; params: Record<string, string> };
type Opts = {
	headers?: Record<string, string>;
	forwardXHeaders?: boolean;
	body?: 'json' | 'form' | 'none';
};

function resolve(template: string, params: Record<string, string>): string {
	return template.replace(/\[(\w+)\]/g, (_, k) => params[k] ?? '');
}

function respond(resp: Response, opts?: Opts): Response {
	const h: Record<string, string> = {
		'content-type': resp.headers.get('content-type') ?? 'application/json'
	};
	if (opts?.headers) Object.assign(h, opts.headers);
	if (opts?.forwardXHeaders) {
		resp.headers.forEach((v, k) => {
			if (k.startsWith('x-')) h[k] = v;
		});
	}
	return new Response(resp.body, { status: resp.status, headers: h });
}

export function proxyGet(path: string, opts?: Opts) {
	return async ({ params }: Event) => {
		const resp = await fetch(`${BACKEND}${resolve(path, params)}`);
		return respond(resp, opts);
	};
}

export function proxyPost(path: string, opts?: Opts) {
	return async ({ request, params }: Event) => {
		const init: RequestInit = { method: 'POST' };
		if (opts?.body === 'form') {
			init.body = await request.formData();
		} else if (opts?.body !== 'none') {
			init.headers = { 'content-type': 'application/json' };
			init.body = await request.text();
		}
		const resp = await fetch(`${BACKEND}${resolve(path, params)}`, init);
		return respond(resp, opts);
	};
}

export function proxyPut(path: string, opts?: Opts) {
	return async ({ request, params }: Event) => {
		const resp = await fetch(`${BACKEND}${resolve(path, params)}`, {
			method: 'PUT',
			headers: { 'content-type': 'application/json' },
			body: await request.text()
		});
		return respond(resp, opts);
	};
}
