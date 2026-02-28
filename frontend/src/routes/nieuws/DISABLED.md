# Nieuws — Tijdelijk Uitgeschakeld

De nieuwsfunctie is uitgeschakeld omdat de TTS-services (Parkiet/Piper) niet draaien.

## Heractiveren checklist

1. **Docker containers starten:**
   ```bash
   cd ~/services && docker compose up -d
   ```
   Dit start: TTS (Parkiet + Piper), n8n, Ollama, STT

2. **Nav-items terugzetten in layout:**
   Bestand: `src/routes/+layout.svelte`
   Vervang de comment `<!-- Nieuws en Instellingen nav-items uitgeschakeld -->` door:
   ```svelte
   <a href="/nieuws" class="nav-item" class:active={$page.url.pathname.startsWith('/nieuws')} aria-label="Nieuws">
       <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
           <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/>
       </svg>
       <span>Nieuws</span>
   </a>
   <a href="/nieuws/instellingen" class="nav-item" class:active={$page.url.pathname === '/nieuws/instellingen'} aria-label="Instellingen">
       <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
           <path d="M19.14 12.94c.04-.3.06-.61.06-.94s-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.49.49 0 0 0-.59-.22l-2.39.96a6.97 6.97 0 0 0-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.466.466 0 0 0-.59.22L2.74 8.87a.48.48 0 0 0 .12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.48.48 0 0 0-.12-.61zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
       </svg>
       <span>Instellingen</span>
   </a>
   ```

3. **Configuratie-items terugzetten in instellingen-pagina:**
   Bestand: `src/routes/nieuws/instellingen/+page.svelte`
   Herstel vanuit git: `git checkout HEAD -- src/routes/nieuws/instellingen/+page.svelte`
   (Of bekijk git log voor de vorige versie met RSS feeds, max artikelen, categorieën)

4. **Nieuws refreshen:**
   ```bash
   curl -X POST http://localhost:5678/webhook/news-refresh
   ```

5. **Verifieer:**
   ```bash
   curl http://localhost:8000/api/news/today | python3 -m json.tool | grep audio_ready
   ```
