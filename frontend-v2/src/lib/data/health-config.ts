// Shared health check types and display config.

export type ServiceStatus = 'ok' | 'slow' | 'down';

export type HealthResponse = {
	status: 'ok' | 'degraded';
	services: Record<string, { status: ServiceStatus }>;
	checked_at: string;
};

export const POLL_INTERVAL = 60_000;

export const SERVICE_LABELS: Record<string, string> = {
	database: 'Database',
	stt: 'Spraak-naar-tekst',
	tts: 'Tekst-naar-spraak',
	ollama: 'LLM',
	n8n: 'Automatisering',
	whatsapp: 'WhatsApp'
};

export const STATUS_LABELS: Record<ServiceStatus, string> = {
	ok: 'Online',
	slow: 'Traag',
	down: 'Offline'
};

export const STATUS_COLORS: Record<ServiceStatus, { dot: string; text: string }> = {
	ok: { dot: 'bg-green-500', text: 'text-green-500' },
	slow: { dot: 'bg-amber-500', text: 'text-amber-500' },
	down: { dot: 'bg-red-500', text: 'text-red-500' }
};
