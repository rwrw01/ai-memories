/// <reference lib="webworker" />

import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching';
import { registerRoute, NavigationRoute } from 'workbox-routing';
import { NetworkFirst } from 'workbox-strategies';
import { CacheableResponsePlugin } from 'workbox-cacheable-response';
import { ExpirationPlugin } from 'workbox-expiration';

declare let self: ServiceWorkerGlobalScope;

// --- Precaching: static assets injected at build time ---
precacheAndRoute(self.__WB_MANIFEST);
cleanupOutdatedCaches();

// --- Navigation: serve cached app shell when offline ---
const navigationHandler = new NetworkFirst({
	cacheName: 'pages-cache',
	plugins: [
		new CacheableResponsePlugin({ statuses: [0, 200] }),
		new ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 24 * 60 * 60 })
	]
});

registerRoute(new NavigationRoute(navigationHandler));

// --- Message handling ---
self.addEventListener('message', (event) => {
	if (event.data?.type === 'SKIP_WAITING') {
		self.skipWaiting();
	}
});
