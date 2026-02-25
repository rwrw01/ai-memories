import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit(),
		SvelteKitPWA({
			registerType: 'autoUpdate',
			strategies: 'injectManifest',
			srcDir: 'src',
			filename: 'service-worker.ts',
			manifest: {
				name: 'Herinneringen',
				short_name: 'Herinneringen',
				description: 'Persoonlijke spraakassistent',
				theme_color: '#1a1a2e',
				background_color: '#1a1a2e',
				display: 'standalone',
				scope: '/',
				start_url: '/',
				orientation: 'portrait',
				icons: [
					{ src: '/pwa-64x64.png', sizes: '64x64', type: 'image/png' },
					{ src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
					{ src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png' },
					{ src: '/maskable-icon-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
				]
			},
			injectManifest: {
				globPatterns: ['client/**/*.{js,css,html,ico,png,svg,webp,woff2}']
			},
			devOptions: {
				enabled: true,
				type: 'module'
			}
		})
	],
	server: {
		host: true,
		port: 5174,
		strictPort: true,
		allowedHosts: ['pc-003.taild4fcd.ts.net']
	}
});
