<script lang="ts">
	import { page } from '$app/stores';
	import { ModeWatcher } from 'mode-watcher';
	import { Toaster } from '$lib/components/ui/sonner';
	import StatusBanner from '$lib/components/StatusBanner.svelte';
	import Mic from '@lucide/svelte/icons/mic';
	import MessageCircle from '@lucide/svelte/icons/message-circle';
	import '../app.css';

	let { children } = $props();

	const navItems = [
		{ href: '/', label: 'Dictafoon', icon: Mic, match: (p: string) => p === '/' },
		{ href: '/whatsapp', label: 'WhatsApp', icon: MessageCircle, match: (p: string) => p === '/whatsapp' }
	];
</script>

<ModeWatcher defaultMode="dark" />
<Toaster />

<div class="mx-auto flex h-dvh max-w-lg flex-col">
	<StatusBanner />

	<header
		class="shrink-0 border-b border-white/8 px-4 py-3"
		style="padding-top: calc(0.75rem + env(safe-area-inset-top))"
	>
		<h1 class="text-[1.05rem] font-semibold tracking-tight">Herinneringen</h1>
	</header>

	<main class="flex-1 overflow-y-auto overscroll-contain">
		{@render children()}
	</main>

	<nav
		class="flex shrink-0 justify-around border-t border-white/8 py-1.5"
		style="padding-bottom: calc(0.375rem + env(safe-area-inset-bottom))"
	>
		{#each navItems as item}
			<a
				href={item.href}
				class="flex flex-col items-center gap-0.5 rounded-lg px-5 py-1.5 text-[0.625rem] font-medium tracking-wide transition-colors {item.match(
					$page.url.pathname
				)
					? 'text-foreground'
					: 'text-muted-foreground'}"
				aria-label={item.label}
			>
				<item.icon class="size-5" />
				<span>{item.label}</span>
			</a>
		{/each}
	</nav>
</div>
