<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { Input } from '$lib/components/ui/input';
	import { Textarea } from '$lib/components/ui/textarea';
	import Send from '@lucide/svelte/icons/send';
	import FileText from '@lucide/svelte/icons/file-text';
	import StickyNote from '@lucide/svelte/icons/sticky-note';
	import type { FlowIntent } from '$lib/types/flow';
	import type { Dictaat } from '$lib/dictafoon/store.svelte';

	type Props = {
		dictaat: Dictaat;
		onExecute: (intent: FlowIntent, params: Record<string, string>) => void;
		executing: boolean;
	};
	let { dictaat, onExecute, executing }: Props = $props();

	let classificatie = $derived(dictaat.classificatie);
	let editParams = $state<Record<string, string>>({});

	// Sync editable params when classificatie changes
	$effect(() => {
		if (classificatie) {
			editParams = { ...classificatie.params };
		}
	});

	const intentConfig: Record<FlowIntent, { label: string; icon: typeof Send; color: string }> = {
		whatsapp: { label: 'WhatsApp', icon: Send, color: 'bg-green-600/15 text-green-400 border-green-600/30' },
		artikel: { label: 'Artikel', icon: FileText, color: 'bg-blue-600/15 text-blue-400 border-blue-600/30' },
		aantekening: { label: 'Aantekening', icon: StickyNote, color: 'bg-muted text-muted-foreground border-muted' }
	};
</script>

{#if classificatie && classificatie.intent !== 'aantekening'}
	{@const config = intentConfig[classificatie.intent]}
	<Card.Root class="mt-1.5 border-primary/10 bg-primary/5">
		<Card.Content class="p-3">
			<div class="mb-2 flex items-center gap-2">
				<Badge class="{config.color} text-[0.6875rem]">
					<config.icon class="mr-1 size-3" />
					{config.label}
				</Badge>
				<span class="text-[0.625rem] text-muted-foreground/40">
					{Math.round(classificatie.confidence * 100)}%
				</span>
			</div>

			{#if classificatie.intent === 'whatsapp'}
				<div class="flex flex-col gap-1.5">
					<Input
						bind:value={editParams.contact}
						placeholder="Contact"
						class="h-8 text-sm"
					/>
					<Textarea
						bind:value={editParams.bericht}
						placeholder="Bericht"
						class="min-h-[3rem] text-sm"
						rows={2}
					/>
				</div>
			{:else if classificatie.intent === 'artikel'}
				<div class="flex flex-col gap-1.5">
					<Input
						bind:value={editParams.onderwerp}
						placeholder="Onderwerp"
						class="h-8 text-sm"
					/>
				</div>
			{/if}

			<div class="mt-2 flex items-center gap-2">
				<Button
					size="sm"
					class="h-7 gap-1 text-xs"
					disabled={executing || dictaat.flowExecutionId !== null}
					onclick={() => onExecute(classificatie!.intent, editParams)}
				>
					{#if dictaat.flowExecutionId}
						Verstuurd
					{:else if executing}
						Bezig...
					{:else}
						<config.icon class="size-3" />
						Uitvoeren
					{/if}
				</Button>
			</div>
		</Card.Content>
	</Card.Root>
{:else if classificatie && classificatie.intent === 'aantekening'}
	<div class="mt-1">
		<Badge class="{intentConfig.aantekening.color} text-[0.625rem]">
			<StickyNote class="mr-0.5 size-2.5" />
			Aantekening
		</Badge>
	</div>
{/if}
