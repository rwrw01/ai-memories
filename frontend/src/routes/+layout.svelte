<script lang="ts">
	let { children } = $props();
</script>

<div class="app">
	<header class="app-header">
		<span class="app-logo">🎙️</span>
		<h1 class="app-title">Herinneringen</h1>
	</header>

	<main class="app-main">
		{@render children()}
	</main>

	<nav class="app-nav">
		<a href="/" class="nav-item active" aria-label="Home">
			<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
				<path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
			</svg>
			<span>Home</span>
		</a>
		<a href="/instellingen" class="nav-item" aria-label="Instellingen">
			<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
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
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		background-color: #1a1a2e;
		color: #eaeaea;
		min-height: 100dvh;
		overscroll-behavior: none;
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
		gap: 0.5rem;
		padding: 1rem 1.25rem;
		padding-top: calc(1rem + env(safe-area-inset-top));
		background-color: #16213e;
		border-bottom: 1px solid #0f3460;
		flex-shrink: 0;
	}

	.app-logo {
		font-size: 1.4rem;
	}

	.app-title {
		font-size: 1.2rem;
		font-weight: 600;
		color: #e94560;
		letter-spacing: 0.02em;
	}

	.app-main {
		flex: 1;
		overflow-y: auto;
		overscroll-behavior: contain;
	}

	.app-nav {
		display: flex;
		justify-content: space-around;
		padding: 0.5rem;
		padding-bottom: calc(0.5rem + env(safe-area-inset-bottom));
		background-color: #16213e;
		border-top: 1px solid #0f3460;
		flex-shrink: 0;
	}

	.nav-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.2rem;
		padding: 0.4rem 1.5rem;
		border-radius: 0.5rem;
		color: #888;
		font-size: 0.7rem;
		transition: color 0.2s;
	}

	.nav-item.active,
	.nav-item:hover {
		color: #e94560;
	}
</style>
