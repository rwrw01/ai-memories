<script lang="ts">
	import { page } from '$app/stores';
	let { children } = $props();
</script>

<div class="app">
	<header class="app-header">
		<h1 class="app-title">Herinneringen</h1>
	</header>

	<main class="app-main">
		{@render children()}
	</main>

	<nav class="app-nav">
		<a href="/" class="nav-item" class:active={$page.url.pathname === '/'} aria-label="Home">
			<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
				<path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15a.998.998 0 0 0-.98-.85c-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z"/>
			</svg>
			<span>Dictafoon</span>
		</a>
		<a href="/nieuws" class="nav-item" class:active={$page.url.pathname.startsWith('/nieuws')} aria-label="Nieuws">
			<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
				<path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/>
			</svg>
			<span>Nieuws</span>
		</a>
		<a href="/instellingen" class="nav-item" class:active={$page.url.pathname === '/instellingen'} aria-label="Instellingen">
			<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
				<path d="M19.14 12.94c.04-.3.06-.61.06-.94s-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.49.49 0 0 0-.59-.22l-2.39.96a6.97 6.97 0 0 0-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.466.466 0 0 0-.59.22L2.74 8.87a.48.48 0 0 0 .12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.48.48 0 0 0-.12-.61zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
			</svg>
			<span>Instellingen</span>
		</a>
	</nav>
</div>

<style>
	:global(*) {
		box-sizing: border-box;
		margin: 0;
		padding: 0;
	}

	:global(body) {
		font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
		background-color: #111;
		color: #e5e5e5;
		min-height: 100dvh;
		overscroll-behavior: none;
		-webkit-font-smoothing: antialiased;
	}

	:global(a) {
		color: inherit;
		text-decoration: none;
	}

	.app {
		display: flex;
		flex-direction: column;
		height: 100dvh;
		max-width: 480px;
		margin: 0 auto;
	}

	.app-header {
		display: flex;
		align-items: center;
		padding: 0.75rem 1rem;
		padding-top: calc(0.75rem + env(safe-area-inset-top));
		background-color: #111;
		border-bottom: 1px solid rgba(255, 255, 255, 0.08);
		flex-shrink: 0;
	}

	.app-title {
		font-size: 1.05rem;
		font-weight: 600;
		color: #e5e5e5;
		letter-spacing: -0.01em;
	}

	.app-main {
		flex: 1;
		overflow-y: auto;
		overscroll-behavior: contain;
	}

	.app-nav {
		display: flex;
		justify-content: space-around;
		padding: 0.375rem 0;
		padding-bottom: calc(0.375rem + env(safe-area-inset-bottom));
		background-color: #111;
		border-top: 1px solid rgba(255, 255, 255, 0.08);
		flex-shrink: 0;
	}

	.nav-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.125rem;
		padding: 0.375rem 1.25rem;
		border-radius: 0.5rem;
		color: rgba(255, 255, 255, 0.4);
		font-size: 0.625rem;
		font-weight: 500;
		letter-spacing: 0.02em;
		transition: color 0.15s;
	}

	.nav-item.active {
		color: #fff;
	}
</style>
