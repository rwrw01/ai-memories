<script lang="ts">
</script>

<div class="instellingen">
	<div class="header-rij">
		<a href="/" class="terug-link">← Terug</a>
		<h1 class="pagina-titel">Instellingen</h1>
	</div>

	<section class="sectie uitgeschakeld">
		<h2 class="sectie-titel">Nieuws</h2>
		<p class="uitleg">Nieuwsfunctie is momenteel uitgeschakeld. Start de TTS-docker containers om nieuws weer te activeren.</p>
	</section>

	<p class="versie">Herinneringen v1.0</p>
</div>

<style>
	.instellingen {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
		padding: 1.5rem 1.25rem;
	}

	.header-rij {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.terug-link {
		font-size: 0.8rem;
		color: #e94560;
	}

	.pagina-titel {
		font-size: 1.2rem;
		font-weight: 700;
		color: #eaeaea;
		margin: 0;
	}

	.sectie {
		background: #16213e;
		border: 1px solid #0f3460;
		border-radius: 1rem;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.uitgeschakeld {
		opacity: 0.5;
	}

	.sectie-titel {
		font-size: 0.9rem;
		font-weight: 600;
		color: #eaeaea;
		margin: 0;
	}

	.uitleg {
		font-size: 0.8rem;
		color: #888;
		line-height: 1.4;
	}

	.versie {
		font-size: 0.7rem;
		color: rgba(255, 255, 255, 0.2);
		text-align: center;
		margin-top: 1rem;
	}
</style>
